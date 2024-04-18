from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from datetime import datetime
from users.models.user import User
from django.core.exceptions import ObjectDoesNotExist
from django_rest_passwordreset.signals import reset_password_token_created
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def blacklist_tokens_for_user(user):
    """
    Blacklist outstanding tokens for the given user.
    """
    outstanding_tokens = OutstandingToken.objects.filter(user=user, expires_at__gt=timezone.now())
    for token in outstanding_tokens:
        # Skip if token is already blacklisted
        if hasattr(token, 'blacklistedtoken'):
            continue
        BlacklistedToken.objects.create(token=token)

@receiver(pre_save, sender=User)
def revoke_tokens_on_password_change_reset(sender, instance, *args, **kwargs):
    """
    Blacklist outstanding tokens on password change.
    """
    # Skip if user is being created for the first time
    if not instance._state.adding:
        try:
            existing_user = User.objects.get(pk=instance.pk)
        except ObjectDoesNotExist:
            return

        if instance.password != existing_user.password:
            blacklist_tokens_for_user(instance)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    """

    email_message = f"""
    Hello {reset_password_token.user.first_name},
    You requested a password reset for your account.
    Please click on the link below to reset your password:
    http://127.0.0.1:8000{reverse('users:reset:reset-password-request')}?token={reset_password_token.key}"""

    send_mail(
        "Account Password Reset - VotingSystem",
        email_message,
        settings.EMAIL_HOST_USER,
        [reset_password_token.user.email],
    )

@receiver(pre_delete, sender=User)
def revoke_tokens_on_user_delete(sender, instance, *args, **kwargs):
    """
    Blacklist outstanding tokens on user deletion.
    """
    blacklist_tokens_for_user(instance)
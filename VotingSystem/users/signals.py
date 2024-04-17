from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import OutstandingToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from datetime import datetime
from users.models.user import User
from django.core.exceptions import ObjectDoesNotExist

@receiver(pre_save, sender=User)
def revoke_tokens_on_password_change(sender, instance, *args, **kwargs):
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
            outstanding_tokens = OutstandingToken.objects.filter(user=instance, expires_at__gt=datetime.now())
            for token in outstanding_tokens:
                # Skip if token is already blacklisted
                if hasattr(token, 'blacklistedtoken'):
                    continue
                BlacklistedToken.objects.create(token=token)
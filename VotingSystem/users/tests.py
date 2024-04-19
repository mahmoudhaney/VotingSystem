from rest_framework.test import APITestCase 
from django.urls import reverse
from rest_framework import status
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
from django.core import mail
import re

def create_basic_user():
    return User.objects.create_user(username='testuser', 
                                    email='test@example.com', 
                                    password='testpassword', 
                                    id_proof_number='30203020302032', 
                                    phone_number='01234567890'
                                    )

def authenticate_user(user):
    token = RefreshToken.for_user(user)
    access_token = str(token.access_token)
    refresh_token = str(token)
    return refresh_token, access_token

def make_token_expired(token):
    # Set the token expiration time to a past time
    expired_token = RefreshToken(token)
    expired_token.set_exp(from_time=datetime.datetime(1970, 1, 1))
    expired_refresh_token = str(expired_token)
    return expired_refresh_token

def blacklist_token(instance, token):
    url = reverse('users:token_blacklist')
    data = {'refresh': token}
    response = instance.client.post(url, data)
    return response

def get_reset_token_from_email(email_body):
        """
        Helper method to retrieve the reset token from the email.
        """
        match = re.search(r'token=([a-zA-Z0-9]+)', email_body)
        if match:
            return match.group(1)

class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.login_data = {'username': 'testuser', 'password': 'testpassword'}

    def test_login_with_valid_credentials(self):
        url = reverse('users:login')
        data = self.login_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_login_with_invalid_credentials(self):
        url = reverse('users:login')
        data = {'username': 'wronguser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_missing_fields(self):
        url = reverse('users:login')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        url = reverse('users:login')
        data = self.login_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_deleted_user(self):
        self.user.delete()

        url = reverse('users:login')
        data = self.login_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TokenRefreshTestCase(APITestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)

    def test_refresh_token(self):
        url = reverse('users:token_refresh')
        data = {'refresh': self.refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        new_access_token = response.data['access']
        self.assertNotEqual(new_access_token, self.access_token)

    def test_invalid_refresh_token(self):
        url = reverse('users:token_refresh')
        data = {'refresh': 'invalid_refresh_token'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_expired_refresh_token(self):
        expired_refresh_token = make_token_expired(self.refresh_token)

        url = reverse('users:token_refresh')
        data = {'refresh': expired_refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

    def test_refresh_token_with_blacklisted_token(self):
        response = blacklist_token(self, self.refresh_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt to refresh the token
        url = reverse('users:token_refresh')
        data = {'refresh': self.refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_with_missing_fields(self):
        url = reverse('users:token_refresh')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LogoutTestCase(APITestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)

    def test_logout_with_valid_token(self):
        response = blacklist_token(self, self.refresh_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_with_invalid_token(self):
        url = reverse('users:token_blacklist')
        data = {'refresh': str("invalid_token")}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_expired_token(self):
        expired_refresh_token = make_token_expired(self.refresh_token)

        url = reverse('users:token_blacklist')
        data = {'refresh': expired_refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_blacklisted_token(self):
        response = blacklist_token(self, self.refresh_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt to logout with the same token
        response = blacklist_token(self, self.refresh_token)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_missing_fields(self):
        url = reverse('users:token_blacklist')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SignUpTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:signup')
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'testpassword',
            'password2': 'testpassword',
            'phone_number': '01234567890',
            'address': '123 Main St',
            'id_proof_number': '12345678901234'
        }

    def test_successful_signup(self):
        url = self.url
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_missing_required_fields(self):
        url = self.url
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_existing_username(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='existingpassword')

        url = self.url
        self.user_data['username'] = 'existinguser'
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_password_mismatch(self):
        url = self.url
        self.user_data['password2'] = 'differentpassword'
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_existing_email_or_phone(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='existingpassword', phone_number='01234567890')

        url = self.url
        self.user_data['email'] = 'existing@example.com'
        self.user_data['phone_number'] = '01234567890'
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)

    def test_invalid_phone_number_format(self):
        url = self.url
        self.user_data['phone_number'] = '012345'
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_invalid_id_proof_number_format(self):
        url = self.url
        self.user_data['id_proof_number'] = 'abc123'
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id_proof_number', response.data)

    def test_non_unique_id_proof_number(self):
        User.objects.create_user(username='existinguser', id_proof_number='12345678901234', password='existingpassword')

        url = self.url
        self.user_data['id_proof_number'] = '12345678901234'
        data = self.user_data
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('id_proof_number', response.data)

class PasswordChangeTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:password_change')
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)
        self.data = {
            'old_password': 'testpassword',
            'new_password': 'newtestpassword',
            'new_password2': 'newtestpassword'
        }
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_password_change_with_valid_data(self):
        response = self.client.put(self.url, self.data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_change_with_wrong_old_password(self):
        self.data['old_password'] = 'wrongpassword'
        response = self.client.put(self.url, self.data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_password_change_with_mismatched_new_passwords(self):
        self.data['new_password2'] = 'mismatchedpassword'
        response = self.client.put(self.url, self.data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password2', response.data)

    def test_password_change_with_wrong_authentication(self):
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer wrong_token_here'}
        response = self.client.put(self.url, self.data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_without_authentication(self):
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_with_missing_fields(self):
        response = self.client.put(self.url, {}, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
        self.assertIn('new_password', response.data)
        self.assertIn('new_password2', response.data)

    def test_password_change_with_invalid_data(self):
        self.data['old_password'] = ''
        self.data['new_password'] = 'new'
        self.data['new_password2'] = 'new'
        response = self.client.put(self.url, self.data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
        self.assertIn('new_password', response.data)

class PasswordResetTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:reset:reset-password-request')
        self.url_confirm = reverse('users:reset:reset-password-confirm')
        self.user = create_basic_user()
        self.data_confirm = {
            'password': 'newtestpassword',
            'token': 'test_token_here'
        }

    def test_password_reset_request_with_valid_email(self):
        data = {'email': self.user.email}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Account Password Reset', mail.outbox[0].subject)
        self.assertIn('Hello', mail.outbox[0].body)
    
    def test_password_reset_request_with_invalid_email(self):
        data = {'email': 'invalid_email'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_password_reset_request_with_missing_email(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_password_reset_request_without_existing_email(self):
        data = {'email': 'not_existed@example.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_password_reset_confirm_with_valid_token(self):
        # Send password reset request
        data = {'email': self.user.email}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        # Confirm password reset
        self.data_confirm['token'] = get_reset_token_from_email(mail.outbox[0].body)
        response = self.client.post(self.url_confirm, self.data_confirm, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)

    def test_password_reset_with_invalid_token(self):
        self.data_confirm['token'] = 'invalid'
        response = self.client.post(self.url_confirm, self.data_confirm, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    def test_password_reset_with_invalid_password(self):
        # Send password reset request
        data = {'email': self.user.email}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

        # Confirm password reset
        self.data_confirm['token'] = get_reset_token_from_email(mail.outbox[0].body)
        self.data_confirm['password'] = 'new'
        response = self.client.post(self.url_confirm, self.data_confirm, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_password_reset_with_missing_fields(self):
        response = self.client.post(self.url_confirm, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertIn('token', response.data)

class UserProfileRetrieveTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:user_profile')
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_profile_retrieve(self):
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['address'], self.user.address)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)

    def test_profile_retrieve_with_wrong_authentication(self):
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer wrong_token_here'}
        response = self.client.put(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_retrieve_without_authentication(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserProfileDestroyTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:user_profile')
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_profile_destroy(self):
        response = self.client.delete(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_profile_destroy_with_wrong_authentication(self):
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer wrong_token_here'}
        response = self.client.delete(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_destroy_without_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserProfileUpdateTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('users:user_profile')
        self.user = create_basic_user()
        self.refresh_token, self.access_token = authenticate_user(self.user)
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        self.data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'updated@example.com',
            'address': '123 Main St',
            'phone_number': '01234567890',
        }

    def test_update_profile_valid_data(self):        
        response = self.client.put(self.url, self.data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.address, '123 Main St')
        self.assertEqual(self.user.phone_number, '01234567890')

    def test_update_profile_partial_data(self):
        data = {
            'first_name': 'Jane',
            'phone_number': '01234567890',
        }
        response = self.client.put(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.last_name, '')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.address, None)
        self.assertEqual(self.user.phone_number, '01234567890')

    def test_update_profile_with_existing_email(self):
        User.objects.create_user(username='existinguser', email='existinguser@example.com', password='testpassword')

        data = {'email': 'existinguser@example.com'}
        response = self.client.put(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_update_profile_with_existing_phone_number(self):
        User.objects.create_user(username='existinguser', email='existinguser@example.com', password='testpassword', phone_number='01500500500')

        data = {'phone_number': '01500500500'}
        response = self.client.put(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_update_profile_invalid_data(self):
        data = {
            'first_name': ';dsf1',
            'email': 'invalid_email',
            'phone_number': '123',
        }
        response = self.client.put(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)

    def test_update_profile_wrong_authentication(self):
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer wrong_token_here'}
        response = self.client.delete(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_without_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from .forms import SignUpForm

User = get_user_model()


class SignUpFormWhiteboxTests(TestCase):
    def test_valid_password_passes(self):
        data = {
            'username': 'user1',
            'email': 'user1@example.com',
            'password1': 'Password1!',
            'password2': 'Password1!',
            'role': 'family',
        }
        form = SignUpForm(data)
        self.assertTrue(form.is_valid(), msg=f"Form unexpectedly invalid: {form.errors}")

    def test_password_requires_upper_and_lower(self):
        data = {
            'username': 'user2',
            'email': 'user2@example.com',
            'password1': 'password1!', 
            'password2': 'password1!',
            'role': 'family',
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('uppercase and lowercase', ''.join(form.errors.get('password1', [])))

    def test_password_requires_number(self):
        data = {
            'username': 'user3',
            'email': 'user3@example.com',
            'password1': 'Password!',  
            'password2': 'Password!',
            'role': 'family',
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('at least one number', ''.join(form.errors.get('password1', [])))

    def test_password_requires_special_character(self):
        data = {
            'username': 'user4',
            'email': 'user4@example.com',
            'password1': 'Password1',  
            'password2': 'Password1',
            'role': 'family',
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('special character', ''.join(form.errors.get('password1', [])))

    def test_password_mismatch(self):
        data = {
            'username': 'user5',
            'email': 'user5@example.com',
            'password1': 'Password1!',
            'password2': 'Different1!',
            'role': 'family',
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        errors_combined = ' '.join(
            form.errors.get('password2', []) + form.errors.get('__all__', []) + form.errors.get('password1', [])
        )
        self.assertTrue('password' in errors_combined.lower())


class SignUpViewBlackboxTests(TestCase):

    def setUp(self):
        # these reverse names must match your urls.py
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')

    def _create_user_side_effect(self, username, email, password, role):
        return User.objects.create_user(username=username, email=email, password=password)

    @patch('core.views.UserFactory.create_user')
    def test_family_signup_creates_user_and_redirects_to_login(self, mock_create_user):
        mock_create_user.side_effect = self._create_user_side_effect

        response = self.client.post(self.signup_url, {
            'username': 'familyuser',
            'email': 'fam@example.com',
            'password1': 'Password1!',
            'password2': 'Password1!',
            'role': 'family',
        })

    
        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)

        self.assertTrue(User.objects.filter(username='familyuser').exists())
        self.assertTrue(mock_create_user.called)

    @patch('core.views.UserFactory.create_user')
    def test_admin_signup_with_invalid_code_deletes_user_and_redirects_back(self, mock_create_user):
        mock_create_user.side_effect = self._create_user_side_effect

        response = self.client.post(self.signup_url, {
            'username': 'adminbad',
            'email': 'adminbad@example.com',
            'password1': 'Password1!',
            'password2': 'Password1!',
            'role': 'admin',
            'admin_code': '0000',  
        })

    
        self.assertRedirects(response, self.signup_url, fetch_redirect_response=False)

        self.assertFalse(User.objects.filter(username='adminbad').exists())

    @patch('core.views.UserFactory.create_user')
    def test_admin_signup_with_valid_code_creates_user_and_redirects_to_login(self, mock_create_user):
        mock_create_user.side_effect = self._create_user_side_effect

        response = self.client.post(self.signup_url, {
            'username': 'admingood',
            'email': 'admingood@example.com',
            'password1': 'Password1!',
            'password2': 'Password1!',
            'role': 'admin',
            'admin_code': '1357', 
        })

        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username='admingood').exists())
        self.assertTrue(mock_create_user.called)

    @patch('core.views.UserFactory.create_user')
    def test_signup_shows_errors_and_does_not_create_user_when_form_invalid(self, mock_create_user):
        response = self.client.post(self.signup_url, {
            'username': 'baduser',
            'email': 'bad@example.com',
            'password1': 'password',
            'password2': 'password',
            'role': 'family',
        }, follow=True) 

      
        self.assertFalse(User.objects.filter(username='baduser').exists())

     
        mock_create_user.assert_not_called()

        self.assertEqual(response.status_code, 200)
    
        self.assertIn('Password must contain', response.content.decode('utf-8'))

from django.test import TestCase


class AccountsTest(TestCase):
    def test_signup_page(self):
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)

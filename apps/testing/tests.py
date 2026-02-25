from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.workspaces.models import Workspace, WorkspaceMembership, WorkspaceRole

User = get_user_model()


class HealthCheckTest(TestCase):
    def test_health_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('ok', response.json()['status'])


class AuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testci', email='ci@test.com', password='CIpass123!'
        )

    def test_login_redirect(self):
        response = self.client.post('/auth/login/', {
            'login': 'ci@test.com', 'password': 'CIpass123!'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_dashboard_requires_login(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response['Location'])


class WorkspaceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='wstest', email='ws@test.com', password='WSpass123!'
        )

    def test_workspace_created_on_signup(self):
        self.assertTrue(self.user.workspaces.exists())

    def test_user_is_owner(self):
        ws = self.user.workspaces.first()
        self.assertEqual(ws.get_member_role(self.user), WorkspaceRole.OWNER)


class TestingModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='mdtest', email='md@test.com', password='MDpass123!'
        )
        self.workspace = self.user.workspaces.first()

    def test_create_test_project(self):
        from apps.testing.models import TestProject
        project = TestProject.objects.create(
            workspace=self.workspace, created_by=self.user,
            name='CI Test Project', base_url='https://example.com'
        )
        self.assertEqual(str(project.name), 'CI Test Project')

    def test_mock_ai_generation(self):
        from apps.testing.ai_service import generate_test_cases
        result = generate_test_cases('https://example.com', 'ui', '')
        self.assertIn('test_cases', result)
        self.assertGreater(len(result['test_cases']), 0)

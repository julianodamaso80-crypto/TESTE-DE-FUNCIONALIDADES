import random

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria dados de demonstração'

    def handle(self, *args, **kwargs):
        from datetime import timedelta

        from django.utils import timezone

        from apps.accounts.models import User
        from apps.testing.models import TestCase, TestProject, TestRun
        from apps.workspaces.models import Workspace, WorkspaceMembership

        email = 'demo@spritetest.io'
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING('Demo user já existe. Pulando.'))
            return

        # create_user triggers signal that auto-creates workspace + membership
        user = User.objects.create_user(
            username=email, email=email, password='demo1234',
            first_name='Demo', last_name='User', onboarding_completed=True
        )
        # Get the auto-created workspace and upgrade to pro
        ws = Workspace.objects.filter(
            memberships__user=user, memberships__role='owner'
        ).first()
        ws.name = 'Demo Workspace'
        ws.plan = 'pro'
        ws.save()

        projects = [
            ('E-commerce Frontend', 'https://example.com', 'ui'),
            ('API Gateway', 'https://api.example.com', 'api'),
            ('Checkout Flow', 'https://checkout.example.com', 'both'),
        ]

        case_names = [
            'Page loads successfully', 'Navigation links work', 'Login form submits',
            'Error messages display', 'Mobile responsive layout', 'Form validation works',
            'API returns 200', 'Authentication required', 'Data persists correctly',
            'Performance within limits',
        ]

        total_runs = 0
        for proj_name, url, test_type in projects:
            project = TestProject.objects.create(
                workspace=ws, name=proj_name, base_url=url,
                test_type=test_type, is_active=True, created_by=user
            )
            for i in range(8):
                total = random.randint(5, 10)
                passed = random.randint(int(total * 0.6), total)
                failed = total - passed
                status = 'passed' if failed == 0 else 'failed'
                run_date = timezone.now() - timedelta(days=30 - i * 4)
                run = TestRun.objects.create(
                    project=project, triggered_by=user, status=status,
                    total_cases=total, passed_cases=passed, failed_cases=failed,
                    completed_at=run_date + timedelta(minutes=1),
                )
                TestRun.objects.filter(pk=run.pk).update(created_at=run_date)
                for j in range(total):
                    case_status = 'passed' if j < passed else 'failed'
                    TestCase.objects.create(
                        run=run, title=random.choice(case_names),
                        status=case_status,
                        description='Auto-gerado por seed_demo',
                    )
                total_runs += 1

        self.stdout.write(self.style.SUCCESS(
            f'Demo criado! Login: {email} / Senha: demo1234\n'
            f'3 projetos, {total_runs} runs, dados históricos dos últimos 30 dias.'
        ))

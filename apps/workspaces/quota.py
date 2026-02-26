from django.utils import timezone


def get_workspace_usage(workspace):
    from apps.testing.models import TestRun, TestProject

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    runs_this_month = TestRun.objects.filter(
        project__workspace=workspace,
        created_at__gte=month_start,
    ).count()
    total_projects = TestProject.objects.filter(
        workspace=workspace, is_active=True,
    ).count()
    total_members = workspace.memberships.count()
    return {
        'runs_this_month': runs_this_month,
        'total_projects': total_projects,
        'total_members': total_members,
    }


def check_quota(workspace, resource: str) -> dict:
    limits = workspace.get_plan_limits()
    usage = get_workspace_usage(workspace)
    checks = {
        'runs': {
            'used': usage['runs_this_month'],
            'limit': limits['runs'],
            'exceeded': usage['runs_this_month'] >= limits['runs'],
            'label': 'test runs este mês',
        },
        'projects': {
            'used': usage['total_projects'],
            'limit': limits['projects'],
            'exceeded': usage['total_projects'] >= limits['projects'],
            'label': 'projetos ativos',
        },
        'members': {
            'used': usage['total_members'],
            'limit': limits['members'],
            'exceeded': usage['total_members'] >= limits['members'],
            'label': 'membros no workspace',
        },
    }
    return checks.get(resource, {'exceeded': False})

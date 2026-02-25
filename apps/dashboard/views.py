from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    workspace = request.workspace
    stats = {
        'total_runs': 0,
        'pass_rate': '\u2014',
        'total_projects': 0,
    }
    recent_runs = []

    if workspace:
        from apps.testing.models import TestProject, TestRun

        projects = TestProject.objects.filter(workspace=workspace, is_active=True)
        runs = TestRun.objects.filter(project__workspace=workspace)
        completed_runs = runs.exclude(status__in=['pending', 'running'])

        stats['total_projects'] = projects.count()
        stats['total_runs'] = runs.count()

        if completed_runs.exists():
            total_rate = sum(r.pass_rate for r in completed_runs)
            stats['pass_rate'] = f"{round(total_rate / completed_runs.count(), 1)}%"

        recent_runs = runs.select_related('project', 'triggered_by')[:5]

    context = {
        'stats': stats,
        'recent_runs': recent_runs,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def new_test(request):
    """Placeholder para Fase 3."""
    return render(request, 'dashboard/new_test_placeholder.html', {})


@login_required
def tests(request):
    """Placeholder para Fase 3."""
    return render(request, 'dashboard/new_test_placeholder.html', {})


@login_required
def test_runs(request):
    return render(request, 'dashboard/runs.html', {})


@login_required
def monitoring(request):
    return render(request, 'dashboard/monitoring.html', {})

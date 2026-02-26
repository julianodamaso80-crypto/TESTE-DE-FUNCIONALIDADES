import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.dashboard.analytics import (
    get_pass_rate_trend,
    get_runs_last_30_days,
    get_summary_stats,
    get_top_failing_projects,
)


@login_required
def home(request):
    workspace = request.workspace
    stats = {
        'total_runs': 0,
        'runs_last_30': 0,
        'pass_rate_30': 0,
        'pass_rate_trend': 0,
        'total_projects': 0,
        'bugs_caught': 0,
    }
    recent_runs = []
    runs_chart = []
    trend_chart = []
    failing = []

    quota_usage = {}
    quota_limits = {}

    if workspace:
        from apps.testing.models import TestRun
        from apps.workspaces.quota import get_workspace_usage

        stats = get_summary_stats(workspace)
        runs_chart = get_runs_last_30_days(workspace)
        trend_chart = get_pass_rate_trend(workspace)
        failing = get_top_failing_projects(workspace)
        recent_runs = TestRun.objects.filter(
            project__workspace=workspace
        ).select_related('project').order_by('-created_at')[:8]
        quota_usage = get_workspace_usage(workspace)
        quota_limits = workspace.get_plan_limits()

    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'recent_runs': recent_runs,
        'runs_chart_json': json.dumps(runs_chart),
        'trend_chart_json': json.dumps(trend_chart),
        'failing_projects': failing,
        'quota_usage': quota_usage,
        'quota_limits': quota_limits,
    })


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

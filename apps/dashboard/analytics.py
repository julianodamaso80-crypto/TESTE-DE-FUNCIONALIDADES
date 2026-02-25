from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from apps.testing.models import TestProject, TestRun


def get_runs_last_30_days(workspace):
    end = timezone.now()
    start = end - timedelta(days=30)
    runs_by_day = []
    for i in range(30):
        day = start + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = TestRun.objects.filter(
            project__workspace=workspace,
            created_at__gte=day_start,
            created_at__lt=day_end,
        ).count()
        passed = TestRun.objects.filter(
            project__workspace=workspace,
            created_at__gte=day_start,
            created_at__lt=day_end,
            status='passed',
        ).count()
        runs_by_day.append({
            'date': day.strftime('%d/%m'),
            'total': count,
            'passed': passed,
            'failed': count - passed,
        })
    return runs_by_day


def get_pass_rate_trend(workspace):
    runs = TestRun.objects.filter(
        project__workspace=workspace,
        status__in=['passed', 'failed'],
        completed_at__isnull=False,
    ).order_by('-created_at')[:20]
    return [
        {'date': r.created_at.strftime('%d/%m'), 'pass_rate': r.pass_rate}
        for r in reversed(runs)
    ]


def get_top_failing_projects(workspace):
    projects = TestProject.objects.filter(workspace=workspace, is_active=True)
    result = []
    for p in projects:
        runs = TestRun.objects.filter(
            project=p, status__in=['passed', 'failed']
        ).order_by('-created_at')[:10]
        if runs.exists():
            avg_pass = sum(r.pass_rate for r in runs) / len(runs)
            result.append({
                'name': p.name,
                'avg_pass_rate': round(avg_pass, 1),
                'total_runs': runs.count(),
            })
    return sorted(result, key=lambda x: x['avg_pass_rate'])[:5]


def get_summary_stats(workspace):
    total_runs = TestRun.objects.filter(project__workspace=workspace).count()
    last_30 = TestRun.objects.filter(
        project__workspace=workspace,
        created_at__gte=timezone.now() - timedelta(days=30),
    )
    passed_30 = last_30.filter(status='passed').count()
    total_30 = last_30.count()
    pass_rate_30 = round(passed_30 / total_30 * 100) if total_30 > 0 else 0

    prev_30 = TestRun.objects.filter(
        project__workspace=workspace,
        created_at__gte=timezone.now() - timedelta(days=60),
        created_at__lt=timezone.now() - timedelta(days=30),
    )
    prev_total = prev_30.count()
    prev_passed = prev_30.filter(status='passed').count()
    prev_rate = round(prev_passed / prev_total * 100) if prev_total > 0 else 0
    trend = pass_rate_30 - prev_rate

    bugs_caught = last_30.aggregate(
        total_failed=Sum('failed_cases')
    )['total_failed'] or 0

    return {
        'total_runs': total_runs,
        'runs_last_30': total_30,
        'pass_rate_30': pass_rate_30,
        'pass_rate_trend': trend,
        'total_projects': TestProject.objects.filter(
            workspace=workspace, is_active=True
        ).count(),
        'bugs_caught': bugs_caught,
    }

from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.analytics import track
from .ai_service import generate_test_cases
from .executor import run_test_execution_smart
from .forms import TestProjectForm
from .models import ScheduleFrequency, ScheduledTest, TestCase, TestProject, TestRun


@login_required
def new_test(request):
    """GET: mostra form. POST: cria projeto + gera casos + cria run."""
    workspace = request.workspace
    if not workspace:
        messages.error(request, 'Selecione um workspace primeiro.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = TestProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.workspace = workspace
            project.created_by = request.user
            project.save()

            # Generate test cases via AI / mock
            result = generate_test_cases(
                base_url=project.base_url,
                test_type=project.test_type,
                special_instructions=project.special_instructions,
            )

            # Create TestRun
            run = TestRun.objects.create(
                project=project,
                triggered_by=request.user,
                status='pending',
                ai_model_used=result.get('model_used', ''),
                ai_summary=result.get('test_strategy', ''),
            )

            # Create TestCases
            test_cases = result.get('test_cases', [])
            for i, tc in enumerate(test_cases):
                TestCase.objects.create(
                    run=run,
                    title=tc.get('title', f'Test Case {i + 1}'),
                    description=tc.get('description', ''),
                    category=tc.get('category', ''),
                    steps=tc.get('steps', []),
                    order=i,
                )

            run.total_cases = len(test_cases)
            run.save(update_fields=['total_cases'])

            track(str(request.user.id), 'test_run_created', {
                'test_type': project.test_type,
                'total_cases': run.total_cases,
                'workspace_plan': request.workspace.plan,
            })

            if not request.user.onboarding_completed:
                request.user.onboarding_completed = True
                request.user.save(update_fields=['onboarding_completed'])

            messages.success(request, f'{len(test_cases)} test cases generated for "{project.name}".')
            return redirect('testing:run_detail', run_id=run.id)
    else:
        form = TestProjectForm()

    return render(request, 'testing/new_test.html', {'form': form})


@login_required
def run_detail(request, run_id):
    """Detalhe de um TestRun com cases agrupados por categoria."""
    workspace = request.workspace
    run = get_object_or_404(
        TestRun.objects.select_related('project', 'triggered_by'),
        id=run_id,
        project__workspace=workspace,
    )

    cases = run.cases.all()
    categories = defaultdict(list)
    for case in cases:
        key = case.category or 'General'
        categories[key].append(case)

    return render(request, 'testing/run_detail.html', {
        'run': run,
        'categories': dict(categories),
    })


@login_required
def execute_run(request, run_id):
    """POST only: executa testes via Celery (async) ou fallback síncrono."""
    if request.method != 'POST':
        return redirect('testing:run_detail', run_id=run_id)

    workspace = request.workspace
    run = get_object_or_404(
        TestRun,
        id=run_id,
        project__workspace=workspace,
    )

    try:
        from .tasks import run_test_execution
        task = run_test_execution.delay(str(run.id))
        run.celery_task_id = task.id
        run.status = 'running'
        run.save(update_fields=['celery_task_id', 'status'])
        messages.info(request, 'Execução iniciada em background...')
    except Exception:
        # Redis offline: fallback síncrono
        run_test_execution_smart(run)
        messages.success(request, f'Execução concluída: {run.pass_rate}% pass rate')

    track(str(request.user.id), 'test_run_executed', {
        'pass_rate': run.pass_rate,
        'status': run.status,
    })

    return redirect('testing:run_detail', run_id=run.id)


@login_required
def project_list(request):
    """Lista TestProjects do workspace atual."""
    workspace = request.workspace
    if not workspace:
        messages.error(request, 'Selecione um workspace primeiro.')
        return redirect('dashboard:home')

    projects = TestProject.objects.filter(
        workspace=workspace, is_active=True,
    ).prefetch_related('runs')

    # Enrich with stats
    project_data = []
    for project in projects:
        runs = project.runs.all()
        total_runs = runs.count()
        completed_runs = runs.exclude(status__in=['pending', 'running'])
        avg_pass_rate = None
        if completed_runs.exists():
            total = sum(r.pass_rate for r in completed_runs)
            avg_pass_rate = round(total / completed_runs.count(), 1)
        project_data.append({
            'project': project,
            'total_runs': total_runs,
            'avg_pass_rate': avg_pass_rate,
        })

    return render(request, 'testing/project_list.html', {
        'project_data': project_data,
    })


@login_required
def run_report(request, run_id):
    run = get_object_or_404(TestRun, id=run_id, project__workspace=request.workspace)
    cases = run.cases.all().order_by('order')
    categories = {}
    for case in cases:
        cat = case.category or 'General'
        if cat not in categories:
            categories[cat] = {'passed': 0, 'failed': 0, 'cases': []}
        categories[cat]['cases'].append(case)
        if case.status == 'passed':
            categories[cat]['passed'] += 1
        else:
            categories[cat]['failed'] += 1
    return render(request, 'testing/run_report.html', {
        'run': run, 'cases': cases, 'categories': categories,
    })


def run_public(request, share_token):
    run = get_object_or_404(TestRun, share_token=share_token, is_public=True)
    cases = run.cases.all().order_by('order')
    categories = {}
    for case in cases:
        cat = case.category or 'General'
        if cat not in categories:
            categories[cat] = {'passed': 0, 'failed': 0, 'cases': []}
        categories[cat]['cases'].append(case)
        if case.status == 'passed':
            categories[cat]['passed'] += 1
        else:
            categories[cat]['failed'] += 1
    return render(request, 'testing/run_public.html', {
        'run': run, 'cases': cases, 'categories': categories,
    })


@login_required
@require_POST
def toggle_share(request, run_id):
    run = get_object_or_404(TestRun, id=run_id, project__workspace=request.workspace)
    run.is_public = not run.is_public
    run.save(update_fields=['is_public'])
    if run.is_public:
        track(str(request.user.id), 'run_shared_public', {'run_id': str(run.id)})
    messages.success(request, f"Link público {'ativado' if run.is_public else 'desativado'}")
    return redirect('testing:run_detail', run_id=run_id)


@login_required
def schedule_list(request):
    schedules = ScheduledTest.objects.filter(
        project__workspace=request.workspace
    ).select_related('project')
    return render(request, 'testing/schedule_list.html', {'schedules': schedules})


@login_required
def schedule_create(request, project_id):
    project = get_object_or_404(TestProject, id=project_id, workspace=request.workspace)
    if request.method == 'POST':
        frequency = request.POST.get('frequency', 'daily')
        notify_email = request.POST.get('notify_email') == 'on'
        notify_failure_only = request.POST.get('notify_on_failure_only') == 'on'
        schedule, created = ScheduledTest.objects.get_or_create(
            project=project,
            defaults={
                'created_by': request.user,
                'frequency': frequency,
                'notify_email': notify_email,
                'notify_on_failure_only': notify_failure_only,
            },
        )
        if not created:
            schedule.frequency = frequency
            schedule.notify_email = notify_email
            schedule.notify_on_failure_only = notify_failure_only
            schedule.save()
        schedule.calculate_next_run()
        messages.success(request, f'Agendamento {frequency} configurado!')
        return redirect('testing:schedule_list')
    return render(request, 'testing/schedule_form.html', {
        'project': project,
        'frequencies': ScheduleFrequency.choices,
    })


@login_required
@require_POST
def schedule_toggle(request, schedule_id):
    schedule = get_object_or_404(
        ScheduledTest, id=schedule_id, project__workspace=request.workspace
    )
    schedule.is_active = not schedule.is_active
    if schedule.is_active:
        schedule.calculate_next_run()
    schedule.save(update_fields=['is_active'])
    messages.success(request, f"Agendamento {'ativado' if schedule.is_active else 'pausado'}")
    return redirect('testing:schedule_list')

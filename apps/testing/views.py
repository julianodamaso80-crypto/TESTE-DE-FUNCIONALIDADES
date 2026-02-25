from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .ai_service import generate_test_cases
from .executor import simulate_test_execution
from .forms import TestProjectForm
from .models import TestCase, TestProject, TestRun


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
        simulate_test_execution(run)
        messages.success(request, f'Execução concluída: {run.pass_rate}% pass rate')

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

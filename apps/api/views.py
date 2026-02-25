from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.testing.models import TestCase, TestProject, TestRun

from .serializers import CreateTestSerializer, TestProjectSerializer, TestRunSerializer


class ProjectListView(APIView):
    def get(self, request):
        projects = TestProject.objects.filter(
            workspace=request.workspace, is_active=True
        )
        return Response(TestProjectSerializer(projects, many=True).data)


class CreateTestView(APIView):
    def post(self, request):
        s = CreateTestSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)

        d = s.validated_data
        project = TestProject.objects.create(
            workspace=request.workspace,
            created_by=request.user,
            name=d['name'],
            base_url=d['url'],
            test_type=d['test_type'],
            special_instructions=d.get('instructions', ''),
            auth_email=d.get('auth_email', ''),
            auth_password=d.get('auth_password', ''),
        )

        from apps.testing.ai_service import generate_test_cases

        ai_result = generate_test_cases(
            project.base_url, project.test_type, project.special_instructions
        )

        if 'error' in ai_result:
            return Response(
                {'error': ai_result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        run = TestRun.objects.create(
            project=project, triggered_by=request.user, status='pending'
        )

        for i, tc in enumerate(ai_result.get('test_cases', [])):
            TestCase.objects.create(
                run=run,
                title=tc.get('title', ''),
                description=tc.get('description', ''),
                category=tc.get('category', ''),
                steps=tc.get('steps', []),
                order=i,
            )

        run.total_cases = run.cases.count()
        run.save(update_fields=['total_cases'])

        if d.get('run_immediately'):
            from apps.testing.tasks import run_test_execution

            try:
                run_test_execution.delay(str(run.id))
            except Exception:
                from apps.testing.executor import run_test_execution_smart

                run_test_execution_smart(run)

        return Response(
            {
                'project_id': str(project.id),
                'run_id': str(run.id),
                'total_cases': run.total_cases,
                'status': run.status,
            },
            status=status.HTTP_201_CREATED,
        )


class RunDetailView(APIView):
    def get(self, request, run_id):
        run = get_object_or_404(
            TestRun, id=run_id, project__workspace=request.workspace
        )
        return Response(TestRunSerializer(run).data)


class RunStatusView(APIView):
    def get(self, request, run_id):
        run = get_object_or_404(
            TestRun, id=run_id, project__workspace=request.workspace
        )
        return Response({
            'run_id': str(run.id),
            'status': run.status,
            'pass_rate': run.pass_rate,
            'total': run.total_cases,
            'passed': run.passed_cases,
            'failed': run.failed_cases,
        })

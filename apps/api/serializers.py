from rest_framework import serializers

from apps.testing.models import TestCase, TestProject, TestRun


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = [
            'id', 'title', 'description', 'category', 'status',
            'error_message', 'ai_fix_suggestion', 'duration_ms', 'steps',
        ]


class TestRunSerializer(serializers.ModelSerializer):
    cases = TestCaseSerializer(many=True, read_only=True)
    pass_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = TestRun
        fields = [
            'id', 'status', 'pass_rate', 'total_cases', 'passed_cases',
            'failed_cases', 'ai_summary', 'duration_secs', 'created_at',
            'completed_at', 'cases',
        ]


class TestProjectSerializer(serializers.ModelSerializer):
    last_run = serializers.SerializerMethodField()

    class Meta:
        model = TestProject
        fields = [
            'id', 'name', 'base_url', 'test_type', 'special_instructions',
            'is_active', 'created_at', 'last_run',
        ]

    def get_last_run(self, obj):
        run = obj.runs.first()
        if run:
            return TestRunSerializer(run).data
        return None


class CreateTestSerializer(serializers.Serializer):
    url = serializers.URLField()
    name = serializers.CharField(max_length=200)
    test_type = serializers.ChoiceField(choices=['ui', 'api', 'both'], default='ui')
    instructions = serializers.CharField(required=False, allow_blank=True, default='')
    auth_email = serializers.EmailField(required=False, allow_blank=True, default='')
    auth_password = serializers.CharField(required=False, allow_blank=True, default='')
    run_immediately = serializers.BooleanField(default=True)

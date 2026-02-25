import uuid
from django.db import migrations, models


def populate_share_tokens(apps, schema_editor):
    TestRun = apps.get_model('testing', 'TestRun')
    for run in TestRun.objects.all():
        run.share_token = uuid.uuid4()
        run.save(update_fields=['share_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0002_testrun_celery_task_id'),
    ]

    operations = [
        # 1) Add share_token without unique constraint
        migrations.AddField(
            model_name='testrun',
            name='share_token',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        # 2) Add is_public
        migrations.AddField(
            model_name='testrun',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        # 3) Add screenshot_path
        migrations.AddField(
            model_name='testcase',
            name='screenshot_path',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        # 4) Populate unique UUIDs for existing rows
        migrations.RunPython(populate_share_tokens, migrations.RunPython.noop),
        # 5) Now make share_token unique and non-null
        migrations.AlterField(
            model_name='testrun',
            name='share_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_task_theme_color"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tasks",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="daysummary",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="day_summaries",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="daysummary",
            name="date",
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AddConstraint(
            model_name="daysummary",
            constraint=models.UniqueConstraint(
                fields=("user", "date"),
                name="unique_daysummary_user_date",
            ),
        ),
    ]

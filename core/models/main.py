from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.core.validators import RegexValidator

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        DOING = "doing", "General Doing"
        TODAY = "today", "Today Doing"
        DONE = "done", "Done"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)

    estimated_minutes = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: You can enable validators if you want
    hex_color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Enter a valid hex color.'
    )

    background_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        validators=[hex_color_validator]
    )

    color = models.CharField(
        max_length=7,
        default="#000000",
        validators=[hex_color_validator]
    )

    def progress(self):
        if self.estimated_minutes == 0:
            return 0

        focused = self.total_focused_minutes()
        return min(100, int((focused / self.estimated_minutes) * 100))

    def total_focused_minutes(self):
        """Use SQL SUM for better performance."""
        return self.focus_sessions.aggregate(total=Sum("duration_minutes"))["total"] or 0

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class FocusSession(models.Model):
    task = models.ForeignKey(Task, related_name="focus_sessions", on_delete=models.CASCADE)

    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    duration_minutes = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=False)  # forest-like success marker
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Auto compute duration if ended_at is provided
        if self.started_at and self.ended_at and self.duration_minutes == 0:
            delta = self.ended_at - self.started_at
            self.duration_minutes = max(0, int(delta.total_seconds() // 60))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Focus Session {self.task_id} - {self.duration_minutes}m"


class DaySummary(models.Model):
    date = models.DateField(default=timezone.localdate)
    summary_text = models.TextField(blank=True)

    total_focused_minutes = models.PositiveIntegerField(default=0)

    def recompute(self):
        """Recalculate the total focus minutes for the day."""
        start = timezone.make_aware(
            timezone.datetime.combine(self.date, timezone.datetime.min.time())
        )
        end = timezone.make_aware(
            timezone.datetime.combine(self.date, timezone.datetime.max.time())
        )

        minutes = FocusSession.objects.filter(
            started_at__gte=start,
            started_at__lte=end
        ).aggregate(total=Sum("duration_minutes"))["total"] or 0

        self.total_focused_minutes = minutes
        self.save()

    def __str__(self):
        return f"Summary {self.date}"


class Block(models.Model):
    """A scheduling block tied to a Task."""

    task = models.ForeignKey(Task, related_name="blocks", on_delete=models.CASCADE)

    title = models.CharField(max_length=200, blank=True)
    desc = models.TextField(blank=True)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):

        # Default title/description from task
        if not self.title:
            self.title = self.task.title

        if not self.desc:
            self.desc = self.task.description

        # Default end_date = start_date + estimated task duration
        if not self.end_date and self.task.estimated_minutes:
            self.end_date = self.start_date + timedelta(minutes=self.task.estimated_minutes)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Block: {self.title} ({self.start_date.isoformat()})"

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

    # Title and desc are derived from the linked Task and are not user-editable
    title = models.CharField(max_length=200, blank=True, editable=False)
    desc = models.TextField(blank=True, editable=False)

    start_date = models.DateTimeField(default=timezone.now)
    # Not editable by API/forms; computed from `start_date` + task.estimated_minutes
    end_date = models.DateTimeField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):

        # Always synchronize title/description from the Task so they're not
        # editable by clients or forms.
        try:
            self.title = self.task.title
        except Exception:
            self.title = self.title or ""

        try:
            self.desc = self.task.description
        except Exception:
            self.desc = self.desc or ""

        # Auto-compute end_date from start_date + task estimated_minutes
        # Because `end_date` is not user-editable, always compute it whenever
        # we have a start_date and a task with an estimated duration.
        try:
            estimated = int(self.task.estimated_minutes or 0)
        except Exception:
            estimated = 0

        if self.start_date and estimated:
            self.end_date = self.start_date + timedelta(minutes=estimated)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Block: {self.title} ({self.start_date.isoformat()})"

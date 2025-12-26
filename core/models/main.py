from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Task(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

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

    hex_color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Enter a valid hex color.'
    )

    background_color = models.CharField(max_length=7, default="#FFFFFF", validators=[hex_color_validator])
    theme_color = models.CharField(max_length=7, default="#10b981", validators=[hex_color_validator])
    color = models.CharField(max_length=7, default="#000000", validators=[hex_color_validator])

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
    success = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Auto compute duration if ended_at is provided
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            # Recalculate duration only if it wasn't manually overridden or if it's 0
            computed_minutes = max(0, int(delta.total_seconds() // 60))
            if self.duration_minutes == 0 or self.duration_minutes != computed_minutes:
                self.duration_minutes = computed_minutes

        # Enforce success rule: false if duration under 10 minutes
        self.success = self.duration_minutes >= 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Focus Session {self.task_id} - {self.duration_minutes}m"


class DaySummary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="day_summaries",
    )

    date = models.DateField(default=timezone.localdate)
    summary_text = models.TextField(blank=True)

    total_focused_minutes = models.PositiveIntegerField(default=0)

    def recompute(self):
        """Recalculate the total focus minutes for the day."""
        # FIX: Use __date lookup. This handles timezone conversion automatically
        # and lets PostgreSQL do the heavy lifting.
        minutes_qs = FocusSession.objects.filter(started_at__date=self.date)
        if self.user_id is not None:
            minutes_qs = minutes_qs.filter(task__user_id=self.user_id)

        minutes = minutes_qs.aggregate(total=Sum("duration_minutes"))["total"] or 0

        self.total_focused_minutes = minutes
        self.save()

    def __str__(self):
        return f"Summary {self.date} - {self.total_focused_minutes}m"


class Block(models.Model):
    """A scheduling block tied to a Task."""
    task = models.ForeignKey(Task, related_name="blocks", on_delete=models.CASCADE)

    title = models.CharField(max_length=200, blank=True)
    desc = models.TextField(blank=True)
    done = models.BooleanField(default=False)

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.task.title

        if not self.desc:
            self.desc = self.task.description

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Block: {self.title} ({self.start_date.isoformat()})"


class Setting(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="setting",
    )

    day_bounds = models.JSONField(default=list, blank=True)
    column_colors = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Setting for user {self.user_id}"


class Note(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    background_color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        validators=[
            RegexValidator(
                regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Enter a valid hex color.",
            )
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=FocusSession)
def update_day_summary(sender, instance, **kwargs):
    session_date = timezone.localdate(instance.started_at)
    summary, created = DaySummary.objects.get_or_create(
        user=instance.task.user,
        date=session_date,
    )
    
    summary.recompute()
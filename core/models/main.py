from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        DOING = "doing", "General Doing"
        TODAY = "today", "Today Doing"
        DONE = "done", "Done"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)
    progress = models.PositiveIntegerField(default=0)  # 0-100 for fill bar
    estimated_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_focused_minutes(self):
        return sum(self.focus_sessions.values_list("duration_minutes", flat=True))

    

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
        if self.ended_at and self.started_at and self.duration_minutes == 0:
            delta = self.ended_at - self.started_at
            self.duration_minutes = max(0, int(delta.total_seconds() // 60))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Focus {self.task_id} {self.duration_minutes}m"


    


class DaySummary(models.Model):
    date = models.DateField(default=timezone.localdate)
    summary_text = models.TextField(blank=True)

    total_focused_minutes = models.PositiveIntegerField(default=0)

    def recompute(self):
        start = timezone.make_aware(timezone.datetime.combine(self.date, timezone.datetime.min.time()))
        end = timezone.make_aware(timezone.datetime.combine(self.date, timezone.datetime.max.time()))

        focus_minutes = FocusSession.objects.filter(started_at__gte=start, started_at__lte=end).aggregate(
            m=models.Sum("duration_minutes")
        )["m"] or 0

        self.total_focused_minutes = focus_minutes
        self.save()

    def __str__(self):
        return f"Summary {self.date}"

# Create your models here.
    
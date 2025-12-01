from rest_framework import viewsets, decorators, response, status
from django.utils import timezone
from django.db.models import Sum, Count, Case, When, IntegerField
from django.db.models.functions import TruncWeek, TruncMonth
from datetime import timedelta

from core.models.main import Task, FocusSession, DaySummary
from core.serializers.main import (
    TaskSerializer,
    FocusSessionSerializer,
    DaySummarySerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at")
    serializer_class = TaskSerializer

    @decorators.action(detail=True, methods=["post"], url_path="start-focus")
    def start_focus(self, request, pk=None):
        task = self.get_object()
        fs = FocusSession.objects.create(task=task, started_at=timezone.now())
        return response.Response(FocusSessionSerializer(fs).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["post"], url_path="end-focus")
    def end_focus(self, request, pk=None):
        task = self.get_object()
        fs_id = request.data.get("focus_session_id")
        try:
            fs = FocusSession.objects.get(id=fs_id, task=task)
        except FocusSession.DoesNotExist:
            return response.Response({"detail": "Focus session not found"}, status=404)
        fs.ended_at = timezone.now()
        fs.success = bool(request.data.get("success", True))
        fs.save()
        return response.Response(FocusSessionSerializer(fs).data)

    @decorators.action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        task = self.get_object()
        focus_minutes = task.focus_sessions.aggregate(m=Sum("duration_minutes"))["m"] or 0
        return response.Response({
            "focused_minutes": focus_minutes,
            "progress": task.progress,
            "status": task.status,
        })


class FocusSessionViewSet(viewsets.ModelViewSet):
    queryset = FocusSession.objects.all().order_by("-started_at")
    serializer_class = FocusSessionSerializer


class DaySummaryViewSet(viewsets.ModelViewSet):
    queryset = DaySummary.objects.all().order_by("-date")
    serializer_class = DaySummarySerializer

    @decorators.action(detail=False, methods=["post"], url_path="recompute")
    def recompute(self, request):
        date_str = request.data.get("date")
        date = timezone.datetime.fromisoformat(date_str).date() if date_str else timezone.localdate()
        summary, _ = DaySummary.objects.get_or_create(date=date)
        summary.recompute()
        return response.Response(DaySummarySerializer(summary).data)

    @decorators.action(detail=False, methods=["get"], url_path="weekly")
    def weekly(self, request):
        tz = timezone.get_current_timezone()
        weeks = int(request.query_params.get("weeks", 12))
        start_str = request.query_params.get("start")

        today = timezone.localdate()
        if start_str:
            start_date = timezone.datetime.fromisoformat(start_str).date()
        else:
            start_date = today - timedelta(days=today.weekday())  # Monday of this week
            start_date = start_date - timedelta(weeks=weeks - 1)

        end_date = start_date + timedelta(weeks=weeks)
        start_dt = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()), tz)
        end_dt = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.min.time()), tz)

        qs = (
            FocusSession.objects.filter(started_at__gte=start_dt, started_at__lt=end_dt)
            .annotate(period=TruncWeek("started_at", tzinfo=tz))
            .values("period")
            .annotate(
                total_minutes=Sum("duration_minutes"),
                session_count=Count("id"),
                success_count=Sum(Case(When(success=True, then=1), default=0, output_field=IntegerField())),
            )
            .order_by("period")
        )

        data = [
            {
                "week_start": item["period"].date().isoformat(),
                "week_end": (item["period"].date() + timedelta(days=6)).isoformat(),
                "focused_minutes": item.get("total_minutes", 0) or 0,
                "sessions": item.get("session_count", 0) or 0,
                "successes": item.get("success_count", 0) or 0,
            }
            for item in qs
        ]

        return response.Response({
            "start": start_date.isoformat(),
            "end": (end_date - timedelta(days=1)).isoformat(),
            "weeks": weeks,
            "items": data,
        })

    @decorators.action(detail=False, methods=["get"], url_path="monthly")
    def monthly(self, request):
        tz = timezone.get_current_timezone()
        months = int(request.query_params.get("months", 6))
        start_str = request.query_params.get("start")

        today = timezone.localdate().replace(day=1)
        if start_str:
            start_date = timezone.datetime.fromisoformat(start_str).date().replace(day=1)
        else:
            # Go back (months-1) months
            year = today.year
            month = today.month - (months - 1)
            while month <= 0:
                month += 12
                year -= 1
            start_date = timezone.datetime(year, month, 1).date()

        # Compute end_date as first day of the month after the span
        end_year = start_date.year
        end_month = start_date.month + months
        while end_month > 12:
            end_month -= 12
            end_year += 1
        end_date = timezone.datetime(end_year, end_month, 1).date()

        start_dt = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()), tz)
        end_dt = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.min.time()), tz)

        qs = (
            FocusSession.objects.filter(started_at__gte=start_dt, started_at__lt=end_dt)
            .annotate(period=TruncMonth("started_at", tzinfo=tz))
            .values("period")
            .annotate(
                total_minutes=Sum("duration_minutes"),
                session_count=Count("id"),
                success_count=Sum(Case(When(success=True, then=1), default=0, output_field=IntegerField())),
            )
            .order_by("period")
        )

        data = [
            {
                "month": item["period"].date().strftime("%Y-%m"),
                "focused_minutes": item.get("total_minutes", 0) or 0,
                "sessions": item.get("session_count", 0) or 0,
                "successes": item.get("success_count", 0) or 0,
            }
            for item in qs
        ]

        return response.Response({
            "start": start_date.isoformat(),
            "end": (end_date - timedelta(days=1)).isoformat(),
            "months": months,
            "items": data,
        })

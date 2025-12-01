from rest_framework import serializers
from core.models.main import Task, FocusSession, DaySummary

class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusSession
        fields = [
            "id",
            "task",
            "started_at",
            "ended_at",
            "duration_minutes",
            "success",
            "notes",
        ]
        read_only_fields = ["duration_minutes"]

 

class DaySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DaySummary
        fields = [
            "id",
            "date",
            "summary_text",
            "total_focused_minutes",
        ]

class TaskSerializer(serializers.ModelSerializer):
    focus_sessions = FocusSessionSerializer(many=True, read_only=True)

    total_focused_minutes = serializers.SerializerMethodField()

    def get_total_focused_minutes(self, obj):
        return obj.total_focused_minutes()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "progress",
            "estimated_minutes",
            "created_at",
            "updated_at",
            "focus_sessions",
            "total_focused_minutes",
        ]

from rest_framework import serializers
from core.models.main import Task, FocusSession, DaySummary, Block

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
        read_only_fields = ["total_focused_minutes"]


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = [
            "id",
            "task",
            "title",
            "desc",
            "start_date",
            "end_date",
        ]
        # title/desc/end_date are derived server-side and not writable by clients
        read_only_fields = ["title", "desc", "end_date"]

class TaskSerializer(serializers.ModelSerializer):
    focus_sessions = FocusSessionSerializer(many=True, read_only=True)
    # include full block objects for tasks
    blocks = serializers.SerializerMethodField()

    progress = serializers.SerializerMethodField()

    total_focused_minutes = serializers.SerializerMethodField()

    def get_total_focused_minutes(self, obj):
        return obj.total_focused_minutes()

    def get_progress(self, obj):
        # call the model method to compute progress
        try:
            return obj.progress()
        except Exception:
            return 0

    def get_blocks(self, obj):
        # return minimal block info
        qs = getattr(obj, "blocks", None)
        if qs is None:
            return []
        # Use BlockSerializer representation to keep consistent formatting
        from .main import BlockSerializer as _BlockSerializer  # local import to avoid circular at top-level
        return _BlockSerializer(qs.all(), many=True).data

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "progress",
            "estimated_minutes",
            "background_color",
            "theme_color",
            "color",
            "created_at",
            "updated_at",
            "focus_sessions",
            "blocks",
            "total_focused_minutes",
        ]

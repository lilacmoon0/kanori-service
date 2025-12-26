from rest_framework import serializers
from core.models.main import Task, FocusSession, DaySummary, Block, Setting, Note

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
    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "end_date must be greater than or equal to start_date"
            })

        return attrs

    class Meta:
        model = Block
        fields = [
            "id",
            "task",
            "title",
            "desc",
            "done",
            "start_date",
            "end_date",
        ]
        read_only_fields = ["title", "desc"]

class TaskSerializer(serializers.ModelSerializer):
    focus_sessions = FocusSessionSerializer(many=True, read_only=True)
    blocks = serializers.SerializerMethodField()

    progress = serializers.SerializerMethodField()

    total_focused_minutes = serializers.SerializerMethodField()

    def get_total_focused_minutes(self, obj):
        return obj.total_focused_minutes()

    def get_progress(self, obj):
        try:
            return obj.progress()
        except Exception:
            return 0

    def get_blocks(self, obj):
        qs = getattr(obj, "blocks", None)
        if qs is None:
            return []
        from .main import BlockSerializer as _BlockSerializer  
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


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = [
            "id",
            "day_bounds",
            "column_colors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "background_color",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

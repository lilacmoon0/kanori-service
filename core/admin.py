from django.contrib import admin
from .models.main import Task, FocusSession, DaySummary, Block, Setting, Note


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "status", "estimated_minutes", "created_at")
	list_filter = ("status",)
	search_fields = ("title", "description")


@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
	list_display = ("id", "task", "started_at", "ended_at", "duration_minutes", "success")
	list_filter = ("success",)
	search_fields = ("task__title",)


@admin.register(DaySummary)
class DaySummaryAdmin(admin.ModelAdmin):
	list_display = ("id", "date", "total_focused_minutes")
	ordering = ("-date",)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "task", "start_date", "end_date")
	search_fields = ("title", "task__title")


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "created_at", "updated_at")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "user", "background_color", "created_at")
	search_fields = ("title", "content")


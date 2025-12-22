from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views.auth import LoginView, RegisterView, MeView
from .views.main import (
	TaskViewSet,
	FocusSessionViewSet,
	DaySummaryViewSet,
	BlockViewSet,
	SettingViewSet,
	NoteViewSet,
)

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")
router.register("focus-sessions", FocusSessionViewSet, basename="focus-session")
router.register("day-summaries", DaySummaryViewSet, basename="day-summary")
router.register("blocks", BlockViewSet, basename="block")
router.register("setting", SettingViewSet, basename="setting")
router.register("notes", NoteViewSet, basename="note")

urlpatterns = [
	path("", include(router.urls)),
	path("auth/register/", RegisterView.as_view(), name="auth-register"),
	path("auth/login/", LoginView.as_view(), name="auth-login"),
	path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
	path("auth/me/", MeView.as_view(), name="auth-me"),
]

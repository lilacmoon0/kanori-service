from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views.auth import RegisterView, MeView
from .views.main import TaskViewSet, FocusSessionViewSet, DaySummaryViewSet, BlockViewSet

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet)
router.register("focus-sessions", FocusSessionViewSet)
router.register("day-summaries", DaySummaryViewSet)
router.register("blocks", BlockViewSet)

urlpatterns = [
	path("", include(router.urls)),
	path("auth/register/", RegisterView.as_view(), name="auth-register"),
	path("auth/login/", TokenObtainPairView.as_view(), name="auth-login"),
	path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
	path("auth/me/", MeView.as_view(), name="auth-me"),
]

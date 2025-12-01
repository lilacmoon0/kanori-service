from rest_framework import routers
from .views.main import TaskViewSet, FocusSessionViewSet, DaySummaryViewSet

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet)
router.register("focus-sessions", FocusSessionViewSet)
router.register("day-summaries", DaySummaryViewSet)

urlpatterns = router.urls

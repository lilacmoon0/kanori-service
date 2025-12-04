from rest_framework import routers
from .views.main import TaskViewSet, FocusSessionViewSet, DaySummaryViewSet, BlockViewSet

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet)
router.register("focus-sessions", FocusSessionViewSet)
router.register("day-summaries", DaySummaryViewSet)
router.register("blocks", BlockViewSet)

urlpatterns = router.urls

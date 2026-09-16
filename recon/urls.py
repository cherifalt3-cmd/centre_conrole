from rest_framework.routers import DefaultRouter
from .views import TargetViewSet, ToolViewSet

router = DefaultRouter()
router.register('targets', TargetViewSet)
router.register('tools', ToolViewSet)

urlpatterns = router.urls

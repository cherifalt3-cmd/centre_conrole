from rest_framework.routers import DefaultRouter
from .views import TargetViewSet, ToolViewSet, CommandPresetViewSet

router = DefaultRouter()
router.register('targets', TargetViewSet)
router.register('tools', ToolViewSet)
router.register('command-presets', CommandPresetViewSet)

urlpatterns = router.urls

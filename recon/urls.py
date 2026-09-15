from rest_framework.routers import DefaultRouter
from .views import TargetViewSet

router = DefaultRouter()
router.register('targets', TargetViewSet)

urlpatterns = router.urls

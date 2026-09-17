from rest_framework.routers import DefaultRouter
from .views import BoardViewSet, ColumnViewSet, CardViewSet

router = DefaultRouter()
router.register('boards', BoardViewSet)
router.register('columns', ColumnViewSet)
router.register('cards', CardViewSet)

urlpatterns = router.urls

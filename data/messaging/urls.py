from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, dlr_webhook, mo_webhook


router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')


urlpatterns = [
path('', include(router.urls)),
path('webhooks/dlr', dlr_webhook, name='dlr-webhook'),
path('webhooks/mo', mo_webhook, name='mo-webhook'),
]
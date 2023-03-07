from django.urls import path
from backend.views import index, LogoUploadView,ImageAPIView, LogoUploadView2

urlpatterns = [
    path('', index),
    path('upload-logo/', LogoUploadView2.as_view(), name='logo-upload'),
    path('api/image/<str:id>/<str:extension>', ImageAPIView.as_view(), name='image_api'),
]
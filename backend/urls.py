from django.urls import path
from backend.views import index, LogoUploadView

urlpatterns = [
    path('', index),
    path('upload-logo/', LogoUploadView.as_view(), name='logo-upload'),
]

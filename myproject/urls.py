# project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from people.views import (
    StudentViewSet, 
    StaffViewSet, 
    EmployeeViewSet, 
    PDFUploadView, 
    UploadPDFView,
    stats_view,  # <- import செய்தது முக்கியம்
)

# DRF router for ViewSets
router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API ViewSets
    path('api/', include(router.urls)),

    # PDF Upload (class-based)
    path('api/upload-pdf/', PDFUploadView.as_view(), name='upload-pdf'),
    path('upload-pdf/', UploadPDFView.as_view(), name='upload-pdf-simple'),

    # Stats endpoint (function-based)
    path('api/stats/', stats_view, name='stats'),
]

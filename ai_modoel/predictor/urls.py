from django.urls import path
from .views import (
    ResolveMergeConflictView,
    BatchResolveMergeConflictView,
    HealthCheckView
)

urlpatterns = [
    path('resolve/', ResolveMergeConflictView.as_view(), name='resolve-conflict'),
    path('resolve/batch/', BatchResolveMergeConflictView.as_view(),
         name='batch-resolve'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]

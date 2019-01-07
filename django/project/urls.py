from django.contrib import admin
from django.urls import path

import cluster.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', cluster.views.ClusterAPIView.as_view())
]

from django.contrib import admin
from django.urls import path

import cluster.apis

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', cluster.apis.ListCluster.as_view()),
    path('api/<int:pk>', cluster.apis.DetailCluster.as_view()),
]

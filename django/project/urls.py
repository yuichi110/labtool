from django.contrib import admin
from django.urls import path

import cluster.apis

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cluster/', cluster.apis.ListCluster.as_view()),
    path('api/cluster/<int:pk>', cluster.apis.DetailCluster.as_view()),
]
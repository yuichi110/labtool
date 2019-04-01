from django.contrib import admin
from django.urls import path

from asset.apis import AssetApi
from segment.apis import SegmentApi
from cluster.apis import ClusterApi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/assets', AssetApi.assets),
    path('api/assets/', AssetApi.assets),
    path('api/assets/<str:uuid>', AssetApi.asset),

    path('api/segments', SegmentApi.segments),
    path('api/segments/', SegmentApi.segments),
    path('api/segments/<str:uuid>', SegmentApi.segment),

    path('api/clusters', ClusterApi.clusters),
    path('api/clusters/', ClusterApi.clusters),
    path('api/clusters/<str:uuid>', ClusterApi.cluster),
    
    path('test', ClusterApi.test),
]
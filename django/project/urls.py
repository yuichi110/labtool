from django.contrib import admin
from django.urls import path

from asset.apis import AssetApi
from segment.apis import SegmentApi
from cluster.apis import ClusterApi
from operation.apis import OperationApi
from task.apis import TaskApi

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/assets', AssetApi.assets),
    path('api/assets/', AssetApi.assets),
    path('api/assets/<str:uuid>', AssetApi.asset),

    path('api/segments', SegmentApi.segments),
    path('api/segments/', SegmentApi.segments),
    path('api/segments/<str:uuid>', SegmentApi.segment),

    path('api/foundationvms', SegmentApi.foundationvms),
    path('api/foundationvms/', SegmentApi.foundationvms),
    path('api/foundationvms/<str:segment_uuid>', SegmentApi.foundationvm),

    path('api/clusters', ClusterApi.clusters),
    path('api/clusters/', ClusterApi.clusters),
    path('api/clusters/<str:uuid>', ClusterApi.cluster),

    path('api/operations/foundation', OperationApi.foundation),
    path('api/operations/foundation/', OperationApi.foundation),

    path('api/tasks', TaskApi.tasks),
    path('api/tasks/', TaskApi.tasks),
    path('api/tasks/<str:uuid>', TaskApi.task),
    
    path('test', ClusterApi.test),
]
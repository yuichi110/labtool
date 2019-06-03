from django.contrib import admin
from django.urls import path

from cluster.views import IndexView
from asset.apis import AssetApi
from segment.apis import SegmentApi
from cluster.apis import ClusterApi
from playbook.apis import PlaybookApi
from operation.apis import OperationApi
from task.apis import TaskApi

urlpatterns = [
    path('', IndexView.as_view(), name='home'),

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
    path('api/cluster_status/<str:uuid>', ClusterApi.cluster_status),

    path('api/playbooks/', PlaybookApi.playbooks),
    path('api/playbooks/<str:uuid>', PlaybookApi.playbook),

    path('api/operations/foundation/<str:uuid>', OperationApi.foundation),
    path('api/operations/start/<str:uuid>', OperationApi.start),
    path('api/operations/stop/<str:uuid>', OperationApi.stop),
    path('api/operations/run_playbook/<str:uuid>', OperationApi.run_playbook),

    path('api/tasks', TaskApi.tasks),
    path('api/tasks/', TaskApi.tasks),
    path('api/tasks/<str:uuid>', TaskApi.task),
    path('api/task_status/<str:uuid>', TaskApi.task_status),
    
    path('test', ClusterApi.test),
]
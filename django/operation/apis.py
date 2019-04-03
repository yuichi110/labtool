from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers import serialize

from rest_framework import generics
from cluster.models import Cluster
from task.models import Task

from uuid import UUID
import json

from background_tasks import FoundationTask

class OperationApi:

  @classmethod
  def foundation(cls, request):
    if request.method not in ['POST']:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      json_text = request.body.decode()
      d = json.loads(json_text)
      cluster_uuid = d['cluster_uuid']
      aos_image = d['aos_image']
      hypervisor_type = d['hypervisor_type']
      if hypervisor_type != 'ahv':
        hypervisor_image = d['hypervisor_image']
      else:
        hypervisor_image = ''
    except:
      response_body = json.dumps({'error':"request body has problem"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      UUID(cluster_uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    if hypervisor_type not in ['ahv', 'esx', 'hyperv']:
      response_body = json.dumps({'error':"unsupported hypervisor type"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    clusters = Cluster.objects.filter(uuid=cluster_uuid)
    if len(clusters) == 0:
      response_body = json.dumps({'error':'cluster object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    task = Task.objects.create(name='foundation task for cluster', data='{}')
    try:
      ftask = FoundationTask(str(task.uuid), clusters[0].data(),
       aos_image, hypervisor_type, hypervisor_image)
      ftask.daemon = True
    except:
      task.is_complete = True
      
    ftask.start()

    return HttpResponse('{}', content_type='application/json')
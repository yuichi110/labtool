from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers import serialize

from rest_framework import generics
from cluster.models import Cluster

from uuid import UUID
import json

class OperationApi:

  @classmethod
  def foundation(cls, request, uuid):
    try:
      UUID(uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')
    if len(Cluster.objects.filter(uuid=uuid)) == 0:
      response_body = json.dumps({'error':'object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    if request.method not in ['GET', 'POST']:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    return HttpResponse('{}', content_type='application/json')
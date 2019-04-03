from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers import serialize

from rest_framework import generics

from background_task import background
from uuid import UUID
import json
from .models import Task

class TaskApi:

  @classmethod
  def tasks(cls, request):
    if request.method != 'GET':
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    task_objects = Task.objects.all()
    task_list = [task_object.get_dict() for task_object in task_objects]
    response_body = json.dumps(task_list, indent=2)
    return HttpResponse(response_body, content_type='application/json')

  @classmethod
  def task(cls, request, uuid):
    def get(request, task_object):
      response_body = json.dumps(task_object.get_dict(), indent=2)
      return HttpResponse(response_body, content_type='application/json')
    
    def delete(request, task_object):
      task_object.delete()
      return HttpResponse('{}', content_type='application/json')

    # validation
    try:
      UUID(uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')
    task_objects = Task.objects.filter(uuid=uuid)
    if len(task_objects) == 0:
      response_body = json.dumps({'error':'object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    if request.method == 'GET':
      return get(request, task_objects[0])
    elif request.method == 'DELETE':
      return delete(request, task_objects[0])
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

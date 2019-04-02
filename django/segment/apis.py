from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from rest_framework import generics
from .models import Segment

from background_task import background
from uuid import UUID
import json

class SegmentApi:

  @classmethod
  def segments(cls, request):
    def get(request):
      segment_objects = Segment.objects.all()
      segment_list = [json.loads(segment_object.data) for segment_object in segment_objects]
      response_body = json.dumps(segment_list, indent=2)
      return HttpResponse(response_body, content_type='application/json')
    
    def post(request):
      try:
        json_text = request.body.decode()
        data = Segment.create(json_text)
      except Exception as e:
        print(e)
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')
      return HttpResponse(data, content_type='application/json')

    if request.method == 'GET':
      return get(request)
    elif request.method == 'POST':
      return post(request)
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

  @classmethod
  def segment(cls, request, uuid):
    def get(request, uuid):
      segment_object = Segment.objects.filter(uuid=uuid)[0]
      response_body = segment_object.data
      return HttpResponse(response_body, content_type='application/json')

    def put(request, uuid):
      try:
        json_text = request.body.decode()
        Segment.update(uuid, json_text)
      except Exception as e:
        print(e)
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')
      return HttpResponse(segment_object.data, content_type='application/json')
    
    def delete(request, uuid):
      segment_object = Segment.objects.filter(uuid=uuid)[0]
      segment_object.delete()
      return HttpResponse('{}', content_type='application/json')

    # validation
    try:
      UUID(uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')
    if len(Segment.objects.filter(uuid=uuid)) == 0:
      response_body = json.dumps({'error':'object not found'.format(request.method)}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    if request.method == 'GET':
      return get(request, uuid)
    elif request.method == 'PUT':
      return put(request, uuid)
    elif request.method == 'DELETE':
      return delete(request, uuid)
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

  @classmethod
  def update_status(cls, request):
    @background(queue='queue_name1', schedule=0)
    def some_long_duration_process(some_param1, some_param2):
      print('hello world')

    return HttpResponse('{"status":"ok"}')

  @classmethod
  def test(cls, request):
    some_long_duration_process('a', 'b')

    response_body = json.dumps({'aaa':'bbb'}, indent=2)
    return HttpResponse(response_body, content_type='application/json')

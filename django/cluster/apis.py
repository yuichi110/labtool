from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from rest_framework import generics
from .models import Cluster

from asset.models import Asset
from segment.models import Segment

from background_task import background
from uuid import UUID
import json

class ClusterApi:

  @classmethod
  def cluster_status(cls, request, uuid):
    if request.method != 'PUT':
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      cluster = Cluster.objects.get(uuid=uuid)
    except:
      response_body = json.dumps({'error':"cluster not found"}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    try:
      text = request.body.decode()
      d = json.loads(text)
    except:
      response_body = json.dumps({'error':"cluster not found"}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    print(text)
    cluster.status = text
    cluster.save()

    return HttpResponse('{}', content_type='application/json')
    
  @classmethod
  def clusters(cls, request):
    def get(request):
      cluster_objects = Cluster.objects.all()
      cluster_list = []
      for cluster_object in cluster_objects:
        '''
        asset = cluster_object.asset
        segment = cluster_object.segment
        d = json.loads(asset.data)
        d['uuid'] = str(cluster_object.uuid)
        d['asset_uuid'] = str(asset.uuid)
        d['segment_uuid'] = str(segment.uuid)
        '''
        cluster_list.append(cluster_object.data())
      response_body = json.dumps(cluster_list, indent=2)
      return HttpResponse(response_body, content_type='application/json')
    
    def post(request):
      try:
        text = request.body.decode()
        d = json.loads(text)
        asset_uuid = d['asset']
        print('asset uuid: ' + asset_uuid)
        if len(Asset.objects.filter(uuid=asset_uuid)) == 0:
          response_body = json.dumps({'error':'asset object not found'}, indent=2)
          return HttpResponseBadRequest(response_body, content_type='application/json')
        segment_uuid = d['segment']
        print('segment uuid: ' + segment_uuid)
        if len(Segment.objects.filter(uuid=segment_uuid)) == 0:
          response_body = json.dumps({'error':'segment object not found'}, indent=2)
          return HttpResponseBadRequest(response_body, content_type='application/json')
        cluster_object = Cluster.objects.create(
          asset=Asset.objects.filter(uuid=asset_uuid)[0], 
          segment=Segment.objects.filter(uuid=segment_uuid)[0]
        )
      except Exception as e:
        print(e)
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')
      d = {
        'uuid' : str(cluster_object.uuid),
        'asset_uuid' : asset_uuid,
        'segment_uuid' : segment_uuid
      }
      return HttpResponse(json.dumps(d, indent=2), content_type='application/json')

    if request.method == 'GET':
      return get(request)
    elif request.method == 'POST':
      return post(request)
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

  @classmethod
  def cluster(cls, request, uuid):
    def get(request, uuid):
      cluster_object = Cluster.objects.filter(uuid=uuid)[0]
      response_body = json.dumps(cluster_object.data(), indent=2)
      return HttpResponse(response_body, content_type='application/json')

    def put(request, uuid):
      try:
        text = request.body.decode()
        d = json.loads(text)
        Cluster.dict2object(d, uuid)
      except Exception as e:
        print(e)
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')
      d = {
        'uuid' : str(cluster_object.uuid),
        'asset_uuid' : asset_uuid,
        'segment_uuid' : segment_uuid
      }
      return HttpResponse(json.dumps(d, indent=2), content_type='application/json')
    
    def delete(request, uuid):
      cluster_object = Cluster.objects.filter(uuid=uuid)[0]
      cluster_object.delete()
      return HttpResponse('{}', content_type='application/json')

    # validation
    try:
      UUID(uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')
    if len(Cluster.objects.filter(uuid=uuid)) == 0:
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
    return HttpResponse('{"status":"ok"}')

  @classmethod
  def test(cls, request):
    some_long_duration_process('a', 'b')

    response_body = json.dumps({'aaa':'bbb'}, indent=2)
    return HttpResponse(response_body, content_type='application/json')

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.core.serializers import serialize

from rest_framework import generics
from .models import Asset

from background_task import background
from uuid import UUID
import json

class AssetApi:

  @classmethod
  def assets(cls, request):
    def get(request):
      asset_objects = Asset.objects.all()
      asset_list = [json.loads(asset_object.data) for asset_object in asset_objects]
      response_body = json.dumps(asset_list, indent=2)
      return HttpResponse(response_body, content_type='application/json')
    
    def post(request):
      try:
        text = request.body.decode()
        d = json.loads(text)
        name = d['name']
        asset_object = Asset.objects.create(name=name, data='')
        d['uuid'] = str(asset_object.uuid)
        asset_object.data = json.dumps(d, indent=2)
        asset_object.save()
      except Exception as e:
        print(e)
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')
      return HttpResponse(asset_object.data, content_type='application/json')

    if request.method == 'GET':
      return get(request)
    elif request.method == 'POST':
      return post(request)
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

  @classmethod
  def asset(cls, request, uuid):
    def get(request, uuid):
      asset_object = Asset.objects.filter(uuid=uuid)[0]
      response_body = asset_object.data
      return HttpResponse(response_body, content_type='application/json')

    def put(request, uuid):
      try:
        asset_object = Asset.objects.filter(uuid=uuid)[0]
        text = request.body.decode()
        d = json.loads(text)
        d['uuid'] = str(asset_object.uuid)
        asset_object.name = d['name']
        asset_object.data = json.dumps(d, indent=2)
        asset_object.save()
      except Exception as e:
        print(e)
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')
      return HttpResponse(asset_object.data, content_type='application/json')
    
    def delete(request, uuid):
      asset_object = Asset.objects.filter(uuid=uuid)[0]
      asset_object.delete()
      return HttpResponse('{}', content_type='application/json')

    # validation
    try:
      UUID(uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')
    if len(Asset.objects.filter(uuid=uuid)) == 0:
      response_body = json.dumps({'error':'object not found'}, indent=2)
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

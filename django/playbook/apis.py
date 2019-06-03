from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from .models import Playbook

import json

class PlaybookApi:

  @classmethod
  def playbooks(cls, request):
    def post(request):
      try:
        text = request.body.decode()
        d = json.loads(text)
        name = d['name']
        body = d['body']
        book = Playbook.objects.create(name=name, body=body)

        response_body = json.dumps(book.data(), indent=2)
        return HttpResponse(response_body, content_type='application/json')
      except:
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')

    def get(request):
      book_list = [book.data() for book in Playbook.objects.all()]
      response_body = json.dumps(book_list, indent=2)
      return HttpResponse(response_body, content_type='application/json')

    if request.method == 'GET':
      return get(request)
    elif request.method == 'POST':
      return post(request)
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

  @classmethod
  def playbook(cls, request, uuid):

    def get(request, book):
      response_body = json.dumps(book.data(), indent=2)
      return HttpResponse(response_body, content_type='application/json')

    def put(request, book):
      try:
        text = request.body.decode()
        d = json.loads(text)
        if 'name' in d:
          book.name = d['name']
        if 'body' in d:
          book.body = d['body']
        book.save()

        response_body = json.dumps(book.data(), indent=2)
        return HttpResponse(response_body, content_type='application/json')
      except:
        response_body = json.dumps({'error':"request body has problem"}, indent=2)
        return HttpResponseBadRequest(response_body, content_type='application/json')

    def delete(request, book):
      book.delete()
      return HttpResponse('{}', content_type='application/json')

    try:
      book = Playbook.objects.get(uuid=uuid)
    except:
      response_body = json.dumps({'error':'object not found'.format(request.method)}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    if request.method == 'GET':
      return get(request, book)
    elif request.method == 'PUT':
      return put(request, book)
    elif request.method == 'DELETE':
      return delete(request, book)
    else:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')
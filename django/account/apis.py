from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

class AccountApi:

  @classmethod
  def login(cls, request):
    return HttpResponse(response_body, content_type='application/json')

  @classmethod
  def logout(cls, request):
    return HttpResponse(response_body, content_type='application/json')

  def users(cls, request):
    # get
    # post
    return HttpResponse(response_body, content_type='application/json')

  def user(cls, request):
    # get
    # put
    # delete
    return HttpResponse(response_body, content_type='application/json')
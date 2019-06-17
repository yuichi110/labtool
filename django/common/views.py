from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from bs4 import BeautifulSoup

def index(request):
  rendered = render_to_string('index.html')
  soup = BeautifulSoup(rendered, 'html.parser') 
  html = soup.prettify()
  return HttpResponse(html, 'text/html; charset=utf-8')

def others(request, exception):
  return redirect('/')
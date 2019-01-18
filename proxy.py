# Proxy for local run
# Please use nginx for production

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request, urllib.error

BACKEND_PORT = 8000
FRONTEND_PORT = 8080
BACKEND_PREFIXS = ['/api', '/admin', '/static/admin']

# Handler for avoid 302 redirection on urllib Request.
class NoRedirectProcessor(urllib.request.HTTPErrorProcessor):
  def http_response(self, request, response):
    return response
  https_response = http_response
  
class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
  def do_GET(self, method='GET'):

    # check whether frontend or backend
    port = FRONTEND_PORT
    is_backend = False
    for prefix in BACKEND_PREFIXS:
      if self.path.startswith(prefix):
        is_backend = True
    if is_backend:
      port = BACKEND_PORT

    # check request headers
    header_dict = {}
    for key in self.headers:
      header_dict[key] = self.headers.get(key)

    # check request body
    content_len = self.headers.get('Content-Length')
    if content_len is None:
      content_len = 0
    else:
      content_len = int(content_len)
      body = self.rfile.read(content_len)

    # make request to server
    url = 'http://localhost:{}{}'.format(port, self.path)
    if content_len == 0:
      req = urllib.request.Request(url=url, method=method, headers=header_dict)
    else:
      req = urllib.request.Request(url=url, method=method, headers=header_dict, data=body)

    # build opener which avoid redirect
    opener = urllib.request.build_opener(NoRedirectProcessor)

    # access to server and get response
    try:
      resp = opener.open(req)
    except urllib.error.HTTPError as e:
      if e.getcode():
        resp = e
      else:
        self.send_error(599, u'error proxying: {}'.format(unicode(e)))
        return

    # response code
    self.send_response(resp.getcode())

    # response header
    respheaders = resp.info()
    print('=== RESPONSE HEADER ===')
    for line in respheaders.as_string().splitlines():
      print(line)
      line_parts = line.split(':', 1)
      if len(line_parts) == 2:
        self.send_header(*line_parts)
    self.end_headers()
    print()

    # response body
    self.wfile.write(resp.read())
    return

  def do_POST(self):
    self.do_GET(method='POST')

  def do_PUT(self):
    self.do_GET(method='PUT')

  def do_DELETE(self):
    self.do_GET(method='DELETE')

  def do_HEAD(self):
    self.do_GET(method='HEAD')

  def do_OPTIONS(self):
    self.do_GET(method='OPTIONS')


httpd = HTTPServer(('127.0.0.1', 80), ProxyHTTPRequestHandler)
print('Python http proxy is running http://127.0.0.1/')
httpd.serve_forever()
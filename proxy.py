# Proxy for local run
# Please use nginx for production

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request, urllib.error

BACKEND_PORT = 8000
FRONTEND_PORT = 8080
BACKEND_PREFIXS = ['/api', '/admin', '/static/admin']

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

    # make request to server
    url = 'http://localhost:{}{}'.format(port, self.path)
    req = urllib.request.Request(url=url)


    # TESTING URLLIB NOW TO IMPLEMENT POST PORXY ETC.
    content_len = self.headers.get('Content-Length')
    if content_len is None:
      content_len = 0
    else:
      content_len = int(content_len)
      body = self.rfile.read(content_len)


    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write('OK'.encode())
    return
    # END TESTING


    # access to server
    try:
      resp = urllib.request.urlopen(req)
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
    for line in respheaders.as_string().splitlines():
      line_parts = line.split(':', 1)
      if len(line_parts) == 2:
        self.send_header(*line_parts)
    self.end_headers()

    # response body
    self.wfile.write(resp.read())
    return

  def do_POST(self):
    self.do_GET(method='POST')

httpd = HTTPServer(('127.0.0.1', 80), ProxyHTTPRequestHandler)
print('Python http proxy is running http://127.0.0.1/')
httpd.serve_forever()
# Proxy for local run
# Please use nginx for production

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request, urllib.error

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
  def do_GET(self, body=True):
    if self.path.startswith('/api'):
      # go to app server (django)
      port = 8000
    else:
      # go to web server (vue)
      port = 8080

    url = 'http://localhost:{}{}'.format(port, self.path)
    req = urllib.request.Request(url=url)
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

httpd = HTTPServer(('127.0.0.1', 80), ProxyHTTPRequestHandler)
print('Python http proxy is running http://127.0.0.1/')
httpd.serve_forever()
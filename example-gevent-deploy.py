from gevent.pywsgi import WSGIServer
from app import app

http_server = WSGIServer(('', 8080), app)
http_server.serve_forever()

from gevent.pywsgi import WSGIServer
from app import app

app.config['SERVER_NAME'] = 'http://game.ss13.moe/stats'

http_server = WSGIServer(('', 8080), app)
http_server.serve_forever()

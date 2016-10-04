from gevent.pywsgi import WSGIServer
from app import app
import logging
from logging.handlers import RotatingFileHandler

from gevent import monkey
monkey.patch_all()

ourLog = logging.getLogger('gevent.log')
ourLog.setLevel(logging.DEBUG)
logHandler = RotatingFileHandler('statsserv_gevent_log.txt', maxBytes = 100000, backupCount = 1)

ourELog = logging.getLogger('gevent.log')
ourELog.setLevel(logging.DEBUG)
elogHandler = RotatingFileHandler('statsserv_gevent_log.txt', maxBytes = 100000, backupCount = 1)

ourLog.addHandler(logHandler)
ourELog.addHandler(elogHandler)

http_server = WSGIServer(('', 8080), app, log = ourLog, error_log = ourELog)
http_server.serve_forever()

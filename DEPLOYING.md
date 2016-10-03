# Deploying via Gunicorn Reverse Proxy Setup
These instructions are for setting up Apache to retrieve pages from Gunicorn in order to workaround mod_wsgi not working.
Note that **Gunicorn does not work on Windows** at the time of writing (October 3rd, 2016).

For nginx instructions refer to [Gunicorn's example](http://gunicorn.org/#deployment).

## Installing Gunicorn
`pip install gunicorn`

## Running Gunicorn
On Linux, make a .sh with:
```bash
#!/bin/bash
gunicorn -w 1 app:app -b 0.0.0.0:8080
```
More information on configuring Gunicorn can be found [in the documentation for Gunicorn](http://docs.gunicorn.org/en/stable/settings.html).

## Configuring Apache
We'll need to specify the directory for the `static` resources so that images and such work correctly, and are served by Apache instead of Gunicorn.
```apache
<VirtualHost oursite.com>

  # Tells apache where /static/ should go
  Alias /static/ /full/path/to/flask/app/static/

  # Proxy everything to gunicorn EXCEPT /static and favicon.ico
  ProxyPass /favicon.ico !
  ProxyPass /static !
  ProxyPass /stats http://oursite.com:8080/
  ProxyPassReverse /stats http://oursite.com:8080/

</VirtualHost>
```

Once this is set up, asssuming Gunicorn is running, browsing to `http://oursite.com/stats` should serve this app via Gunicorn.

# Deploying on Windows via Gevent
Since Gunicorn doesn't work for Windows, here's how to do the above with Gevent:
```
pip install gevent
```

## Running Gevent
Make a new python script at the root of the project folder.
```python
from gevent.wsgi import WSGIServer
from app import app

http_server = WSGIServer(('', 8080), app)
http_server.serve_forever()
```
For instructions on configuring the Apache reverse proxy, [see above](#Configuring Apache).
Note: For some reason, gevent didn't work properly and I couldn't load `gevent.pywsgi`. If you know why this is, let me know.
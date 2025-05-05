"""
WSGI config for rejestrskladek project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rejestrskladek.settings')

application = get_wsgi_application()

"""
def application(environ, start_response):
    status = '200 OK'
    output = ""
    for k, v in environ.items():
        output += "'" + str(k) + "': '" + str(v) + "'                 "

    output = bytes(output, "utf-8")
    #output = environ['wsgi.input'].read()

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
"""

"""
WSGI config for untitled project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, '/opt/python/current/app/BubbleUpServer')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BubbleUpServer.settings")

from django.core.wsgi import get_wsgi_application
from scheduled import scheduler

application = get_wsgi_application()

scheduler.start()

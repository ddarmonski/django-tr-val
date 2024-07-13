"""
WSGI config for InvoiceValidator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys  
import logging  

from django.core.wsgi import get_wsgi_application
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvoiceValidator.settings')

application = get_wsgi_application()

"""
ASGI config for sport_parser project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import sport_parser.khl.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sport_parser.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': URLRouter(sport_parser.khl.routing.websocket_urlpatterns)
})

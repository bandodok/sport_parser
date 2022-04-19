from django.urls import path
from sport_parser.core import consumers

websocket_urlpatterns = [
    path('ws/update_protocol', consumers.UpdateProtocolConsumer.as_asgi()),
]

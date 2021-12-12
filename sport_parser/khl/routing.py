from django.urls import path
from sport_parser.khl import consumers


websocket_urlpatterns = [
    path('ws/update_protocol', consumers.UpdateProtocolConsumer.as_asgi()),
]

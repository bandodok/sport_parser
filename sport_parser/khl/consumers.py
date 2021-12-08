from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class UpdateProtocolConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'update', self.channel_name
        )
        self.accept()

    def disconnect(self, close_data):
        async_to_sync(self.channel_layer.group_discard)(
            'update', self.channel_name
        )

    def update_update(self, event):
        self.send(text_data=event['text'])

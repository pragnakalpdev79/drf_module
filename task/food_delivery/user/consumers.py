from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime

class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'orders_{self.room_name}'
        # Get the authenticated user
        self.user = self.scope['user']
        # Reject anonymous users
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return 
        # Join the room group
        # This registers our channel to receive group broadcasts
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()



    async def disconnect(self, close_code):
        print(f"Connection closed with code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data ):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
            


    async def send_notification(self,event):
        notification = event['message']

        await self.send(text_data=json.dumps({
            'notification' : notification
        }))

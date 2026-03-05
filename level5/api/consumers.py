from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'tasks'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receiver(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'task_message',
                'message': message
            }
        )

    async def task_message(self,event):
        message = event['message']
        await self.send(text_data=json.dumps(
            {'message': message}
        ))
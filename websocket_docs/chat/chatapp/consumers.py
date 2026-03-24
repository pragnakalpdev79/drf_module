import json
from django.contrib.auth.models import AnonymousUser
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Connecting to websocket!!------------")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "testing"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print("intiated")
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        print("====================================================")
        print("====================================================")
        print("====================================================")
        print("====================================================")
        print("disconnecting")
        print("====================================================")
        print("====================================================")
        print("====================================================")
        print("====================================================")
        await self.channel_layer.group_discard(self.room_group_name,
                                                self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print("---------message recieved----------")
        print(message)

        # Send message to room group
        print("calling the chatmessage function")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message" : message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        print("inside chat message function")
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

# # api/consumers.py
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# class TaskConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = 'tasks'
        
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         await self.accept()
    
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
    
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
        
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'task_message',
#                 'message': message
#         })
    
#     async def task_message(self, event):
#         message = event['message']
        
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))
# chat/views.py
from django.shortcuts import render
from websockets.exceptions import ConnectionClosed
from rest_framework import status,viewsets
from rest_framework.decorators import action
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
import asyncio
import websockets
import ssl
import json

# async def producer_handler(websocket):
#     while True:
#         try:
#             message = await produce()



def index(request):
    return render(request, "chatapp/index.html")

def room(request,room_name):
    channel_layer = get_channel_layer()
    print("1.chanel-layer---- >   ",channel_layer)
    #print(channel_layer.group)
    return render(request,"chatapp/room.html",{
        "room_name" : room_name
    })

async def hello():
    async with websockets.connect('ws://127.0.0.1:8000/ws/chatapp/orders/', close_timeout=500) as websocket:
        message = 'weird'
        data = {
                "type": "chat.message",
                "message" : message
            }
        await websocket.send(json.dumps(data))

        print(f"sent data {data}" )


@api_view(('GET',))
def test(request):
    channel_layer = get_channel_layer()
    print("2.chanel-layer---- >   ",channel_layer)
    tv = async_to_sync(channel_layer.send)(
           'testing',
            {
                'type': 'chat.message',
                'message': 'New task created'
            }
        )
    print(tv)
    print("message sent!")
    #asyncio.get_event_loop().run_until_complete(hello())
    #async_to_sync(hello)
    asyncio.run(hello())
    return Response({
        "message": "worked"
    })


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from chat.models import Clients


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anon_channel_name = None

    async def connect(self):
        await self.accept()
        await self.add_user()

        # Let a worker do the searching in the background
        await self.channel_layer.send("find-interlocutor", {
            "type": "init.receive",
            "channel": self.channel_name,
        })
        print(self.scope["session"])

    async def disconnect(self, close_code):
        print(close_code)
        await self.delete_user()

        # If channel was connected
        if self.anon_channel_name:
            # Notify another channel about disconnection
            await self.channel_layer.send(self.anon_channel_name, {
                "type": "send.json",
                "action": "close",
                "message": "Connection closed"
            })

            await self.channel_layer.send(self.anon_channel_name, {
                "type": "close.connection",
                "code": 1000
            })

    async def receive(self, text_data):
        # Send data to my and anon's channels
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to current channel
        await self.channel_layer.send(self.channel_name, {
            "type": "send.json",
            "user": "me",
            "action": "chat",
            "message": message
        })

        # Send message to interlocutor's channel
        await self.channel_layer.send(self.anon_channel_name, {
            "type": "send.json",
            "user": "anon",
            "action": "chat",
            "message": message
        })

    async def send_json(self, event):
        action = event["action"]
        message = event["message"]

        if action == "close":
            await self.send(text_data=json.dumps(
                {
                    "type": "close",
                    "message": message
                }
            ))
        elif action == "chat":
            user = event["user"]

            await self.send(text_data=json.dumps(
                {
                    "type": "chat",
                    "user": user,
                    "message": message
                }
            ))

    async def get_anon_channel_name(self, event):
        self.anon_channel_name = event["anon_channel_name"]

        # Saving anon name in session in order to reconnect
        # if this channel lose connection
        self.scope["session"]["anon_channel_name"] = self.anon_channel_name
        sync_to_async(self.scope["session"].save)()
        print(self.scope["session"]["anon_channel_name"])

    async def close_connection(self, event):
        code = event.get("code", None)
        await self.close(code)

    # Database queries, decorated for asynchronous purposes
    @database_sync_to_async
    def add_user(self):
        Clients.objects.create(channel_name=self.channel_name, is_busy=False, anon_channel_name=None)

    @database_sync_to_async
    def delete_user(self):
        Clients.objects.get(channel_name=self.channel_name).delete()

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Channel, Group
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.connected = False
        self.session_updated = False

    async def connect(self):
        await self.accept()
        await self.add_user()

        await self.reconnect_to_group()

        if not self.connected:
            # Let a worker do the searching in the background
            await self.channel_layer.send("find-interlocutor", {
                "type": "init.receive",
                "channel": self.channel_name,
            })

    async def reconnect_to_group(self):
        self.group_name = await sync_to_async(self.scope["session"].get)("group_name")

        if self.group_name:
            group_exists = await self.is_group_exists(self.group_name)
            
            if not group_exists:
                return

            await self.restore_connection(self.channel_name, self.group_name)
            await self.connect_to_group(self.group_name)

    async def disconnect(self, close_code):
        # Remove from database
        await self.delete_user()

        # If channel was connected
        if self.group_name:
            # Remove this channel from the group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

            # await self.channel_layer.send(self.anon_channel_name, {
            #     "type": "close.connection",
            #     "code": 1000
            # })

    async def receive(self, text_data):
        if not self.connected:
            return None

        # Send data all channels in the group
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to current channel
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send.json",
                "action": "chat",
                "user": self.channel_name,
                "message": message
            }
        )

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

    async def get_data(self, event):
        self.group_name = event["group_name"]

        await self.connect_to_group(self.group_name)

    async def connect_to_group(self, group_name):
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        self.connected = True

        if not self.session_updated:
            await self.update_session(group_name)

    async def update_session(self, group_name):
        self.scope["session"]["group_name"] = group_name
        await sync_to_async(self.scope["session"].save)()
        self.session_updated = True

    async def close_connection(self, event):
        code = event.get("code", None)
        await self.close(code)

    # Database queries, decorated for asynchronous purposes
    @database_sync_to_async
    def add_user(self):
        Channel.objects.create(channel_name=self.channel_name, is_busy=False, group_name=None)

    @database_sync_to_async
    def delete_user(self):
        Channel.objects.get(channel_name=self.channel_name).delete()

    @database_sync_to_async
    def restore_connection(self, channel_name, group_name):        
        group = Group.objects.get(name=group_name)

        cur_channel = Channel.objects.get(channel_name=channel_name)
        cur_channel.is_busy = True
        cur_channel.group_name = group
        cur_channel.save()

    @database_sync_to_async
    def is_group_exists(self, group_name):
        try:
            return Group.objects.get(name=group_name)
        except Channel.DoesNotExist:
            return False

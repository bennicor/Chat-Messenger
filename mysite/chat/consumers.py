import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Channel, Group, MessageLine
from asgiref.sync import sync_to_async
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None
        self.user_id = None
        self.connected = False
        self.session_updated = False

    async def connect(self):
        await self.accept()

        user_session_data = await sync_to_async(self.scope["session"].get)("user_data")
        
        # Get user id which indicates user instance in the chat
        self.user_id = await self.get_user_id(user_session_data)
        await self.add_user()

        if user_session_data:
            await self.reconnect_to_group(user_session_data)

        if not self.connected:
            # Let a worker do the searching in the background
            await self.channel_layer.send("find-interlocutor", {
                "type": "init.receive",
                "channel": self.channel_name,
            })

    async def get_user_id(self, user_session_data):
        # By default user id will be equal to next db entry id
        user_id = await self.get_next_entry_id()

        if user_session_data:
            # if conversastion is still going
            if await self.is_group_exists(user_session_data["group_name"]):
                user_id = user_session_data["user_id"]

        return user_id

    async def reconnect_to_group(self, user_session_data):
        self.group_name = user_session_data["group_name"]

        group_exists = await self.is_group_exists(self.group_name)

        if not group_exists:
            await self.close_connection(
                {
                    "code": 1000
                }
            )

            return

        self.session_updated = True
        await self.restore_connection(self.channel_name, self.group_name, self.user_id)
        await self.load_chat_history()
        await self.connect_to_group(self.group_name)

    async def disconnect(self, close_code):
        if close_code == 3000:
            await self.clear_session()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "close.connection"
                }
            )

        await self.delete_user(self.channel_name)

        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if not self.connected:
            return None

        # Send data to all channels in the group
        text_data_json = json.loads(text_data)
        event_type = text_data_json["type"]
        message = text_data_json["message"]

        if event_type == "message":
            # Add message entry to db
            current_time = datetime.now()
            await self.add_message(message, self.group_name, self.user_id, current_time)
            current_time = current_time.strftime("%H:%M")

            # Send message to current channel
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send.json",
                    "action": "chat",
                    "user_id": self.user_id,
                    "message": message,
                    "time": current_time,
                }
            )
        elif event_type == "typing":
            sender_channel_name = self.channel_name
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send.json",
                    "action": "typing",
                    "message": message,
                    "sender_channel_name": sender_channel_name,
                }
            )

    async def send_json(self, event):
        action = event["action"]
        message = event["message"]

        if action == "chat":
            await self.send(text_data=json.dumps(
                {
                    "type": action,
                    "user_id": event["user_id"],
                    "message": message,
                    "time": event["time"],
                }
            ))
        elif action == "user_data":
            await self.send(text_data=json.dumps(
                {
                    "type": action,
                    "user_id": event["user_id"],
                    "group_name": event["group_name"]
                }
            ))
        elif action == "start":
            await self.send(text_data=json.dumps(
                {
                    "type": action,
                    "message": message
                }
            ))
        elif action == "typing":
            if self.channel_name != event["sender_channel_name"]:
                await self.send(text_data=json.dumps(
                    {
                        "type": action,
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
            await self.update_session(group_name, self.user_id)

            # Send user id to front end client
            await self.send_json(
                {
                    "action": "user_data",
                    "message": "send user data",
                    "user_id": self.user_id,
                    "group_name": self.group_name
                }
            )

        # Send message that everything is ready
        await self.send_json(
            {
                "action": "start",
                "message": "ready"
            }
        )

    async def update_session(self, group_name, user_id):
        self.scope["session"]["user_data"] = {}
        self.scope["session"]["user_data"]["group_name"] = group_name
        self.scope["session"]["user_data"]["user_id"] = user_id
        await sync_to_async(self.scope["session"].save)()

    async def clear_session(self):
        self.scope["session"]["user_data"] = {}
        await sync_to_async(self.scope["session"].save)()

    async def load_chat_history(self):
        group_messages = await self.get_group_messages(self.group_name)
        # Send all the messages to client
        for message in group_messages:
            await self.send_json(
                {
                    "action": "chat",
                    "user_id": message.user_id,
                    "message": message.message,
                    "time": message.time_created.strftime("%H:%M"),
                }
            )

    async def close_connection(self, event):
        code = event.get("code", None)
        await self.clear_session()
        await self.close(code)

    # Database queries, decorated for asynchronous purposes
    @database_sync_to_async
    def add_user(self):
        Channel.objects.create(channel_name=self.channel_name, is_busy=False, group_name=None, user_id=self.user_id)

    @database_sync_to_async
    def delete_user(self, channel_name):
        Channel.objects.get(channel_name=channel_name).delete()

    @database_sync_to_async
    def delete_group(self, group_name):
        Group.objects.get(name=group_name).delete()

    @database_sync_to_async
    def restore_connection(self, channel_name, group_name, unique_id):
        group = Group.objects.get(name=group_name)

        cur_channel = Channel.objects.get(channel_name=channel_name)
        cur_channel.is_busy = True
        cur_channel.group_name = group
        cur_channel.user_id = unique_id
        cur_channel.save()

    @database_sync_to_async
    def is_group_exists(self, group_name):
        try:
            return Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return False

    @database_sync_to_async
    def get_next_entry_id(self):
        try:
            return Channel.objects.last().id + 1
        except AttributeError:
            return 1

    @database_sync_to_async
    def add_message(self, message, group_name, user_id, time_created):
    
        group = Group.objects.get(name=group_name)

        MessageLine.objects.create(message=message, group=group, user_id=user_id, time_created=time_created)

    @database_sync_to_async
    def get_group_messages(self, group_name):
        group = Group.objects.get(name=group_name)

        return list(MessageLine.objects.filter(group=group).all())

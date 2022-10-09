from channels.generic.websocket import AsyncConsumer
from asyncio import sleep
from channels.db import database_sync_to_async
from chat.models import Channel, Group
from random import choice
from chat.utils import generate_group_name


class ConnectionWorker(AsyncConsumer):
    async def init_receive(self, message):
        self.attempts = 10 # 10
        self.cooldown = 3 # 3
        self.anon_channel_name = None
        self.group_name = None
        self.reply_channel = message["channel"]

        await self.find_interlocutor()

    async def find_interlocutor(self):
        # Making a database query until someone is found
        while self.attempts > 0:
            # Check if this channel has been disconnected
            if not await self.get_channel(self.reply_channel):
                return None

            # Check if someone has already connected to this channel
            if await self.is_channel_connected(self.reply_channel):
                return None

            available_channels = await self.get_companion()

            # Connect to random searching channel
            if available_channels:
                self.anon_channel_name = choice(available_channels).channel_name
                
                # Generate random group name for both channels to connect
                self.group_name = generate_group_name()
                await self.create_group(self.group_name)
                await self.send_data(self.reply_channel, self.group_name)
                await self.send_data(self.anon_channel_name, self.group_name)
                break

            self.attempts -= 1
            await sleep(self.cooldown)
        else:
            # If nobody is found close connection
            await self.channel_layer.send(self.reply_channel, {
                "type": "close.connection",
            })
            return None
    
        await self.create_connection(self.reply_channel, self.anon_channel_name, self.group_name)

    async def send_data(self, channel_name, group_name):
        # Send data back to reply channel
        await self.channel_layer.send(channel_name, {
            "type": "get.data",
            "group_name": group_name
        })

    # Database queries, decorated for asynchronous purposes
    @database_sync_to_async
    def get_companion(self):
        return list(Channel.objects.exclude(channel_name=self.reply_channel).filter(is_busy=False))

    @database_sync_to_async
    def is_channel_connected(self, channel_name):
        return Channel.objects.get(channel_name=channel_name).is_busy == 1

    @database_sync_to_async
    def create_connection(self, channel_name, anon_channel_name, group_name):        
        # Change statuses and establish relationship connection
        group = Group.objects.get(name=group_name)
        
        cur_channel = Channel.objects.get(channel_name=channel_name)
        cur_channel.is_busy = True
        cur_channel.group_name = group
        cur_channel.save()

        anon_channel = Channel.objects.get(channel_name=anon_channel_name)
        anon_channel.is_busy = True
        anon_channel.group_name = group
        anon_channel.save()

    @database_sync_to_async
    def create_group(self, group_name):
        Group.objects.create(name=group_name)

    @database_sync_to_async
    def get_channel(self, channel_name):
        try:
            return Channel.objects.get(channel_name=channel_name)
        except Channel.DoesNotExist:
            return False

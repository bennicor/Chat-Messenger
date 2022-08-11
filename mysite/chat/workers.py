from channels.generic.websocket import AsyncConsumer
from asyncio import sleep
from channels.db import database_sync_to_async
from chat.models import Clients
from random import choice


class ConnectionWorker(AsyncConsumer):
    async def init_receive(self, message):
        self.attempts = 10 # 10
        self.cooldown = 3 # 3
        self.anon_channel_name = None
        self.reply_channel = message["channel"]

        await self.find_interlocutor()

    async def find_interlocutor(self):
        # Making a database query until someone is found
        while self.attempts > 0:

            # Check if channel has been disconnected
            if not await self.get_channel(self.reply_channel):
                return None

            available_channels = await self.get_companion()

            # Check if someone has already connected to this channel
            if await self.is_channel_connected():
                self.anon_channel_name = await self.get_anon_channel()
                
                await self.send_anon_channel_name()
                return None

            # Connect to random idle channel
            if available_channels:
                self.anon_channel_name = choice(available_channels).channel_name
                
                await self.send_anon_channel_name()
                break

            self.attempts -= 1
            await sleep(self.cooldown)
        else:
            # If nobody is found close connection
            await self.channel_layer.send(self.reply_channel, {
                "type": "close.connection",
            })
            return None
    
        await self.create_connection(self.reply_channel, self.anon_channel_name)

    async def send_anon_channel_name(self):
        await self.channel_layer.send(self.reply_channel, {
            "type": "get.anon.channel.name",
            "anon_channel_name": self.anon_channel_name,
        })

    # Database queries, decorated for asynchronous purposes
    @database_sync_to_async
    def get_companion(self):
        return list(Clients.objects.exclude(channel_name=self.reply_channel).filter(is_busy=False))

    @database_sync_to_async
    def is_channel_connected(self):
        return Clients.objects.get(channel_name=self.reply_channel).is_busy == 1

    @database_sync_to_async
    def get_anon_channel(self):
        return Clients.objects.get(channel_name=self.reply_channel).anon_channel_name

    @database_sync_to_async
    def create_connection(self, channel_name, anon_channel_name):        
        # Change statuses and establish relationship connection
        cur_channel = Clients.objects.get(channel_name=channel_name)
        cur_channel.is_busy = True
        cur_channel.anon_channel_name = anon_channel_name
        cur_channel.save()

        anon_channel = Clients.objects.get(channel_name=anon_channel_name)
        anon_channel.is_busy = True
        anon_channel.anon_channel_name = channel_name
        anon_channel.save()

    @database_sync_to_async
    def get_channel(self, channel_name):
        try:
            return Clients.objects.get(channel_name=channel_name)
        except Clients.DoesNotExist:
            return False

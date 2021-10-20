import discord
from discord.ext import commands
import database
from constants import *
import time

class AdminCommandsCog(commands.Cog):
    def __init__(self, client: discord.Client):
        super().__init__()
        self.client: discord.Client = client

    @commands.command()
    @commands.is_owner()
    async def update(self, _, collection_name: str, *args):
        if collection_name == 'names':
            if len(args) != 1:
                print(f'Invalid arguments count for "update names": {len(args)}.')
                return
            
            filename = args[0]
            database.update_names(filename)
        else:
            print(f'Invalid collection name: "{collection_name}"')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Admin commands cog attached.')

class UserCommandsCog(commands.Cog):
    def __init__(self, client: discord.Client):
        super().__init__()
        self.client: discord.Client = client

    @commands.command()
    async def kurwa(self, ctx: commands.Context):
        start = time.perf_counter()
        pot_emoji = self.client.get_emoji(DEFAULT_EMOJI_ID)

        kurwa_count = 0
        async for msg in ctx.history(limit=MSG_READ_LIMIT):
            pred_generator = (1 for w in msg.content.lower().split(' ') if w == 'kurwa' and msg.author != self.client.user)
            kurwa_count += sum(pred_generator)

        await ctx.send(f'{pot_emoji} **Kurwa Counter ->** {kurwa_count}')
        elapsed = time.perf_counter() - start
        print(f'Function kurwa ran in {elapsed} seconds')

    @commands.Cog.listener()
    async def on_ready(self):
        print('User commands cog attached.')
    
    def get_message_kurwa_count(self, msg: discord.Message):
        return 
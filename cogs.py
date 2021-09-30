from discord.ext import commands
import discord
import database

class AdminCommandsCog(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client: discord.Client = client
    
    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: commands.Context, collection_name: str, *args):
        if collection_name == 'names':
            if len(args) != 1:
                print(f'Invalid arguments count for "update names": {len(args)}.')
                return
            
            filename = args[0]
            database.update_names(filename)
        elif collection_name == 'images':
            if len(args) == 0:
                print('Command "update images" requires at least one argument.')
                return
                
            for filename in args:
                await self.client.upload_image(filename)
        else:
            print(f'Invalid collection name: "{collection_name}"')
    
    @update.error
    async def update_error(self, ctx: commands.Context, error: Exception):
        print(f'Command "update" errored: {error}.')
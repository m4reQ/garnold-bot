import asyncio
from typing import Any, Dict, List
import discord
from discord.ext import tasks, commands
import datetime
import random
import cogs
import image
import database
import io

DEFAULT_EMOJI_ID: int = 886242957555028018
COMMAND_PREFIX: str = '$'

class BotClient(commands.Bot):
    def __init__(self, server_info: Dict[str, Any]):
        super().__init__(command_prefix=COMMAND_PREFIX)

        self.main_channel_id = server_info['main_channel_id']
        self.image_channel_id = server_info['image_channel_id']
        self.guild_id = server_info['guild_id']
        
        self.names: List[str] = database.get_names()
        self.names_to_use: List[str] = self.names.copy()
        self.names_used: List[str] = []
        self.avatar_emojis: List[discord.Emoji] = []

        self.add_cog(cogs.AdminCommandsCog(self))
        print('Admin commands cog attached.')
    
    def reset_used_names(self) -> None:
        self.names_used.clear()
        self.names_to_use = self.names.copy()
        print('Names list reset.')
    
    async def send_error(self) -> None:
        asyncio.create_task(self.main_channel.send('sie zjebało'))

    async def on_ready(self) -> None:
        self.avatar_emojis = self.get_emojis()
        print(f'{len(self.emojis)} avatar emojis found.')

        self.send_random_names_task.start()
        print('Bot started.')
    
    @tasks.loop(seconds=60)
    async def send_random_names_task(self) -> None:
        date = datetime.datetime.now()

        # at the funny time send something special
        if date.hour == 21 and date.minute == 37:
            await self.send_2137_message()
            return

        # reset used names list at the end of a day
        if date.hour == 0 and date.minute == 0:
            self.reset_used_names()
            return
        
        # don't send anything if it's not a full hour
        if date.minute != 0:
            return
        
        # don't send if during night hours
        if 0 < date.hour < 8:
            print('Sending message cancelled due to night hours.')
            return

        await self.send_random_name()
        print(f'Message sent at {date}.')
    
    async def send_random_name(self) -> None:
        name = random.choice(self.names_to_use)
        pot_emoji = self.get_emoji(DEFAULT_EMOJI_ID)
        avatar_emoji = random.choice(self.avatar_emojis)
        image_url = await self.pick_random_image_url()

        title_str = f'{avatar_emoji} **{name}** :point_right:{pot_emoji}'

        self.names_to_use.remove(name)

        _embed = discord.Embed(title=title_str)
        _embed.set_image(url=image_url)
        
        await self.main_channel.send(embed=_embed)
    
    async def send_2137_message(self) -> None:
        msg = random.choice(['dwie jedynki trzy siódemki', '11777'])
        await self.main_channel.send(msg)
    
    async def pick_random_image_url(self) -> str:
        img_messages = [x.attachments[0].url for x in await self.image_channel.history().flatten()]
        return random.choice(img_messages)

    async def image_exists(self, image_hash: str, channel: discord.TextChannel) -> bool:
        messages = await channel.history().flatten()
        image_messages = filter(self.msg_cotains_img_filter, messages)
        
        for msg in image_messages:
            if image_hash in msg.content:
                return True
        
        return False

    async def on_message(self, msg: discord.Message) -> None:
        if msg.channel != self.image_channel:
            return

        if msg.author == self.user:
            return

        await super().on_message(msg)

        if not self.msg_cotains_img_filter(msg):
            return

        images = [x for x in msg.attachments if x.content_type.startswith('image')]
        
        for img in images:
            buf = io.BytesIO()
            bytes_written = await img.save(buf)

            if bytes_written == 0:
                print(f'Cannot download image "{img.file}".')
                return
            
            _hash = image.hash_image(image.from_file_like(buf))

            await msg.delete()

            if await self.image_exists(_hash, msg.channel):
                print(f'Image "{img.filename}" already uploaded.')
                continue
            
            # return to the beggining of a file
            buf.seek(0)

            img_attachment = discord.File(buf, filename=img.filename)
            await msg.channel.send(content=_hash, file=img_attachment)
            
            buf.close()
            print(f'Image "{img.filename}" uploaded succesfully.')

    def get_emojis(self) -> List:
        emojis = self.guild.emojis
        usable_emojis = list(emojis)

        for e in emojis:
            if e.name != DEFAULT_EMOJI_ID:
                usable_emojis.append(e)

        return usable_emojis
    
    def msg_cotains_img_filter(self, msg: discord.Message) -> bool:
        if not msg.attachments:
            return False
        
        for attachment in msg.attachments:
            if attachment.content_type.startswith('image'):
                return True
        
        return False

    @property
    def guild(self) -> discord.Guild:
        return self.get_guild(self.guild_id)
    
    @property
    def main_channel(self) -> discord.TextChannel:
        return self.get_channel(self.main_channel_id)
    
    @property
    def image_channel(self) -> discord.TextChannel:
        return self.get_channel(self.image_channel_id)
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot

class MessageController(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        '''
        Handle any messages sent by users
        '''
        content = message.content.lower()

        if content == 'hi prism':
            await message.channel.send('Hi there 😊')

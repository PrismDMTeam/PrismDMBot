import os
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot

from cogs.services import SentimentService, LOWER_BOT_NAME, MessageTooLongToAnalyzeError

class MessageController(commands.Cog):
    def __init__(self, bot: Bot, sentiment_service: SentimentService):
        self.bot = bot
        self.sentiment_service = sentiment_service

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        '''
        Handle any messages sent by users
        '''
        if message.author == self.bot.user:
            return

        content = message.content.casefold()

        if content == 'hi prism':
            await message.channel.send('Hi there 😊')
        elif LOWER_BOT_NAME in content:
            await self._on_message_with_prism(message=message)

    async def _on_message_with_prism(self, message: Message):
        '''
        Handle any messages sent by users with the word 'prism' in it
        '''
        try:
            response = self.sentiment_service.query_sentiment(message.content)
        except MessageTooLongToAnalyzeError:
            return

        if response:
            return await message.channel.send(response)


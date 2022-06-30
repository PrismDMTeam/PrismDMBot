from typing import Type
from discord.ext import commands
from discord.ext.commands import Bot, Context, command
from models.base_model import BaseModel

class ModelController(commands.Cog):
    def __init__(self, cls: Type[BaseModel], bot: Bot):
        self.bot = bot
        self.cls = cls

        temp = command(name='temp', parent=self.bot)(self.inner)
        bot.add_command(temp)

    async def inner(self, ctx: Context, potato: str):
        '''
        Hello! This is a temp function. I've got no idea what's going on
        '''
        await ctx.send("This is the inner function called with class " + self.cls.__name__ + " and potato " + potato)
from discord import Embed
from discord.ext.commands import Context
import os

COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')
INFO_COLOR = 0x2ec3f5
ERROR_COLOR = 0xff0000

def info_embed(title: str = None, description: str = None) -> Embed:
    embed = Embed(title=title, description=description, color=INFO_COLOR)
    return embed

def error_embed(title: str = None, description: str = None) -> Embed:
    embed = Embed(title=title, description=description, color=ERROR_COLOR)
    return embed

async def send_guild_only_error(ctx: Context):
    embed = error_embed(title="Sorry! This command is only available in a server", description="I'm looking forward to playing private games in the future 😊")
    return await ctx.send(embed=embed)

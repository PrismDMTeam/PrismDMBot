from discord import Embed
from discord.ext.commands import Context, MissingRequiredArgument
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

async def send_missing_arg_error(ctx: Context, error: MissingRequiredArgument):
    embed = error_embed(title=f"Error! Missing parameter {error.param.name}", description='Sorry bout that, double check you are adding the right key words. Try reading my docs for more help!')
    return await ctx.send(embed=embed)

async def send_generic_error(ctx: Context, error_message: str):
    '''
    Generic error where something has gone terribly wrong
    error_message is only printed to console and not sent to user
    '''
    await ctx.send(embed=error_embed(title='Whoops! 💀', description="Sorry, something has gone terribly wrong! I'll ask my makers to figure out what happend"))
    raise Exception(error_message)


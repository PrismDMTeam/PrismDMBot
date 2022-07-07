from discord import Embed
from discord.ext.commands import Context, MissingRequiredArgument
import os

COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')
INFO_COLOR = 0x2ec3f5
WARNING_COLOR = 0xfcc603
ERROR_COLOR = 0xff0000

WARNING_LOGO_URL = 'https://i.imgur.com/sS9bIWd.png'  # Yellow exclamation mark

def info_embed(title: str = None, description: str = None) -> Embed:
    embed = Embed(title=title, description=description, color=INFO_COLOR)
    return embed

def warning_embed(title: str = None, description: str = None) -> Embed:
    embed = Embed(title=title, description=description, color=WARNING_COLOR)
    embed.set_author(name='Warning!', icon_url=WARNING_LOGO_URL)
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

async def send_generic_error(ctx: Context, error: Exception = None, error_message: str = None):
    '''
    Generic error where something has gone terribly wrong.
    If error is provided, bubble the error up
    If error_message is provided, then raise a new exception with the error. The message is not propogated up to the Discord user
    '''
    await ctx.send(embed=error_embed(title='Whoops! 💀', description="Sorry, something has gone terribly wrong! I'll ask my makers to figure out what happend"))
    
    if error:
        raise error
    elif error_message:
        raise Exception(error_message)


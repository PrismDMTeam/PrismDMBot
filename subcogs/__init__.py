'''
Cogs do not support nesting in other cogs (see https://github.com/Rapptz/discord.py/issues/1816)
This leads to oversized cog files
Workaround is to manually call functions from a POPO from the original cog. Those POPOs are "subcogs"
'''
from .game_channel_controller import *
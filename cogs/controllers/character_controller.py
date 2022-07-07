from discord.ext import commands
from discord.ext.commands import Bot, Context, guild_only
# from cogs.services.character_service import CharacterService # FIXME: Delete
# from cogs.services.game_service import GameService
from cogs.services import GameService, CharacterService
from models.character import Character
from models.game import Game
from util.embed_builder import COMMAND_PREFIX, info_embed, warning_embed, error_embed

class CharacterController(commands.Cog):
    def __init__(self, bot: Bot, game_service: GameService, character_service: CharacterService):
        self.bot = bot
        self.game_service = game_service
        self.character_service = character_service

    @commands.group(aliases=['character'])
    @guild_only()
    async def char(self, ctx: Context):
        '''
        General command for managing characters
        '''
        if ctx.invoked_subcommand is None:
            embed = error_embed(title='Error! Missing subcommand')  # TODO: Upgrade to include rich error message
            return await ctx.send(embed=embed)

    @char.command(name='list', aliases=['ls', 'll'])
    async def list(self, ctx: Context):
        return await ctx.send(embed=error_embed(title='Error, list not implemented yet'))  # FIXME: delete

    @char.command(name='show')
    async def show(self, ctx: Context):
        return await ctx.send(embed=error_embed(title='Error, show not implemented yet'))  # FIXME: delete

    @char.command(name='create')
    async def show(self, ctx: Context):
        return await ctx.send(embed=error_embed(title='Error, create not implemented yet'))  # FIXME: delete

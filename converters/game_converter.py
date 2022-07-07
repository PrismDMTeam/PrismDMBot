from discord import TextChannel
from discord.ext.commands import Bot, Context, Converter, CommandError

from cogs.services import GameService
from models import Game
from util.embed_builder import COMMAND_PREFIX, error_embed

async def send_game_not_found(ctx: Context, name: str):
    '''Send user-friendly error'''
    embed = error_embed(title='Game not found!',
            description='Sorry! We could not find a game with the name **{}**.\nTry `{}game list` to see all available games.'.format(name, COMMAND_PREFIX))
    return await ctx.send(embed=embed)

class GameNotFoundError(CommandError):
    def __init__(self, name: str):
        super().__init__(f'Could not find a game with the name {name}')
        self.name = name

    async def send_error(self, ctx: Context):
        '''Send user-friendly error'''
        return await send_game_not_found(ctx, self.name)

class GameConverter(Converter):
    async def convert(self, ctx: Context, arg: str) -> Game:
        '''
        Fetches the game based on the following order:
        1. By the matching name provided in arg. Raises GameNotFoundError if no game matches arg
        2. By the cahnnel containing this game
        3. By the category containing this game
        '''

        game_service: GameService = ctx.bot.get_cog("GameService")

        # Try searching by name first
        if arg:
            game = game_service.find_by_guild_and_name(guild=ctx.guild, name=arg)
            if game:
                return game
            else:
                raise GameNotFoundError(arg)

        # Try searching by channel
        channel = ctx.channel
        game = game_service.find_by_channel(channel=channel)
        if game:
            return game

        # Fallback to searching by category
        if not isinstance(channel, TextChannel):
            raise CommandError('Expected GameConverter to be used inside guild')

        if channel.category == None:
            return None

        game = game_service.find_by_category(category=ctx.channel.category)
        return game

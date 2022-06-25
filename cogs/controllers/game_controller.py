from doctest import debug_script
from discord.ext import commands
from discord.ext.commands import Context, MissingRequiredArgument, CommandError, guild_only
from typing import List

from pydantic import ValidationError
from cogs.services.game_service import GameService
from models.game import Game
from util.embed_builder import COMMAND_PREFIX, info_embed, error_embed, send_guild_only_error, send_generic_error

class GameController(commands.Cog):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    @commands.group()
    @guild_only()
    async def game(self, ctx: Context):
        '''
        General command for tabletop roleplaying games
        '''
        if ctx.invoked_subcommand is None:
            embed = error_embed(title='Error! Missing subcommand')  # TODO: Upgrade to include rich error message
            return await ctx.send(embed=embed)
    
    @game.command(name='list', aliases=['ls', 'll'])
    async def list(self, ctx: Context):
        '''
        List all games on this server
        '''
        games = self.game_service.find_by_guild(ctx.guild)
        if not games:
            return await self._send_no_games(ctx)
        return await self._send_games_list(ctx, games)

    @game.command(name='show', aliases=['about', 'display'])
    async def show(self, ctx: Context, name: str):
        '''
        Get details about a game
        '''
        game = self.game_service.find_by_guild_and_name(guild=ctx.guild, name=name)
        if not game:
            embed = error_embed(title='Game not found!',
                description='Sorry! We could not find a game with the name **{}**.\nTry `{}game list` to see all available games.'.format(name, COMMAND_PREFIX))
            return await ctx.send(embed=embed)

        created_ts_str = game.created_ts.strftime("%Y-%m-%d %H:%M:%S")
        description = f'_{created_ts_str}_'

        embed = info_embed(title=game.display_name, description=description)
        embed.add_field(name='Type', value=game.type, inline=True)
        embed.set_footer(text=f'ID: {game.pk}')

        return await ctx.send(embed=embed)
            
    @show.error
    async def show_error(self, ctx: Context, error: CommandError):
        if isinstance(error, MissingRequiredArgument):
            embed = error_embed('Error!', f'Missing parameter {error.param.name}')
            embed.add_field(name='Usage:', value=f'`{COMMAND_PREFIX}game show <name>`', inline=False)
            embed.add_field(name='Example:', value=f'`{COMMAND_PREFIX}game show MyAwesomeGame`', inline=False)
            embed.add_field(name='See also:', value=f'Check out `{COMMAND_PREFIX}game list` if you need to find a name of a game', inline=False)
            return await ctx.send(embed=embed)
        else:
            # TODO: figure out how to debug this
            send_generic_error(ctx, f'Unexpected error in show_error command {error}')
            print("Command game show says help! Some totally different error here!", error)
            raise error

    @game.command(name='create', aliases=['add', 'new'])
    async def create(self, ctx: Context, name: str = None):
        '''
        Create a new game with the given name.
        If name is not provided, create a game with the name "Game"
        '''
        try:
            game = self.game_service.create(guild=ctx.guild, game_name=name)
        except ValidationError as error:
            return await self._send_name_length_error(ctx=ctx, name=name, error=error)
            
        name_change_message = None
        if name and game.display_name != name:
            name_change_message = f'The name **{name}** that you asked for was already taken, so I renamed your new game to **{game.display_name}**.' \
                + " Hope that's alright with you 😅"
        
        description = "Bzzt...new game loaded! Just remember, there's no save states here!" if not name_change_message else name_change_message

        embed = info_embed(title=f'Your game {game.display_name} has been created!', description=description)
        embed.set_footer(text=f'ID: {game.pk}')
        await ctx.send(embed=embed)

    @game.command(name='delete', aliases=['del', 'remove'])
    async def delete(self, ctx: Context, name: str):
        '''
        Delete a game. WARNING! Can't be undone
        '''
        # FIXME: Abstract into helper (affects show command)
        game = self.game_service.find_by_guild_and_name(guild=ctx.guild, name=name)
        if not game:
            embed = error_embed(title='Game not found!',
                description='Sorry! We could not find a game with the name **{}**.\nTry `{}game list` to see all available games.'.format(name, COMMAND_PREFIX))
            return await ctx.send(embed=embed)

        # Store variables before game gets deleted
        display_name = game.display_name

        Game.delete(game.pk)
        
        embed = info_embed(title=f'Deleted game {display_name}', description='So long, and thanks for all the fish!')
        return await ctx.send(embed=embed)
        
    async def _send_no_games(self, ctx: Context):
        description_lines = '\n'.join(['Get a game started with:',
            '```',
            f'{COMMAND_PREFIX}game create MyAwesomeGame',
            '```'])
        embed = info_embed(title=f"{ctx.guild.name} doesn't have any games!", description=description_lines)
        embed.set_footer(text="See you real soon, pard'ner")
        await ctx.send(embed=embed)
    
    async def _send_games_list(self, ctx: Context, games: List[Game]):
        # Guild name. Truncate to 20 characters if name is excessively long
        guild_name = ctx.guild.name
        if len(guild_name) > 20:
            guild_name = guild_name[:17] + '...'
        
        num_games = len(games)
        title = f'{guild_name} has {num_games} game{"s" if num_games != 1 else ""}'
        description = 'Type `{}game show <name>` to learn more about a game\n'.format(COMMAND_PREFIX)
        embed = info_embed(title=title, description=description)

        field_name = 'Games:'
        field_value = ''
        footer = None
        for game in games:
            # Check that length of embed does not 6000 character limit (with buffer room for extra text)
            if len(embed) + len(game.display_name) + 4 <= 5930:
                field_value += '- {}\n'.format(game.display_name)
            else:
                # TODO: Wow, that's a lot of games. Add some pagination!
                footer = "Wow that's a lot of games. Delete some with `{COMMAND_PREFIX}game delete <name>`"
                break

        embed.add_field(name=field_name, value=field_value, inline=False)

        if footer:
            embed.set_footer(text=footer)
        
        await ctx.send(embed=embed)

    async def _send_name_length_error(self, ctx: Context, name: str, error: ValidationError):
        errors = error.errors()
        name_too_short_error = next((e for e in errors if 'search_name' in e['loc'] and e['type'] == 'value_error.any_str.min_length'), None)
        name_too_long_error = next((e for e in errors if 'search_name' in e['loc'] and e['type'] == 'value_error.any_str.max_length'), None)

        length_error_text = []
        if name_too_short_error:
            length_error_text = ['short', 'at least', str(name_too_short_error['ctx']['limit_value'])]
        elif name_too_long_error:
            length_error_text = ['long', 'at most', str(name_too_long_error['ctx']['limit_value'])]
        else:
            return await send_generic_error(ctx, 'Expected either name to be too short or name to be too long, instead got errors:\n' + str(error))

        title = f'Error! Your name is too {length_error_text[0]}!'
        description = f'Please change your name **{name}** to be {length_error_text[1]} **{length_error_text[2]}** characters long and try again'
        
        embed = error_embed(title=title, description=description)
        return await ctx.send(embed=embed)

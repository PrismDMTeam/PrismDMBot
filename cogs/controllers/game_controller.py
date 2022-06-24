from doctest import debug_script
from discord.ext import commands
from discord.ext.commands import Context, MissingRequiredArgument, CommandError
from typing import List
from cogs.services.game_service import GameService
from models.game import Game
from util.embed_builder import info_embed, error_embed, send_guild_only_error, COMMAND_PREFIX

class GameController(commands.Cog):
    def __init__(self, game_service: GameService):
        self.game_service = game_service

    @commands.group()
    async def game(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await error_embed(title='Error! Missing subcommand')
            await ctx.send()  # TODO: Upgrade to include rich error message
    
    @game.command()
    async def list(self, ctx: Context):
        games = self.game_service.find_by_guild(ctx.guild)
        if not games:
            await self._send_no_games(ctx)
        await self._send_games_list(ctx, games)

    @game.command(name='show', aliases=['about', 'display'])
    async def show(self, ctx: Context, name: str):
        guild = ctx.guild
        if not guild:
            return await send_guild_only_error()

        game = self.game_service.find_by_guild_and_name(guild=guild, name=name)
        if not game:
            embed = error_embed(title='Game not found!',
                description='Sorry! We could not find a game with the name **{}**.\nTry `{}game list` to see all available games.'.format(name, COMMAND_PREFIX))
            return await ctx.send(embed=embed)

        created_ts_str = game.created_ts.strftime("%Y-%m-%d %H:%M:%S")
        description = f'_{created_ts_str}_'

        embed = info_embed(title=game.display_name, description=description)
        embed.add_field(name='Type', value=game.type, inline=True)
        embed.set_footer(text=game.pk)

        await ctx.send(embed=embed)
            
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
            print("Command game show says help! Some totally different error here!", error)
            raise error


    async def _send_no_games(self, ctx: Context):
        description_lines = '\n'.join('Get a game started with:',
            '```',
            f'{COMMAND_PREFIX}game new MyAwesomeGame',
            '```')
        embed = info_embed(title="You don't have any games!", description=description_lines)
        await ctx.send(embed=embed)
    
    async def _send_games_list(self, ctx: Context, games: List[Game]):
        guild = ctx.guild
        if not guild:
            return await send_guild_only_error()
        
        # Guild name. Truncate to 20 characters if name is excessively long
        guild_name = guild.name
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
import asyncio
from discord import Message, TextChannel, CategoryChannel
from discord import User
from discord import Reaction
from discord.ext import commands
from discord.ext.commands import Bot, Context, MissingRequiredArgument, CommandError, guild_only
from typing import List, Optional

from pydantic import ValidationError
from cogs.services import GameService
from converters import GameConverter, GameNotFoundError, send_game_not_found
from models.game import Game
from subcogs import GameChannelController
from util.embed_builder import COMMAND_PREFIX, info_embed, warning_embed, error_embed, send_generic_error

class GameController(commands.Cog):
    def __init__(self, bot: Bot, game_service: GameService):
        self.bot = bot
        self.game_service = game_service
        self.game_channel_controller = GameChannelController(bot=self.bot, game_service=self.game_service)

    async def cog_after_invoke(self, ctx: Context):
        '''Special function called after all commands in this cog'''
        await self.game_channel_controller.category_after_invoke(ctx)

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
    async def show(self, ctx: Context, game: Optional[GameConverter]):
        '''
        Get details about a game
        '''
        created_ts_str = game.created_ts.strftime("%Y-%m-%d %H:%M:%S")
        description = f'_{created_ts_str}_'

        embed = info_embed(title=game.display_name, description=description)
        embed.add_field(name='Type', value=game.type, inline=True)
        embed.add_field(name='Default in',value='Default game in **{}** channels\nDefault game in **{}** categories'.format(
            len(game.text_channel_ids) if game.text_channel_ids else 0,
            len(game.category_ids) if game.category_ids else 0))
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
            send_generic_error(ctx, error_message=f'Unexpected error in show_error command {error}')
            print("Command game show says help! Some totally different error here!", error)
            raise error

    @game.command(name='create', aliases=['add', 'new'])
    async def create(self, ctx: Context, name: Optional[str]):
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

    @create.error
    async def create_error(self, ctx: Context, error: CommandError):
        return await send_generic_error(ctx, error)

    @game.command(name='delete', aliases=['remove', 'del'])
    async def delete(self, ctx: Context, game: GameConverter):
        '''
        Delete a game. WARNING! Can't be undone
        '''
        # Store variables before game gets deleted
        display_name = game.display_name

        delete_confirm_text = 'delete'
        delete_cancel_emoji = '🚫'
        delete_confirm_timeout = 30  # 30 seconds

        embed = warning_embed(title=f'Are you sure you want to delete {display_name}?', description="Once you delete the game, you can't undo it!")
        embed.add_field(name='Confirm', value=f'Type `{delete_confirm_text}` in the next {delete_confirm_timeout} seconds to confirm deletion')
        embed.add_field(name='Cancel', value=f'Press the {delete_cancel_emoji} button to cancel deletion')

        warning_message = await ctx.send(embed=embed)
        await warning_message.add_reaction(delete_cancel_emoji)

        def check_message(m: Message):
            '''Check that the author has sent a message but do NOT check text has matched'''
            return m.channel == ctx.channel and m.author == ctx.author

        def check_cancelled(reaction: Reaction, user: User):
            '''Check that the author has reacted with the cancel emoji'''
            return user == ctx.author and str(reaction.emoji) == delete_cancel_emoji

        user_response_message = None
        delete_is_confirmed = False

        user_response_message_task = asyncio.create_task(self.bot.wait_for('message', check=check_message))
        user_react_task = asyncio.create_task(self.bot.wait_for('reaction_add', check=check_cancelled))
        task_options = {user_response_message_task, user_react_task}
        done_tasks, pending_tasks = await asyncio.wait(task_options, timeout=delete_confirm_timeout, return_when=asyncio.FIRST_COMPLETED)

        if user_response_message_task in done_tasks:
            user_response_message = user_response_message_task.result()
        elif user_react_task in done_tasks:
            await self._update_delete_cancelled(message=warning_message, game_name=display_name, cancel_reason=f'{delete_cancel_emoji} has been pressed.')    
        elif len(pending_tasks) == len(task_options):
            # No option chosen after timeout
            await self._update_delete_cancelled(message=warning_message, game_name=display_name, cancel_reason=f'No action taken after {delete_confirm_timeout} seconds.')

        if user_response_message:
            if user_response_message.content.strip().lower() == delete_confirm_text:
                delete_is_confirmed = True
            else:
                await self._update_delete_cancelled(message=warning_message, game_name=display_name, cancel_reason=f'Text did not match `{delete_confirm_text}`.')

        if delete_is_confirmed:
            return await self._complete_deletion(ctx, game)

    @delete.error
    async def delete_error(self, ctx: Context, error: CommandError):
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    @game.group(name='channel', aliases=['textchannel'])
    async def channel(self, ctx: Context):
        '''Manage default games assigned per channel'''
        return await self.game_channel_controller.channel(ctx)

    @channel.command(name='use', aliases=['set'])
    async def use_channel(self, ctx: Context, game: Optional[GameConverter], channel: Optional[TextChannel]):
        '''
        Assign the channel to default to using the given game for all commands that require game as an optional parameter.
        
        Either game, channel or both must be provided.
        * If both game and channel are provided, then the given channel will default to the given game.
        * If only game is provided, then this channel will default to the given game.
        * If only channel is provided, then the given channel will default to the game that is default for this channel.
        '''
        return await self.game_channel_controller.use_channel(ctx=ctx, game=game, channel=channel)

    @use_channel.error
    async def use_channel_error(self, ctx: Context, error: CommandError):
        return await self.game_channel_controller.use_channel_error(ctx=ctx, error=error)

    @channel.command(name='show')
    async def show_channel(self, ctx: Context, game: Optional[GameConverter], channel: Optional[TextChannel]):
        '''
        Show info about the default game used for a channel
        If game is provided, show the channels that use this game as the default. Takes precedence over channel
        If channel is provided, show the game that the provided channel uses as the default.
        If neither is provied, show the game that this channel uses as the default.
        '''
        return await self.game_channel_controller.show_channel(ctx=ctx, game=game, channel=channel)

    @show_channel.error
    async def show_channel_error(self, ctx: Context, error: CommandError):
        return await self.game_channel_controller.show_channel_error(ctx=ctx, error=error)

    @channel.command(name='delete', aliases=['remove', 'del'])
    async def delete_channel(self, ctx: Context, game: Optional[GameConverter], channel: Optional[TextChannel]):
        '''
        Remove the default game assigned to the given channel.
        '''
        return await self.game_channel_controller.delete_channel(ctx=ctx, game=game, channel=channel)

    @delete_channel.error
    async def delete_channel_error(self, ctx: Context, error: CommandError):
        return await self.game_channel_controller.delete_channel_error(ctx=ctx, error=error)

    @game.group(name='category', aliases=['cat', '🐱', '🐈', '😸', '😹', '😺', '😻', '😼', '😽', '😾', '😿', '🙀'])
    async def category(self, ctx: Context):
        '''Manage default games assigned per category'''
        return await self.game_channel_controller.category(ctx)

    @category.command(name='use', aliases=['set'])
    async def use_category(self, ctx: Context, game: Optional[GameConverter], category: Optional[CategoryChannel]):
        '''
        Assign the category to default to using the given game for all commands that require game as an optional parameter.
        
        Either game, category or both must be provided.
        * If both game and category are provided, then the given category will default to the given game.
        * If only game is provided, then this category will default to the given game.
        * If only category is provided, then the given category will default to the game that is default for this category.
        '''
        return await self.game_channel_controller.use_category(ctx=ctx, game=game, category=category)

    @use_category.error
    async def use_category_error(self, ctx: Context, error: CommandError):
        return await self.game_channel_controller.use_category_error(ctx=ctx, error=error)

    @category.command(name='show')
    async def show_category(self, ctx: Context, game: Optional[GameConverter], category: Optional[CategoryChannel]):
        '''
        Show info about the default game used for a category
        If game is provided, show the categories that use this game as the default. Takes precedence over category
        If category is provided, show the game that the provided category uses as the default.
        If neither is provied, show the game that this category uses as the default.
        '''
        return await self.game_channel_controller.show_category(ctx=ctx, game=game, category=category)

    @show_category.error
    async def show_category_error(self, ctx: Context, error: CommandError):
        return await self.game_channel_controller.show_category_error(ctx=ctx, error=error)

    @category.command(name='delete', aliases=['remove', 'del'])
    async def delete_category(self, ctx: Context, game: Optional[GameConverter], category: Optional[CategoryChannel]):
        '''
        Remove the default game assigned to the given category.
        '''
        return await self.game_channel_controller.delete_category(ctx=ctx, game=game, category=category)

    @delete_category.error
    async def delete_category_error(self, ctx: Context, error: CommandError):
        return await self.game_channel_controller.delete_category_error(ctx=ctx, error=error)

    async def _send_no_games(self, ctx: Context):
        embed = info_embed(title=f"{ctx.guild.name} doesn't have any games!", description=f'Get a game started with: `{COMMAND_PREFIX}game create MyAwesomeGame`')
        embed.set_footer(text="See you real soon, pard'ner")
        await ctx.send(embed=embed)
    
    async def _send_games_list(self, ctx: Context, games: List[Game]):
        # Guild name. Truncate to 20 characters if name is excessively long
        # FIXME: Extract into helper and apply universally
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
                footer = f"Wow that's a lot of games. Delete some with `{COMMAND_PREFIX}game delete <name>`"
                break

        embed.add_field(name=field_name, value=field_value, inline=False)

        if footer:
            embed.set_footer(text=footer)
        
        return await ctx.send(embed=embed)

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
            return await send_generic_error(ctx, error_message='Expected either name to be too short or name to be too long, instead got errors:\n' + str(error))

        title = f'Error! Your name is too {length_error_text[0]}!'
        description = f'Please change your name **{name}** to be {length_error_text[1]} **{length_error_text[2]}** characters long and try again'
        
        embed = error_embed(title=title, description=description)
        return await ctx.send(embed=embed)

    async def _complete_deletion(self, ctx: Context, game: Game):
        self.game_service.delete(game)
        confirm_delete_embed = info_embed(title=f'Deleted game {game.display_name}', description='So long, and thanks for all the fish!')
        return await ctx.send(embed=confirm_delete_embed)

    async def _update_delete_cancelled(self, message: Message, game_name: str, cancel_reason: str):
        delete_stopped_title = f'Game {game_name} deletion cancelled'
        delete_stopped_description = cancel_reason + '\nPlease type the command again.'
        delete_stopped_embed = warning_embed(title=delete_stopped_title, description=delete_stopped_description)
        await message.edit(embed=delete_stopped_embed)
        await message.remove_reaction('🚫', self.bot.user)

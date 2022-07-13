from typing import Optional
from discord import TextChannel, CategoryChannel
from discord.ext import commands
from discord.ext.commands import Bot, Context, CommandError
from cogs.services import GameService
from converters import GameConverter, GameNotFoundError
from models import Game
from util.embed_builder import COMMAND_PREFIX, info_embed, error_embed, send_generic_error
import random

class GameChannelController:
    def __init__(self, bot: Bot, game_service: GameService):
        self.bot = bot
        self.game_service = game_service

    async def channel(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            embed = error_embed(title='Error! Missing subcommand for channel subcommand', description='Please check out the help command')  # TODO: Upgrade to include rich error message
            return await ctx.send(embed=embed)

    async def use_channel(self, ctx: Context, game: Optional[GameConverter], channel: Optional[TextChannel]):
        if not game and not channel:
            embed = error_embed(title=f'Error! Missing parameter game or channel', description="I'm not pyschic. I need you to give the name of a **game** or a **channel**.")
            return await ctx.send(embed=embed)
        
        channel = channel or ctx.channel
        altered_game = self.game_service.add_channel(game=game, channel=channel)

        description = f'The channel {channel.mention} will now default to using the game **{game.display_name}**. Less typing for you!'
        if altered_game:
            if altered_game == game:
                embed = error_embed(title=f'Error! Game **{game.display_name}** already has the channel #{channel.name}', description=f'You can see all channels that use this game as default with `{COMMAND_PREFIX}game channel show {game.display_name}`')
                return await ctx.send(embed=embed)

            description += f'Your other game **{altered_game.display_name}** will no longer use the channel as the default'

        embed = info_embed(title=f'Game **{game.display_name}** set for channel #{channel.name}', description=description)
        return await ctx.send(embed=embed)

    async def use_channel_error(self, ctx: Context, error: CommandError):
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    async def show_channel(self, ctx: Context, game: Optional[GameConverter], channel: Optional[TextChannel]):
        '''
        Show info about the default game used for a channel
        If game is provided, show the channels that use this game as the default. Takes precedence over channel
        If channel is provided, show the game that the provided channel uses as the default.
        If neither is provied, show the game that this channel uses as the default.
        '''

        if not game and not channel:
            channel = ctx.channel
        
        if game:
            return await self._send_channel_list(ctx=ctx, game=game)

        if channel:
            return await self._send_game_using_channel(ctx=ctx, channel=channel)

    async def show_channel_error(self, ctx: Context, error: CommandError):
        # FIXME: try nonexistent game name, see if this error shows up as expected
        # FIXME: Merge with other channel errors
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    async def delete_channel(self, ctx: Context, game: Optional[GameConverter], channel: Optional[TextChannel]):
        channel = channel or ctx.channel
        game = game or self.game_service.find_by_channel(channel=channel)

        # TODO: This if statement belongs in game_service somehow
        if not game or str(channel.id) not in game.text_channel_ids:
            embed = error_embed(title=f"The channel #{channel.name} doesn't have a default game already!", description=f'You can try `{COMMAND_PREFIX}game channel use <game> #{channel.name}` to set up the default instead')
            return await ctx.send(embed=embed)

        self.game_service.delete_channel(game=game, channel=channel)

        embed = info_embed(title=f'Game {game.display_name} will no longer be used as the default game for #{channel.name}', description=f'You can undo this with `{COMMAND_PREFIX}game channel use <game> #{channel.name}`')
        return await ctx.send(embed=embed)

    async def delete_channel_error(self, ctx: Context, error: CommandError):
        # FIXME: try nonexistent game name, see if this error shows up as expected
        # FIXME: Merge with other channel errors
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    async def category(self, ctx: Context):        
        if ctx.invoked_subcommand is None:
            embed = error_embed(title='Error! Missing subcommand for category subcommand', description='Please check out the help command')  # TODO: Upgrade to include rich error message
            return await ctx.send(embed=embed)

    async def category_after_invoke(self, ctx: Context):
        cat_emojis = ['🐱', '🐈', '😸', '😹', '😺', '😻', '😼', '😽', '😾', '😿', '🙀']
        if ctx.invoked_with.lower() == 'cat' or ctx.invoked_with in cat_emojis:
            await ctx.message.add_reaction(random.choice(cat_emojis))

    async def use_category(self, ctx: Context, game: Optional[GameConverter], category: Optional[CategoryChannel]):
        if not game and not category:
            embed = error_embed(title=f'Error! Missing parameter game or category', description="I'm not pyschic. I need you to give the name of a **game** or a **category**.")
            return await ctx.send(embed=embed)
        
        category, error_msg = self._get_category(ctx, category)
        if not category:
            return await ctx.send(embed=error_msg)

        altered_game = self.game_service.add_category(game=game, category=category)

        description = f'The category {category.mention} will now default to using the game **{game.display_name}**. Less typing for you!'
        if altered_game:
            if altered_game == game:
                embed = error_embed(title=f'Error! Game **{game.display_name}** already has the category {category.name}', description=f'You can see all categories that use this game as default with `{COMMAND_PREFIX}game category show {game.display_name}`')
                return await ctx.send(embed=embed)

            description += '\n' + f'Your other game **{altered_game.display_name}** will no longer use the category as the default'

        embed = info_embed(title=f'Game **{game.display_name}** set for category {category.name}', description=description)
        return await ctx.send(embed=embed)

    async def use_category_error(self, ctx: Context, error: CommandError):
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    async def show_category(self, ctx: Context, game: Optional[GameConverter], category: Optional[CategoryChannel]):
        if not game and not category:
            category, error_msg = self._get_category(ctx, category)
            if not category:
                return await ctx.send(embed=error_msg)
        
        if game:
            return await self._send_category_list(ctx=ctx, game=game)

        if category:
            return await self._send_game_using_category(ctx=ctx, category=category)

    async def show_category_error(self, ctx: Context, error: CommandError):
        # FIXME: try nonexistent game name, see if this error shows up as expected
        # FIXME: Merge with other channel errors
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    async def delete_category(self, ctx: Context, game: Optional[GameConverter], category: Optional[CategoryChannel]):
        category, error_msg = self._get_category(ctx, category)
        if not category:
            return await ctx.send(embed=error_msg)
        game = game or self.game_service.find_by_category(category=category)

        # TODO: This if statement belongs in game_service somehow
        if not game or str(category.id) not in game.category_ids:
            embed = error_embed(title=f"The category {category.name} doesn't have a default game already!", description=f'You can try `{COMMAND_PREFIX}game category use <game> {category.name}` to set up the default instead')
            return await ctx.send(embed=embed)

        self.game_service.delete_category(game=game, category=category)

        embed = info_embed(title=f'Game {game.display_name} will no longer be used as the default game for {category.name}', description=f'You can undo this with `{COMMAND_PREFIX}game category use <game> {category.name}`')
        return await ctx.send(embed=embed)

    async def delete_category_error(self, ctx: Context, error: CommandError):
        # FIXME: try nonexistent game name, see if this error shows up as expected
        # FIXME: Merge with other category errors
        if isinstance(error, GameNotFoundError):
            return await error.send_error(ctx)
        else:
            return await send_generic_error(ctx, error=error)

    async def _send_channel_list(self, ctx: Context, game: Game):
        channel_ids = game.text_channel_ids
        
        if not channel_ids:
            title = f'Game **{game.display_name}** is not set as the default game for any channels yet!'
            description = f"Type `{COMMAND_PREFIX}game channel use <game name> <channel name>` to make this the default game for a channel. You'll thank me later 😉"
            embed = info_embed(title=title, description=description)
            return await ctx.send(embed=embed)

        num_channels = len(channel_ids)
        channels = [ctx.guild.get_channel(int(id)) for id in channel_ids]

        title = f'Game **{game.display_name}** is the default game for {num_channels} channel{"s" if num_channels != 1 else ""}'
        description = '\n'.join(['The following channels use this game as the default game.', 
            f'Type `{COMMAND_PREFIX}game channel use <game name> <channel name>` to change a channel to use a different game or to add more channels here.'])
        embed = info_embed(title=title, description=description)

        field_name = 'Channels:'
        field_value = ''
        footer = None
        for channel in channels:
            # Check that length of embed does not 6000 character limit (with buffer room for extra text)
            if len(embed) + len(channel.mention) + 4 <= 5930:
                field_value += '- {}\n'.format(channel.mention)
            else:
                # TODO: Wow, that's a lot of channels. Add some pagination!
                footer = f"Wow that's a lot of channels. Delete some with `{COMMAND_PREFIX}game channel delete <channel>`"
                break

        embed.add_field(name=field_name, value=field_value, inline=False)

        if footer:
            embed.set_footer(text=footer)
        
        return await ctx.send(embed=embed)

    async def _send_game_using_channel(self, ctx: Context, channel: TextChannel):
        game = self.game_service.find_by_channel(channel=channel)
        
        tip_line = f'To change the default game for this channel, type `{COMMAND_PREFIX}game channel use <game_name> #{channel.name}`'

        if game:
            title = f'Game **{game.display_name}** is the default game for #{channel.name}'
            description = '\n'.join([f'Whenever a command sent in the channel {channel.mention} has an optional `[game]` parameter, the game **{game.display_name}** will be used as the default.',
            tip_line])
            return await ctx.send(embed=info_embed(title=title, description=description))
        else:
            title = f"The channel #{channel.name} doesn't have a default game!"
            description = '\n'.join([f'If you set a default game for this channel, then whenever a command sent in the channel {channel.mention} has an optional `[game]` parameter, that game will be used as the default.',
            tip_line,
            "If you or your fellow players plan to use this channel a lot for a game, I recommend you try it out! 😊"])
            return await ctx.send(embed=info_embed(title=title, description=description))

    def _get_category(self, ctx: Context, category: Optional[CategoryChannel]):
        category = category or ctx.channel.category
        if not category:
            description = '\n'.join(["This can happen if you spelled your category name wrong or if you didn't specify a category and you sent this from a channel without a category.",
            f'You can try setting a default game for this channel instead with `{COMMAND_PREFIX}game channel use <game> <channel>`'])
            embed = error_embed(title=f'Error! Could not find any channel category!', description=description)
            return None, embed

        return category, None

    async def _send_category_list(self, ctx: Context, game: Game):
        category_ids = game.category_ids
        
        if not category_ids:
            title = f'Game **{game.display_name}** is not set as the default game for any categories yet!'
            description = f"Type `{COMMAND_PREFIX}game category use <game name> <category name>` to make this the default game for a category. You'll thank me later 😉"
            embed = info_embed(title=title, description=description)
            return await ctx.send(embed=embed)

        num_categories = len(category_ids)
        categories = [ctx.guild.get_channel(int(id)) for id in category_ids]

        title = f'Game **{game.display_name}** is the default game for {num_categories} {"categories" if num_categories != 1 else "category"}'
        description = '\n'.join(['The following categories use this game as the default game.', 
            f'Type `{COMMAND_PREFIX}game category use <game name> <category name>` to change a category to use a different game or to add more categories here.'])
        embed = info_embed(title=title, description=description)

        field_name = 'Categories:'
        field_value = ''
        footer = None
        for category in categories:
            # Check that length of embed does not 6000 character limit (with buffer room for extra text)
            if len(embed) + len(category.mention) + 4 <= 5930:
                field_value += '- {}\n'.format(category.mention)
            else:
                # TODO: Wow, that's a lot of channels. Add some pagination!
                footer = f"Wow that's a lot of channels. Delete some with `{COMMAND_PREFIX}game channel delete <channel>`"
                break

        embed.add_field(name=field_name, value=field_value, inline=False)

        if footer:
            embed.set_footer(text=footer)
        
        return await ctx.send(embed=embed)

    async def _send_game_using_category(self, ctx: Context, category: CategoryChannel):
        game = self.game_service.find_by_category(category=category)
        
        tip_line = f'To change the default game for this channel, type `{COMMAND_PREFIX}game channel use <game_name> {category.name}`'

        if game:
            title = f'Game **{game.display_name}** is the default game for {category.name}'
            description = '\n'.join([f'Whenever a command sent in the category {category.mention} has an optional `[game]` parameter, the game **{game.display_name}** will be used as the default.',
            tip_line])
            return await ctx.send(embed=info_embed(title=title, description=description))
        else:
            title = f"The category {category.name} doesn't have a default game!"
            description = '\n'.join([f'If you set a default game for this category, then whenever a command sent in the category {category.mention} has an optional `[game]` parameter, that game will be used as the default.',
            tip_line,
            "If you or your fellow players plan to use this category a lot for a game, I recommend you try it out! 😊"])
            return await ctx.send(embed=info_embed(title=title, description=description))
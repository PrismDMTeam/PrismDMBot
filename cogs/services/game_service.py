from typing import Optional, List
from redis_om import NotFoundError
from discord.ext import commands
from discord import Guild, TextChannel, CategoryChannel
from models.game import Game
from models.character import Character
from util.name_builder import create_unique_name, create_search_name

# Database management for all Game models
class GameService(commands.Cog):
    def find_by_guild(self, guild: Guild) -> List[Game]:
        return Game.find(Game.guild_id == guild.id).all()
        
    def find_by_guild_and_name(self, guild: Guild, name: str) -> Game:
        games = Game.find((Game.guild_id == guild.id) & (Game.search_name == name.casefold())).all()
        if len(games) == 1:
            return games[0]
        elif len(games):
            # TODO: Throw some error about duplicate entries
            print(f'Error! {len(games)} with duplicate search name {name} found')
            return games[0]
        else:
            return None

    def find_by_channel(self, channel: TextChannel) -> Game | None:
        try:
            return Game.find((Game.guild_id == channel.guild.id) & (Game.text_channel_ids << str(channel.id))).first()
        except NotFoundError:
            return None

    def find_by_category(self, category: CategoryChannel) -> Game | None:
        try:
            return Game.find((Game.guild_id == category.guild.id) & (Game.category_ids << str(category.id))).first()
        except NotFoundError:
            return None

    def create(self, guild: Guild, game_name: Optional[str] = None) -> Game:
        '''
        Create a new game using the game name provided
        If no game name is provided, will try to name it the first available name, such as Game, Game1, Game2, Game3 etc.
        Raises ValidationError if name is too short or too long
        '''
        game_names = {game.display_name for game in self.find_by_guild(guild)}
        display_name = create_unique_name(name_attempt=game_name or 'Game', existing_names=game_names)

        game = Game(guild_id = guild.id,
            display_name=display_name,
            search_name=create_search_name(display_name),
            text_channel_ids=[],
            category_ids=[])
        game.save()
        return game

    def delete(self, game: Game):
        Game.delete(game.pk)

    def add_channel(self, game: Game, channel: TextChannel) -> Game | None:
        '''
        Adds the given channel to this game's list of channel IDs
        If this channel exists in any other game, then remove the channel from that game and return that game.
        If this channel already exists in this game, then just return the game with no changes.
        '''
        existing_game = self.find_by_channel(channel=channel)
        if existing_game:
            if existing_game == game:
                return game

            existing_game.text_channel_ids.remove(str(channel.id))
            existing_game.save()

        game.text_channel_ids = game.text_channel_ids or []
        game.text_channel_ids.append(str(channel.id))
        game.save()

        return existing_game

    def delete_channel(self, game: Game, channel: TextChannel):
        game.text_channel_ids.remove(str(channel.id))
        game.save()

    def add_category(self, game: Game, category: CategoryChannel) -> Game | None:
        '''
        Adds the given category to this game's list of category IDs
        If this category exists in any other game, then remove the category from that game and return that game
        '''
        existing_game = self.find_by_category(category=category)
        if existing_game:
            existing_game.category_ids.remove(str(category.id))
            existing_game.save()

        game.category_ids = game.category_ids or []
        game.category_ids.append(str(category.id))
        game.save()

        return existing_game

    def delete_category(self, game: Game, category: CategoryChannel):
        game.category_ids.remove(str(category.id))
        game.save()


    def add_character(self, game: Game, character: Character):
        if not game.char_ids:
            game.char_ids = []
        game.char_ids.append(character.pk)
        game.save()
        return character

    def delete_character(self, game: Game, character: Character):
        if not game.char_ids or character.pk not in game.char_ids:
            return None
        game.char_ids.remove(character.pk)
        return character
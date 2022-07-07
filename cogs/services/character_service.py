from typing import List
from redis_om import NotFoundError
from discord.ext import commands
from discord.ext.commands import Bot
from discord import Member
from models.character import Character
from models.game import Game
from util.name_builder import create_unique_name, create_search_name

# Database management for all Game models
class CharacterService(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def find_by_member(self, member: Member) -> List[Character]:
        return Character.find(Character.player_id == member.id).all()

    def find_by_game(self, game: Game) -> List[Character]:
        return Character.find(Character.game_id == game.pk).all()

    def find_by_game_and_member(self, game: Game, member: Member) -> Character | None:
        try:
            return Character.find((Character.game_id == game.pk) & (Character.player_id == member.id)).first()
        except NotFoundError:
            return None

    def find_by_game_and_name(self, game: Game, name: str) -> Character | None:
        try:
            return Character.find((Character.game_id == game.pk) & (Character.search_name == name.casefold())).first()
        except NotFoundError:
            return None

    def create(self, game: Game, name: str) -> Character:
        character_names = {char.display_name for char in self.find_by_game(game)}
        display_name = create_unique_name(name_attempt=name, existing_names=character_names)

        character = Character(game_id = game.pk,
            display_name=display_name,
            search_name=create_search_name(display_name),
            attributes={})
        character.save()

        # Add the character to the game
        self.bot.get_cog("GameService").add_character()

        return character

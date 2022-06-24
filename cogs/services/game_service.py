from typing import Optional
import uuid
from discord.ext import commands
from discord.guild import Guild
from models.game import Game

# Database management for all Game models
class GameService(commands.Cog):
    def find_by_guild(self, guild: Guild) -> list[Game]:
        return Game.find(Game.guild_id == guild.id).all()
        
    def create(self, guild: Guild, game_name: Optional[str] = None) -> Game:
        '''
        Create a new game using the game name provided
        If no game name is provided, will try to name it the first available name, such as Game, Game1, Game2, Game3 etc.
        '''
        display_name = game_name or self._create_unique_name(guild=guild, game_name='Game')
        game = Game(guild_id = guild.id,
            display_name=display_name,
            search_name=self._create_search_name(display_name))
        game.save()
        return game
        

    def _create_search_name(self, display_name: str) -> str:
        return display_name.lower()

    def _create_unique_name(self, guild: Guild, game_name: str) -> str:
        games = self.find_by_guild(guild)
        lower_display_names = {game.display_name.lower() for game in games}
        
        if self._is_name_free(name_attempt=game_name, names=lower_display_names):
            return game_name

        for i in range(1, 1000):
            name_attempt = game_name + str(i)
            if self._is_name_free(name_attempt=name_attempt, names=lower_display_names):
                return name_attempt

        # Failsafe - return a random UUID
        return str(uuid.uuid4())

    def _is_name_free(self, name_attempt: str, names: set[str]) -> bool:
        '''
        Check if the proposed name is free
        Check only lowercased version of display names since all search names are identical anyway
        '''
        return name_attempt.lower() not in names

        
        
        


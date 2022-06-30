from cogs.controllers.model_controller import ModelController
from discord.ext.commands import Bot
from models.character import Character

class CharacterController(ModelController):
    def __init__(self, bot: Bot):
        super().__init__(cls=Character, bot=bot)

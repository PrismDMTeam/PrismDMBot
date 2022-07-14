import os
from dotenv import load_dotenv
from discord import Intents
from discord.ext.commands import Bot, Context, CommandError, NoPrivateMessage
from cogs.controllers import GameController, CharacterController, MessageController
from cogs.services.game_service import GameService
from cogs.services.character_service import CharacterService
from cogs.services.sentiment_service import SentimentService
from util.embed_builder import send_guild_only_error

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')

# TODO: Migration to discord.py 2.0.0 will require await keyword for all add_cog calls
def add_cogs(bot: Bot):
    game_service = GameService()
    bot.add_cog(game_service)
    character_service = CharacterService(bot)
    bot.add_cog(character_service)

    sentiment_service = SentimentService(bot)
    bot.add_cog(sentiment_service)

    bot.add_cog(GameController(bot, game_service))
    bot.add_cog(CharacterController(bot, game_service, character_service))
    bot.add_cog(MessageController(bot, sentiment_service))

bot = Bot(command_prefix=COMMAND_PREFIX, intents=Intents.default())
# TODO: Add async with bot:  to make call this line async and await (discord.py 2.0.0)
add_cogs(bot)

@bot.command(name='ping')
async def test(ctx: Context):
    await ctx.channel.send('Pong!')

@bot.event
async def on_command_error(ctx: Context, error: CommandError):
    if isinstance(error, NoPrivateMessage):
        return await send_guild_only_error(ctx)

bot.run(DISCORD_TOKEN)
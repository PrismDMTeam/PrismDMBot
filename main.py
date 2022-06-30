import os
from dotenv import load_dotenv
from discord.ext.commands import Bot, Context, CommandError, NoPrivateMessage
from cogs.controllers.character_controller import CharacterController
from cogs.controllers.game_controller import GameController
from cogs.controllers.message_controller import MessageController
from cogs.services.game_service import GameService
from util.embed_builder import send_guild_only_error

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')

def add_cogs(bot: Bot):
    game_service = GameService()
    bot.add_cog(game_service)

    bot.add_cog(GameController(bot, game_service))
    bot.add_cog(CharacterController(bot))
    bot.add_cog(MessageController(bot))

bot = Bot(command_prefix=COMMAND_PREFIX)
add_cogs(bot)

@bot.command(name='ping')
async def test(ctx: Context):
    await ctx.channel.send('Pong!')

@bot.event
async def on_command_error(ctx: Context, error: CommandError):
    if isinstance(error, NoPrivateMessage):
        return await send_guild_only_error(ctx)

bot.run(DISCORD_TOKEN)
import os
from dotenv import load_dotenv
from discord.ext.commands import Bot, Context

from cogs.services.game_service import GameService
from cogs.controllers.game_controller import GameController
from models.game import Game

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')

def add_cogs(bot: Bot):
    game_service = GameService()
    bot.add_cog(game_service)

    bot.add_cog(GameController(game_service))

bot = Bot(command_prefix=COMMAND_PREFIX)
add_cogs(bot)

@bot.command(name='ping')
async def test(ctx: Context):
    await ctx.channel.send('Pong!')

@bot.command(name='setup')
async def setup(ctx: Context):    
    # game = Game(guild_id=ctx.guild.id, char_ids=[9, 8, 7])
    # pk = game.pk
    # print('!!! pk is ', pk)
    # game.save()

    game_service = bot.get_cog('GameService')
    game = game_service.create(guild=ctx.guild)
    await ctx.channel.send("Finished setting up game! Id: " + game.pk)


@bot.command(name='showgame')
async def showgame(ctx: Context, game_id: str):
    game = Game.get(pk=game_id)
    message = f'Game: {game.display_name}'
    message += '\nSearch name: ' + game.search_name
    if game.char_ids:
        message += '\nchar_ids: ' + ', '.join(str(id) for id in game.char_ids)
    await ctx.channel.send(message)

@bot.command(name='games')
async def games(ctx: Context):
    games = Game.find(Game.guild_id==ctx.guild.id).all()
    if games:
        game_ids = [str(game.pk) for game in games]
        await ctx.channel.send('Game IDs for this guild:\n{}'.format("\n".join(game_ids)))
    else:
        await ctx.channel.send("Looks like your server hasn't set up any games yet!")

# @bot.command(name='deletegame', aliases=['delgame'])
# async def delgame(ctx: Context, game_id: str):


# FIXME: Delete
@bot.command(name='purge')
async def purge(ctx: Context):
    games = Game.find(Game.guild_id==ctx.guild.id).all()
    for game in games:
        Game.delete(game.pk)
    await ctx.channel.send("Bye games!")

bot.run(DISCORD_TOKEN)
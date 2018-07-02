import discord
import re
from discord.ext import commands

from default_players import default_players
from hungergames import HungerGames
from enums import ErrorCode
from bot import HungryBot
from config import config

prefix = '''h$'''
bot = HungryBot(command_prefix=prefix, description="A Hunger Games simulator bot")
hg = HungerGames()


@bot.event
async def on_ready():
    print('Logged in!')
    await bot.change_presence(
        activity=discord.Game(name="{}help".format(prefix), url=None, type=2)
    )


@bot.command()
async def ping(ctx):
    """Pong!"""
    await ctx.send("Pong!")


@bot.command(rest_is_raw=True)
@commands.guild_only()
async def new(ctx, *, title: str = None):
    """
    Start a new Hunger Games simulation in the current channel.
    Each channel can only have one simulation running at a time.

    title - (Optional) The title of the simulation. Defaults to 'The Hunger Games'
    """
    if title is None or title == "":
        # title = "The Hunger Games"
        title = "Kuro's VIP Hunger Games"
    else:
        title = __strip_mentions(ctx.message, title)
        title = __sanitize_here_everyone(title)
        title = __sanitize_special_chars(title)
    owner = ctx.author
    ret = hg.new_game(ctx.channel.id, owner.id, owner.name, title)
    if not await __check_errors(ctx, ret):
        return
    await ctx.send("{0} has started {1}! Use `{2}add [-m|-f] <name>` to add a player or `{2}join [-m|-f]` to enter the "
                   "game yourself!".format(owner.mention, title, prefix))


@bot.command()
@commands.guild_only()
async def join(ctx, gender=None):
    """
    Adds a tribute with your name to a new simulation.

    gender (Optional) - Use `-m` or `-f` to set male or female gender. Defaults to a random gender.
    """
    name = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
    ret = hg.add_player(ctx.channel.id, name, gender=gender, volunteer=True)
    if not await __check_errors(ctx, ret):
        return
    await ctx.reply(ret)


@bot.command(rest_is_raw=True)
@commands.guild_only()
async def add(ctx, *, name: str):
    """
    Add a user to a new game.

    name - The name of the tribute to add. Limit 32 chars. Leading and trailing whitespace will be trimmed.
    Special chars @*_`~ count for two characters each.
    \tPrepend the name with a `-m ` or `-f ` flag to set male or female gender. Defaults to a random gender.
    """
    name = __strip_mentions(ctx.message, name)
    name = __sanitize_here_everyone(name)
    name = __sanitize_special_chars(name)

    ret = hg.add_player(ctx.channel.id, name)
    if not await __check_errors(ctx, ret):
        return
    await ctx.send(ret)


@bot.command(rest_is_raw=True)
@commands.guild_only()
async def remove(ctx, *, name: str):
    """
    Remove a user from a new game.
    Only the game's host may use this command.

    name - The name of the tribute to remove.
    """
    name = __strip_mentions(ctx.message, name)
    name = __sanitize_here_everyone(name)
    name = __sanitize_special_chars(name)

    ret = hg.remove_player(ctx.channel.id, name)
    if not await __check_errors(ctx, ret):
        return
    await ctx.send(ret)


@bot.command()
@commands.guild_only()
async def fill(ctx, group_name=None):
    """
    Pad out empty slots in a new game with default characters.

    group_name (Optional) - The builtin group to draw tributes from. Defaults to members in this guild.
    """
    if group_name is None:
        group = []
        for m in list(ctx.message.guild.members):
            if m.nick is not None:
                group.append(m.nick)
            else:
                group.append(m.name)
    else:
        group = default_players.get(group_name)

    ret = hg.pad_players(ctx.channel.id, group)
    if not await __check_errors(ctx, ret):
        return
    await ctx.send(ret)


@bot.command()
@commands.guild_only()
async def status(ctx):
    """
    Gets the status for the game in the channel.
    """
    ret = hg.status(ctx.channel.id)
    if not await __check_errors(ctx, ret):
        return
    embed = discord.Embed(title=ret['title'], description=ret['description'])
    embed.set_footer(text=ret['footer'])
    await ctx.send(embed=embed)


@bot.command()
@commands.guild_only()
async def start(ctx):
    """
    Starts the pending game in the channel.
    """
    ret = hg.start_game(ctx.channel.id, ctx.author.id, prefix)
    if not await __check_errors(ctx, ret):
        return
    embed = discord.Embed(title=ret['title'], description=ret['description'])
    embed.set_footer(text=ret['footer'])
    await ctx.send(embed=embed)


@bot.command()
@commands.guild_only()
async def end(ctx):
    """
    Cancels the current game in the channel.
    """
    ret = hg.end_game(ctx.channel.id, ctx.author.id)
    if not await __check_errors(ctx, ret):
        return
    await ctx.send("{0} has been cancelled. Anyone may now start a new game with `{1}new`.".format(ret.title, prefix))


@bot.command()
@commands.guild_only()
async def step(ctx):
    """
    Steps forward the current game in the channel by one round.
    """
    ret = hg.step(ctx.channel.id, ctx.author.id)
    if not await __check_errors(ctx, ret):
        return
    embed = discord.Embed(title=ret['title'], color=ret['color'], description=ret['description'])
    if ret['footer'] is not None:
        embed.set_footer(text=ret['footer'])
    await ctx.send(embed=embed)


async def __check_errors(ctx, error_code):
    if type(error_code) is not ErrorCode:
        return True
    if error_code is ErrorCode.NO_GAME:
        await ctx.reply("There is no game currently running in this channel.")
        return False
    if error_code is ErrorCode.GAME_EXISTS:
        await ctx.reply("A game has already been started in this channel.")
        return False
    if error_code is ErrorCode.GAME_STARTED:
        await ctx.reply("This game is already running.")
        return False
    if error_code is ErrorCode.GAME_FULL:
        await ctx.reply("This game is already at maximum capacity.")
        return False
    if error_code is ErrorCode.PLAYER_EXISTS:
        await ctx.reply("That person is already in this game.")
        return False
    if error_code is ErrorCode.CHAR_LIMIT:
        await ctx.reply("That name is too long (max 32 chars).")
        return False
    if error_code is ErrorCode.NOT_OWNER:
        await ctx.reply("You are not the owner of this game.")
        return False
    if error_code is ErrorCode.INVALID_GROUP:
        await ctx.reply("That is not a valid group. Valid groups are:\n```\n{0}\n```"
                        .format("\n".join(list(default_players.keys()))))
        return False
    if error_code is ErrorCode.NOT_ENOUGH_PLAYERS:
        await ctx.reply("There are not enough players to start a game. There must be at least 2.")
        return False
    if error_code is ErrorCode.GAME_NOT_STARTED:
        await ctx.reply("This game hasn't been started yet.")
        return False
    if error_code is ErrorCode.PLAYER_DOES_NOT_EXIST:
        await ctx.reply("There is no player with that name in this game.")
        return False


def __strip_mentions(message: discord.Message, text):
    members = message.mentions
    channels = message.channel_mentions
    roles = message.role_mentions

    for m in members:
        # name = m.nick if m.nick is not None else m.name
        # text = re.sub(m.mention, name, text)
        text = m.mention

    for c in channels:
        # text = re.sub(c.mention, c.name, text)
        text = c.mention

    for r in roles:
        # text = re.sub(r.mention, r.name, text)
        text = r.mention

    return text


def __sanitize_here_everyone(text):
    text = re.sub('@here', '@\u180Ehere', text)
    text = re.sub('@everyone', '@\u180Eeveryone', text)
    return text


def __sanitize_special_chars(text):
    # text = re.sub('@', '\\@', text)
    text = re.sub('~~', '\\~\\~', text)
    text = re.sub('\*', '\\*', text)
    text = re.sub('`', '\\`', text)
    text = re.sub('_', '\\_', text)
    return text.strip()


bot.run(config['token'])

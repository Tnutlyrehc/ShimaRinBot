import hypixel
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import random
import praw
import youtube_dl

#Bot Setup and APIs

client = commands.Bot("/")

startup_extensions = ["Music"]

API_KEYS = ['HYPIXELAPIKEYHERE']
hypixel.setKeys(API_KEYS)

post = praw.Reddit(client_id='',
                   client_secret='',
                   user_agent='Shima Rin Bot v0.1 by DjDarkAssassin')

@client.event
async def on_ready():
    print("Bot online")
    await client.change_presence(game=discord.Game(name="In Dj's Tent reading manga together ;)"))

class Main_Commands():
    def __init__(self, client):
        self.client = client



#Game
@client.command(pass_context=True)
async def coin(ctx):
    """Flips a coin"""
    choice = random.randint(1, 2)
    if choice == 1:
        await client.say("It landed on Tails!")
    if choice == 2:
        await client.say("It landed on Heads!")


#Responses

@client.command()
async def whatismilk():
    """Tells you what milk really is"""
    await client.say('Cereal Sauce')

@client.command(pass_context=True)
async def ping():
    """Pong"""
    await client.say("pong")

@client.command(pass_context=True)
async def hello():
    """Hello There!"""
    await client.say("Hi There! :wave:")

@client.command(pass_context=True)
async def idiot():
    """You're an idiot!"""
    await client.say("You're an idiot!")

@client.command(pass_context=True)
async def suwupreme():
    """Lyrics from the song 'Miraie - Suwupreme(Feat. Fluff Pink)'"""
    await client.say("Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme")

@client.command(pass_context=True)
async def baka():
    """BAKA!"""
    await client.say("no u")

@client.command(pass_context=True)
async def say(ctx,*args):
    """Makes the bot say whatever you want [Only for selected users]"""
    if ctx.message.author.id == 'USERID':
        mesg = ' '.join(args)
        await client.delete_message(ctx.message)
        return await client.say(mesg)

    elif ctx.message.author.id == 'USERID':
        mesg = ' '.join(args)
        await client.delete_message(ctx.message)
        return await client.say(mesg)

    elif ctx.message.author.id == 'USERID':
        mesg = ' '.join(args)
        await client.delete_message(ctx.message)
        return await client.say(mesg)

@client.command()
async def todolist():
    """List of what I will do in the future :D"""
    await client.say("What to do:\n1. CoinMarketCap command\n2. Fortnite stats\n3. 4chan command")

#Reddit Posts

@client.command()
async def meirl():
    """Gets a post from r/meirl"""
    meirl = post.subreddit('me_irl').hot()
    pick_post = random.randint(1, 21)
    for i in range(0, pick_post):
        sub = next(x for x in meirl if not x.stickied)

    await client.say(sub.url)

@client.command()
async def reddit(arg):
    """Gets a post from any subreddit"""
    posts = post.subreddit(arg).hot()
    pick_post = random.randint(1, 21)
    for i in range (0, pick_post):
        sub = next(x for x in posts if not x.stickied)

    await client.say(sub.url)

    #Fortnite

@client.command(pass_context=True)
async def whereto():
    """Randomly select a place in Fortnite"""
    places = ["Hero House", "Villain House", "Risky Reels", "Lucky Landing", "China Motel", "New Factories", "Motel", "anywhere you want", "Football Ground", "Between Shifty and Flush", "Container", "Jail", "North of Wailing Woods", "Anarchy Acres", "Dusty Divot", "Fatal Fields", "Flush Factory", "Greasy Grove", "Haunted Hills", "Junk Junction", "Lonely Lodge", "Loot Lake", "Moisty Mire", "Pleasant Park", "Retail Row", "Salty Springs", "Shifty Shafts", "Snobby Shores", "Tilted Towers", "Tomato Town", "Wailing Woods"]
    plc = random.choice(places)
    place = plc.lower()
    if plc == "anywhere you want":
        await client.say("Go " + place)
    else:
        await client.say("Go to " + place)

#Stats

@client.command()
async def hystats(arg):
    """Gets stats from Hypixel for a user"""

    player = hypixel.Player(arg)
    PlayerName = player.getName()
    PlayerLevel = player.getLevel()
    PlayerRank = player.getRank()

    embed = discord.Embed(
        title='Hypixel Stats',
        colour= discord.Colour.red()
        )

    embed.set_thumbnail(url='https://hypixel.net/attachments/621065/')
    embed.add_field(name='Player Name:', value=PlayerName, inline=False)
    embed.add_field(name='Player Rank:', value=PlayerRank['rank'], inline=False)
    embed.add_field(name='Player Level:', value=PlayerLevel, inline=False)
    await client.say(embed=embed)

#Bitcoin

@client.command(pass_context=True)
async def bitcoin():
    """Gets the price of bitcoin from CoinDesk"""
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    async with aiohttp.ClientSession() as session:  # Async HTTP request
        raw_response = await session.get(url)
        response = await raw_response.text()
        response = json.loads(response)
        embed = discord.Embed (
            title='CryptoCurrency',
            colour= discord.Colour.gold()
        )

        embed.set_thumbnail(url='')
        embed.add_field(name='Bitcoin Price:', value=('$' + response['bpi']['USD']['rate']), inline=True)
        await client.say(embed=embed)

#Music

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))





client.run('BOT_TOKEN')

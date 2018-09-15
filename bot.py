import hypixel
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import random
import praw
import youtube_dl
import time
from weather import Weather, Unit
from fortnite_python import Fortnite
from fortnite_python.domain import Mode
from fortnite_python.domain import Platform
import os
import aiohttp
import json

#Bot Setup and APIs

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

def __init__(self, bot):
        self.bot = bot

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = ' {0.title} uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()
class Music:
    """Music commands.
    Can play music from Youtube
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Ready to play audio in **' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('Are you sure your in a channel?')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            await self.bot.say("Loading the song please be patient..")
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))
    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            await self.bot.say("Cleared the queue and disconnected from voice channel ")
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def skipf(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == '':
            await self.bot.say('A powerful force decided to force skip this song...')
            state.skip()


    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))




client = commands.Bot("/")

startup_extensions = ["Music"]

HYPIXELAPI = os.environ.get('HYPIXEL_KEY')
API_KEYS = [HYPIXELAPI]
hypixel.setKeys(API_KEYS)

REDDITID = os.environ.get('REDDIT_ID')
REDDITSECRET = os.environ.get('REDDIT_SECRET')

post = praw.Reddit(client_id=REDDITID,
                   client_secret=REDDITSECRET,
                   user_agent='Shima Rin Bot v0.1 by DjDarkAssassin')

FORTNITEKEY = os.environ.get('FORTNITE_KEY')

fortnite = Fortnite(FORTNITEKEY)



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
async def ping(ctx):
    """Pong"""



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
    try:
        if ctx.message.author.id == 'USER1':
            mesg = ' '.join(args)
            await client.delete_message(ctx.message)
            return await client.say(mesg)

        elif ctx.message.author.id == 'USER2':
            mesg = ' '.join(args)
            await client.delete_message(ctx.message)
            return await client.say(mesg)

        elif ctx.message.author.id == 'USER3':
            mesg = ' '.join(args)
            await client.delete_message(ctx.message)
            return await client.say(mesg)
    except:
        await client.say("You do not have permission to use this command...")

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
    try:
        posts = post.subreddit(arg).hot()
        pick_post = random.randint(1, 21)
        for i in range (0, pick_post):
            sub = next(x for x in posts if not x.stickied)

        await client.say(sub.url)
    except:
        await client.say("This subreddit does not exist...")

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
    try:
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
    except:
        await client.say("The user you put in doesn't have data/does not exist...")



@client.command()
async def FNstats(arg):
    """Gets stats from Fortnite for a user"""
    try:
        player = fortnite.player(arg)
        statsQ = player.getStats(Mode.SQUAD)
        statsD = player.getStats(Mode.DUO)
        statsS = player.getStats(Mode.SOLO)

        embed = discord.Embed(
            title='Fortnite Stats',
            colour=discord.Colour.dark_purple()
        )

        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/409895347687522307/483009396616462356/FortniteClient-Win64-Shipping_123.png')
        embed.add_field(name='Name:', value=arg, inline=False)
        embed.add_field(name='Squad Wins:', value=statsQ.wins, inline=True)
        embed.add_field(name='Squad Kills:', value=statsQ.kills, inline=True)
        embed.add_field(name='Duo Wins:', value=statsD.wins, inline=True)
        embed.add_field(name='Duo KIlls:', value=statsD.kills, inline=True)
        embed.add_field(name='Solo Wins:', value=statsS.wins, inline=True)
        embed.add_field(name='Solo KIlls:', value=statsS.kills, inline=True)
        await client.say(embed=embed)
    except:
        await client.say("Oh no! We couldn't get stats for this user, or the user you put in doesn't exist...")
        
@client.command()
async def FNstatsPSN(arg):
    """Gets stats from Fortnite for a user"""
    try:
        player = fortnite.player(arg, Platform.PSN)
        statsQ = player.getStats(Mode.SQUAD)
        statsD = player.getStats(Mode.DUO)
        statsS = player.getStats(Mode.SOLO)

        embed = discord.Embed(
            title='Fortnite Stats',
            colour=discord.Colour.dark_purple()
        )

        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/409895347687522307/483009396616462356/FortniteClient-Win64-Shipping_123.png')
        embed.add_field(name='Name:', value=arg, inline=False)
        embed.add_field(name='Squad Wins:', value=statsQ.wins, inline=True)
        embed.add_field(name='Squad Kills:', value=statsQ.kills, inline=True)
        embed.add_field(name='Duo Wins:', value=statsD.wins, inline=True)
        embed.add_field(name='Duo KIlls:', value=statsD.kills, inline=True)
        embed.add_field(name='Solo Wins:', value=statsS.wins, inline=True)
        embed.add_field(name='Solo KIlls:', value=statsS.kills, inline=True)
        await client.say(embed=embed)
    except:
        await client.say("Oh no! We couldn't get stats for this user, or the user you put in doesn't exist...")

@client.command()
async def FNstatsXBOX(arg):
    """Gets stats from Fortnite for a user"""
    try:
        player = fortnite.player(arg, Platform.XBOX)
        statsQ = player.getStats(Mode.SQUAD)
        statsD = player.getStats(Mode.DUO)
        statsS = player.getStats(Mode.SOLO)

        embed = discord.Embed(
            title='Fortnite Stats',
            colour=discord.Colour.dark_purple()
        )

        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/409895347687522307/483009396616462356/FortniteClient-Win64-Shipping_123.png')
        embed.add_field(name='Name:', value=arg, inline=False)
        embed.add_field(name='Squad Wins:', value=statsQ.wins, inline=True)
        embed.add_field(name='Squad Kills:', value=statsQ.kills, inline=True)
        embed.add_field(name='Duo Wins:', value=statsD.wins, inline=True)
        embed.add_field(name='Duo KIlls:', value=statsD.kills, inline=True)
        embed.add_field(name='Solo Wins:', value=statsS.wins, inline=True)
        embed.add_field(name='Solo KIlls:', value=statsS.kills, inline=True)
        await client.say(embed=embed)
    except:
        await client.say("Oh no! We couldn't get stats for this user, or the user you put in doesn't exist...")


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

#weather
@client.command()
async def weather(arg):
    """Gets the weather for a location"""
    try:
        weather = Weather(unit=Unit.FAHRENHEIT)
        location = weather.lookup_by_location(arg)
        condition = location.condition
        date = condition.date
        text = condition.text
        temp = condition.temp

        C = (float(temp) - 32) * 5 / 9

        embed = discord.Embed(
            title='Weather',
            colour=discord.Colour.dark_blue()
        )

        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/412949621069840384/482633254227279882/d06.png')
        embed.add_field(name='Location:', value=arg, inline=False)
        embed.add_field(name='Date:', value=date, inline=False)
        embed.add_field(name='Weather:', value=text, inline=False)
        embed.add_field(name='Temp(F):', value=temp + ' F', inline=False)
        embed.add_field(name='Temp(C):', value=str(round(C)) + ' C', inline=False)
        await client.say(embed=embed)
    except:
        await client.say("The location you put in didn't have data, sorry!")


DISCORD = os.environ.get('DISCORD_KEY')
client.run(DISCORD)

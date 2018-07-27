import discord
from discord.ext import commands
import async
import youtube_dl
import random
import requests as req
import asyncio
import time
import praw
import hypixel

client = commands.Bot("!")

players = {}
queues = {}

def check_queue(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()

#APIs

reddit = praw.Reddit(client_id='',
                     client_secret='',
                     user_agent='')

@client.event
async def on_ready():
    print("Bot online")
    await client.change_presence(game=discord.Game(name='Camping with dj :D'))

@client.command(pass_context=True)
async def coin(ctx):
    choice = random.randint(1, 2)
    if choice == 1:
        await client.say("It landed on Tails!")
    if choice == 2:
        await client.say("It landed on Heads!")

#Music

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    await client.say("Music has been added!")
    players[server.id] = player
    player.start()

@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()

@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

@client.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    players[id].stop()

@client.command(pass_context=True)
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    await client.say('The song has been queued!')

#Random Vids

@client.command(pass_context=True)
async def vid(ctx):
    choice1 = ("https://youtu.be/4KigFRmr8qM?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice2 = ("https://youtu.be/8B4eQ1_kDlE?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice3 = ("https://youtu.be/JadDYTwo41w?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice4 = ("https://youtu.be/io7aaCUrFoY?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice5 = ("https://youtu.be/Yy-hwVWAq_Q?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice6 = ("https://youtu.be/ErYRZ66jS1A?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice7 = ("https://youtu.be/aSx404Gotos?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice8 = ("https://youtu.be/7hZrl57_C9Q?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice9 = ("https://youtu.be/q5fT2nwYF-8?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice10 = ("https://youtu.be/Ie_SwhgCMb8?list=LLmAOVPLaTZTkCBg5mcM0K2Q")
    choice11 = ("https://youtu.be/aTNnQbB-bds?list=LLmAOVPLaTZTkCBg5mcM0K2Q")

    choices = [choice1, choice2, choice3, choice4, choice5, choice6, choice7, choice8, choice9, choice10, choice11]
    result = random.choice(choices)
    await client.say(result)

#Fortnite

@client.command(pass_context=True)
async def whereto():
	places = ["Hero House", "Villain House", "Risky Reels", "Lucky Landing", "China Motel", "New Factories", "Motel", "anywhere you want", "Football Ground", "Between Shifty and Flush", "Container", "Jail", "North of Wailing Woods", "Anarchy Acres", "Dusty Divot", "Fatal Fields", "Flush Factory", "Greasy Grove", "Haunted Hills", "Junk Junction", "Lonely Lodge", "Loot Lake", "Moisty Mire", "Pleasant Park", "Retail Row", "Salty Springs", "Shifty Shafts", "Snobby Shores", "Tilted Towers", "Tomato Town", "Wailing Woods"]
	plc = random.choice(places)
	place = plc.lower()
	if plc == "anywhere you want":
		await client.say("Go " + place)
	else:
		await client.say("Go to " + place)

#Responses

@client.command()
async def whatismilk():
    await client.say('Cereal Sauce')

@client.command(pass_context=True)
async def ping(ctx):
    await client.say("pong")

@client.command(pass_context=True)
async def hello(ctx):
    await client.say("Hi There! :wave:")

@client.command(pass_context=True)
async def idiot(ctx):
    await client.say("You're an idiot!")

@client.command(pass_context=True)
async def suwupreme(ctx):
    await client.say("Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme Supreme")

@client.command(pass_context=True)
async def baka(ctx):
    await client.say("no u")

#Reddit posts

@client.command()
async def cats():
    catpics = reddit.subreddit('cats').hot()
    pick_post = random.randint(1, 11)
    for i in range(0, pick_post):
        sub = next(x for x in catpics if not x.stickied)

    await client.say(sub.url)

@client.command()
async def meirl():
    meirl = reddit.subreddit('me_irl').hot()
    pick_post = random.randint(1, 11)
    for i in range(0, pick_post):
        sub = next(x for x in meirl if not x.stickied)

    await client.say(sub.url)
   
client.run('')

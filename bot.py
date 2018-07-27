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
    choice1 = ("put link here")
    choice2 = ("put link here")
    choice3 = ("put link here")
    choice4 = ("put link here")
    choice5 = ("put link here")
    choice6 = ("put link here")
    choice7 = ("put link here)
    choice8 = ("put link here")
    choice9 = ("put link here")
    choice10 = ("put link here")
    choice11 = ("put link here")

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

import discord
from discord.ext import commands
import os
import logging
import random
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged on as {bot.user.name} in the following guilds!')
    for guild in bot.guilds:
        logger.info(guild.name)

@bot.command(name="mute-roulette", help="Mutes a random user in voice")
async def mute_roulette(ctx: commands.context.Context):
    wait_time = 60
    wait_time_warning = 10
    await ctx.send(f"Welcome to Mute roulette! Starting in {wait_time} seconds...")
    await asyncio.sleep(wait_time - wait_time_warning)

    await ctx.send(f"Mute roulette in {wait_time_warning} seconds...")
    await asyncio.sleep(wait_time_warning)

    # Get a random member in voice
    members = []
    for voice_channel in ctx.guild.voice_channels:
        for member in voice_channel.members:
            members.append(member)
    if not members:
        await ctx.send(f'No winner! Too bad no one was in voice to play with us')
        return
    member = random.choice(members)
    await ctx.send(f"Ding! Ding! Ding! {member.name} wins! Server mute for {wait_time} seconds!")
    
    await member.edit(mute=True)
    await asyncio.sleep(wait_time)
    await member.edit(mute=False)

@bot.command(name="discord-jail", help="Puts a user in jail")
async def mute_roulette(ctx: commands.context.Context, arg):
    timeout_time = 60

    channel = discord.utils.get(ctx.guild.channels, name="discord-jail")
    if not channel:
        await ctx.send(f'Not so fast there {ctx.author.name}, we need a "discord-jail" voice channel to do timeouts.')
        return

    for voice_channel in ctx.guild.voice_channels:
        for member in voice_channel.members:
            if member.name == arg:
                for x in range(timeout_time):
                    try:
                        await member.move_to(channel)
                    except:
                        logger.exception("Exception moving user to voice:")
                    await asyncio.sleep(1)
    
    await ctx.send(f'Not so fast there {ctx.author.name}, user has to be in voice.')
    

@bot.command(name="ping", help="Checks that the bot is up and running")
async def mute_roulette(ctx: commands.context.Context):
    await ctx.send("pong")

bot.run(token)
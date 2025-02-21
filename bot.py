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
    await ctx.send(f"Welcome to Mute Roulette! Starting in {wait_time} seconds...")
    await asyncio.sleep(wait_time - wait_time_warning)

    await ctx.send(f"Mute Roulette in {wait_time_warning} seconds...")
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

@bot.command(name="discord-jail", help="Puts a user in discord-jail, default of 60 seconds")
async def discord_jail(ctx: commands.context.Context, name, timeout_time = 60):
    member = discord.utils.get(ctx.guild.members, name=name)
    if not member or not member.voice.channel:
        await ctx.send(f'Not so fast there {ctx.author.name}, user has to be in the server and in voice.')
        return

    channel = discord.utils.get(ctx.guild.channels, name="discord-jail")
    if not channel:
        await ctx.send(f"Oh look {ctx.author.name}, we don't have a discord-jail voice channel for punishments, let me make one.")
        channel = await ctx.guild.create_voice_channel("discord-jail", category=member.voice.channel.category)

    await ctx.send(f'As you wish {ctx.author.name}, {member.name} has been very bad and is going to discord jail for a punishment of {timeout_time} seconds.')
    for x in range(timeout_time):
        try:
            await member.move_to(channel)
        except:
            logger.exception("Exception moving user to voice:")
        await asyncio.sleep(1)

@bot.command(name="ping", help="Checks that the bot is up and running")
async def ping(ctx: commands.context.Context):
    await ctx.send("pong")

bot.run(token)
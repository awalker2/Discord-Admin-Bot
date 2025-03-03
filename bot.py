import discord
from discord.ext import commands
import os
import logging
import random
import asyncio

handler = discord.utils.setup_logging(level=logging.INFO, root=True)
logger = logging.getLogger(__name__)

token = os.getenv("DISCORD_BOT_TOKEN")
discord_jail_mp3_file = os.getenv("DISCORD_BOT_MP3_JAIL_FILE")
discord_jail_members = {}

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

async def play_audio_in_channel(ctx: commands.context.Context, channel: discord.VoiceChannel, file: str, duration: float):
        # Just start over if already connected to some voice channel
        if not ctx.guild.voice_client:
            await channel.connect()
        else:
            ctx.guild.voice_client.stop()

        # Play the audio for the duration specified
        ctx.guild.voice_client.play((discord.FFmpegPCMAudio(file)))
        await asyncio.sleep(duration)

        # Disconnect when done
        if ctx.guild.voice_client:
            ctx.guild.voice_client.stop()
            await ctx.guild.voice_client.disconnect()

@bot.event
async def on_ready():
    logger.info(f'Logged on as {bot.user.name} in the following guilds:')
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
            # Bot could be in voice playing audio, so do not include in mute roulette
            if member.name != bot.user.name:
                members.append(member)
    if not members:
        await ctx.send(f'No winner! Too bad no one was in voice to play with us')
        return
    member = random.choice(members)
    await ctx.send(f"Ding! Ding! Ding! {member.name} wins! Server mute for {wait_time} seconds!")
    await member.send(f"Ding! Ding! Ding! You win Mute Roulette in {ctx.guild.name}! Server mute for {wait_time} seconds!")
    
    await member.edit(mute=True)
    await asyncio.sleep(wait_time)
    await member.edit(mute=False)


@bot.command(name="discord-jail", help="Puts a user in discord-jail voice channel, default of 60 seconds")
async def discord_jail(ctx: commands.context.Context, name: str, timeout_time = 60):
    member = discord.utils.get(ctx.guild.members, name=name)
    if not member or not member.voice.channel:
        await ctx.send(f'Not so fast there {ctx.author.name}, user has to be in the server and in voice.')
        return
    if discord_jail_members.get(member):
        await ctx.send(f'Not so fast there {ctx.author.name}, user is already in discord jail.')
        return

    jail_channel = discord.utils.get(ctx.guild.channels, name="discord-jail")
    original_channel = member.voice.channel
    if not jail_channel:
        await ctx.send(f"Oh look {ctx.author.name}, we don't have a discord-jail voice channel for punishments, let me make one.")
        jail_channel = await ctx.guild.create_voice_channel("discord-jail", category=member.voice.channel.category)

    await ctx.send(f'As you wish {ctx.author.name}, {member.name} has been very bad and is going to discord jail for a punishment of {timeout_time} seconds.')
    await member.send(f"RIP {member.name}, you have been sent to discord-jail in {ctx.guild.name}, you can leave in {timeout_time} seconds.")
    
    # Put the member in jail and wait before removing their role
    discord_jail_members[member] = jail_channel
    await member.move_to(jail_channel)
    
    # Play the jail audio if it is available
    if discord_jail_mp3_file:
        await play_audio_in_channel(ctx, jail_channel, discord_jail_mp3_file, timeout_time)

    discord_jail_members.pop(member, None)

    try:
        await member.move_to(original_channel)
    except Exception:
        logger.exception("Exception moving user back to original channel:")

    await ctx.send(f'{ctx.author.name}, {member.name} is no longer sentenced to discord jail.')
    await member.send(f"{member.name}, you are no longer sentenced to discord jail in {ctx.guild.name}.")

@bot.event
# This is to keep users in discord-jail in the discord-jail channel if they try to join another channel
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    jail_channel = discord_jail_members.get(member)
    if jail_channel and after.channel and after.channel != jail_channel:
        await member.move_to(jail_channel)


@bot.command(name="ghost-ping", help="Ghost ping a user's DMs")
async def ping(ctx: commands.context.Context, name: str, count: int = 1):
    member = discord.utils.get(ctx.guild.members, name=name)
    if not member:
        await ctx.send(f'Not so fast there {ctx.author.name}, user has to be in the server.')
        return

    for x in range(count):
        message = await member.send(f"👻")
        await message.delete()
        await asyncio.sleep(1)


@bot.command(name="ping", help="Checks that the bot is up and running")
async def ping(ctx: commands.context.Context):
    await ctx.send("pong")


bot.run(token, log_handler=handler)
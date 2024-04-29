import discord
from discord.ext import commands
import asyncio
import yt_dlp 

import os
from dotenv import load_dotenv
load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

#Config for the bot
#=================================================================================
TOKEN = os.getenv("TOKEN")

yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

voice_clients = {}
#=================================================================================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("===========================")
    print(f"{bot.user} is currently idle!")
    print("===========================")
    
@bot.tree.command(name="play", description="play music from youtube link")
async def play(interaction: discord.Interaction, link: str):
    try:
        voice_client = await interaction.user.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:
        await interaction.response.send_message(f"```♫ ➤ Getting Music data...```")
        url = link
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        await interaction.followup.send(f"```♫ ➤ {data['title']}```")
        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
        voice_clients[interaction.guild.id].play(player)
    except Exception as e:
        print(e)

@bot.tree.command(name="stop", description="stop current music")
async def stop(interaction: discord.Interaction):
    try:
        voice_clients[interaction.guild.id].stop()
        await voice_clients[interaction.guild.id].disconnect()
        await interaction.response.send_message(f"```🞮 Program exit```")
    except Exception as err:
        print(err)
   
bot.run(TOKEN)   
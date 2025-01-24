import discord
from discord.ext import commands
import asyncio
import yt_dlp
import os
import random
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Config for the bot
# =================================================================================
TOKEN = os.getenv("TOKEN")

# If there is no token, exit...
if not TOKEN:
    raise ValueError("No TOKEN provided. Please set the TOKEN environment variable.")

yt_dl_options = {
    "format": "bestaudio/best",
    "quiet": True,  # Suppress logs
}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'
}

voice_clients = {}
download_tasks = {}  # To track the current download task
# =================================================================================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("===========================")
    print(f"{bot.user} is currently idle!")
    print("===========================")


#=============================
#PLAY MUSIC

async def play_song(interaction: discord.Interaction, song_url: str, voice_client: discord.VoiceClient):
    """
    Function to play a single song from a URL.
    """
    try:
        loop = asyncio.get_event_loop()

        # Create a task to download the song, if already downloading, it should be handled
        download_task = loop.run_in_executor(None, lambda: ytdl.extract_info(song_url, download=False))
        
        # Store the download task for cancellation later
        download_tasks[interaction.guild.id] = download_task
        
        data = await download_task
        song = data['url']
        await interaction.followup.send(f"```♫ ➤ 𝄞 Now playing: {data['title']}```")
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
        voice_client.play(player)
        while voice_client.is_playing():
            await asyncio.sleep(1)
    except Exception as e:
        print(e)


@bot.tree.command(name="play", description="Play music from a YouTube link")
async def play(interaction: discord.Interaction, youtube_link: str):
    """
    Command to play a single music from a YouTube link.
    """
    try:
        # Join the voice channel
        voice_client = await interaction.user.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:
        await interaction.response.send_message("```♫ ➤ 🌐 Fetching and playing the video...```")

        # Play the single video
        await play_song(interaction, youtube_link, voice_clients[interaction.guild.id])

    except Exception as e:
        print(e)


@bot.tree.command(name="playlist", description="Play music from a YouTube playlist")
async def playlist(interaction: discord.Interaction, youtube_playlist_id: str):
    """
    Command to play music from a YouTube playlist.
    """
    try:
        # Join the voice channel
        voice_client = await interaction.user.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:
        await interaction.response.send_message("```♫ ➤ ⟳ Processing playlist...```")

        # Construct the full playlist URL
        playlist_url = f"https://www.youtube.com/playlist?list={youtube_playlist_id}"

        # Detect if it's a playlist
        playlist_options = yt_dl_options.copy()
        playlist_options['extract_flat'] = True  # Extract metadata only, not media
        playlist_ytdl = yt_dlp.YoutubeDL(playlist_options)

        loop = asyncio.get_event_loop()
        playlist_data = await loop.run_in_executor(None, lambda: playlist_ytdl.extract_info(playlist_url, download=False))

        if 'entries' in playlist_data:  # It's a playlist
            await interaction.followup.send(f"```♫ ➤ 📚 Playing playlist: {playlist_data['title']}```")
            for entry in playlist_data['entries']:
                song_url = entry['url']
                await play_song(interaction, song_url, voice_clients[interaction.guild.id])
        else:  # It's a single video
            await play_song(interaction, playlist_url, voice_clients[interaction.guild.id])

    except Exception as e:
        print(e)


@bot.tree.command(name="stop", description="Stop the current music and cancel downloads")
async def stop(interaction: discord.Interaction):
    """
    Command to stop the current music, cancel download tasks, and disconnect.
    """
    try:
        # Stop any current voice play
        if interaction.guild.id in voice_clients:
            voice_clients[interaction.guild.id].stop()
            await interaction.response.send_message("```🞮 Stopped music playback.```")
        else:
            await interaction.response.send_message("```🞮 No music is currently playing.```")

        # Cancel the ongoing download task (if any)
        if interaction.guild.id in download_tasks:
            task = download_tasks.pop(interaction.guild.id)
            task.cancel()
            await interaction.followup.send("```🞮 Download task cancelled.```")

        # Disconnect from the voice channel
        if interaction.guild.id in voice_clients:
            await voice_clients[interaction.guild.id].disconnect()
            voice_clients.pop(interaction.guild.id, None)  # Remove voice client entry
            
        await interaction.followup.send("```Goodbye! ⸜(｡ ˃ ᵕ ˂ )⸝♡```")

    except Exception as err:
        print(f"Error in /stop command: {err}")

#=============================
#RANDOM ROOM CREATIONS

active_magical_channel = None

# Default portal channel name
PORTAL_NAME = '🪞Portal'

# Magical theme channel names
CHANNEL_NAMES = [
    '🏫 Mysthaven Institute',
    '📚 The Ethernal Archive',
    '🏡 Emberwood Village',
    '🌸 Moonblossom Boutique',
    '🚂 Moonshadow Terminal',
    '⚙️ Emberforge Steelworks',
    '🚗 Moonshadow Lane',
    '✨️ Dreamweaver Ways',
    '⚓ Silverwave Pier',
    '🏠 Verdant Hollow',
    '⛰️ Whispering Abyss',
    '🌊 Celestia Harbor',
    '🍹 Arcane Island',
    '🏰 Spectral Spire',
    '🧱 Forsaken Labyrinth',
]

@bot.event
async def on_voice_state_update(member, before, after):
    global active_magical_channel

    guild = member.guild
    portal_channel = discord.utils.get(guild.voice_channels, name=PORTAL_NAME)

    category_name = "🔮 AETHERIA DOMAIN"
    category = discord.utils.get(guild.categories, name=category_name)

    if not category:
        print(f"Category '{category_name}' not found!")
        return

    # Case 1: First user joins -> create new portal
    if portal_channel and after.channel == portal_channel:
        magical_channel_name = random.choice(CHANNEL_NAMES)
        magical_channel = await guild.create_voice_channel(magical_channel_name, category=category)
        active_magical_channel = magical_channel.id
        
        print(f"Created magical channel: {magical_channel_name} under category {category_name}")

        try:
            await member.move_to(magical_channel)
        except discord.errors.HTTPException as e:
            print(f"Error moving user: {e}")

        await portal_channel.delete()
        print("Deleted 'Portal' channel.")
        return

    # Case 2: User leaves the active magical channel
    if active_magical_channel:
        magical_channel = guild.get_channel(active_magical_channel)
        if magical_channel and len(magical_channel.members) == 0:
            await magical_channel.delete()
            active_magical_channel = None
            print(f"Deleted magical channel: {magical_channel.name}")

            # Recreate the '🪞Portal' channel
            await guild.create_voice_channel(PORTAL_NAME, category=category)
            print("Recreated 'Portal' channel.")

bot.run(TOKEN)

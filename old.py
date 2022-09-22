# Imports
try:
    import nextcord
    from nextcord.ext import commands, tasks
    from links import *
    from utils.responses import *
    from dotenv import load_dotenv
    import os
    import random
    import calendar
    import pytz
    import datetime
    import asyncio
    import regex
    import praw
    import pytube
    import imdb
    import requests
    import urllib.request
    import youtube_dl
    import wikipedia
    import googlesearch
    from cryptography.fernet import Fernet
    print("All modules and libraries imported.")
except ImportError as ie:
    print(ie)

# Setup
prefixes = ["t!", "_"]
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix=[prefix for prefix in prefixes],
    intents=intents,
    case_insensitive=True,
)
color = nextcord.Color.from_rgb(223, 31, 45)
bot.remove_command("help")

# Enviroment Variables
global auth
load_dotenv(".env")


# Audio
server_index = {}
FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
ydl_op = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }
    ],
}

# Reddit
reddit = praw.Reddit(
    client_id=os.getenv("reddit_client_id"),
    client_secret=os.getenv("reddit_client_secret"),
    user_agent=os.getenv("reddit_user_agent"),
    username=os.getenv("reddit_username"),
    password=os.getenv("reddit_userpass")
)
default_topic = {}

# Key for ED
key = Fernet.generate_key()
cipher = Fernet(key)

# Snipe, Number of requests, timezone (default), help page number, quip list
deleted_messages, num, default_tz, help_toggle, dialogue_list = {}, 0, "Asia/Kolkata", 0, []

# ---------------------------------------------- NON ASYNC FUNCTIONS -----------------------------------------

def help_menu():
    global help_toggle

    embed_help_menu = nextcord.Embed(title="🕸𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗠𝗲𝗻𝘂🕸", description="Prefixes: `_` `t!`", color=color)
    embed_help_menu.set_thumbnail(url=random.choice(url_thumbnails))
    embed_help_menu.set_footer(text="New Features Coming Soon ⚙️")

    if help_toggle == 0 or help_toggle < 0:
        help_toggle = 0
        embed_help_menu.add_field(
            name="Standard",
            value="`_hello` to greet bot\n`_help` to get this menu\n`_gif` or `_img `to see cool spiderman photos and GIFs\n`_quips` to get a famous dialogue\n`@Thwipper` to get more info about thwipper",
            inline=False
        )
        embed_help_menu.set_image(url=bot.user.avatar.url)
    if help_toggle == 1:
        embed_help_menu.add_field(
            name="The Web",
            value="`_wiki topic` for wikipedia\n`_g topic` to google\n`_imdb movie` to get movie details from IMDb\n `_reddit topic` to get reddit memes",
            inline=False
        )
        embed_help_menu.set_image(url=help_page1)
    if help_toggle == 2:
        embed_help_menu.add_field(
            name="Shells",
            value="`_; query` to running simple queries\n`_py expression` for running simple code\n`_pydoc function` to get information about that python function",
            inline=False
        )
        embed_help_menu.add_field(
            name="Notes",
            value="Functions, when using `pydoc` command, will not be executed. Try without `()`.\nThere is a test database connected with the SQL command, so you can run whatever queries you like.",
            inline=False
        )
        embed_help_menu.set_image(url=help_page2)
    if help_toggle == 3:
        embed_help_menu.add_field(
            name="Encrypter Decrypter",
            value="`_hush en text`to encrypt message\n`_hush dec text` to decrypt message\n",
            inline=False,
        )
        embed_help_menu.set_image(url=help_page3)
    if help_toggle == 4:
        embed_help_menu.add_field(
            name="Spider-Punk Radio™\n\nVoice Controls",
            value="🔉 `_cn` to get the bot to join voice channel\n🔇 `_dc` to remove bot from voice channel",
            inline=False,
        )
        embed_help_menu.add_field(
            name="Player Controls",
            value="🎶 `_p name/index` to play songs\n▶ `_res` to resume a song\n⏸ `_pause` to pause a song\n⏹ `_st` to stop a song\n🔂 `_rep` to repeat song\n⏭ `_skip` to skip song\n⏮ `_prev` for previous song",
            inline=False
        )
        embed_help_menu.add_field(
            name="Queue Controls",
            value="🔼 `_q` scroll queue `up`\n🔽 `_q` scroll queue `down`\n🔠 `_lyrics name` to display current song's lyrics\n*️⃣ `_songinfo` to get current song's info\n✅ `_q name` to add a song to the queue\n❌ `_rem index` to remove song from queue\n💥 `_cq` to clear queue",
            inline=False
        )
        embed_help_menu.set_image(url=help_page4)
    if help_toggle == 5:
        embed_help_menu.add_field(
            name="Birthdays",
            value="`_addbday mention month day` to add a member's birthday\n`_bday` to get thwipper to wish the members of your server\n`_rembday mention` to remove a member's birthday",
            inline=False
        )
        embed_help_menu.set_image(url=help_page5)
    if help_toggle == 6 or help_toggle > 6:
        help_toggle = 6
        embed_help_menu.add_field(
            name="Utility",
            value="`_req` to get number of used commands\n`_web` to see deleted message\n`_ping` to get bot's latency\n`_serverinfo` to get server's information\n`_pfp mention` to get user's profile picture\n`_setbit` to set quality of bitrate\n`_polls` to see how to conduct a poll\n`_dt timezone` to get date and time\n`_cal year month` to get calendar",
            inline=False
        )
        embed_help_menu.add_field(
            name="Notes",
            value="The default timezone for `_dt` is set as `Asia/Kolkata`. Check above on how to get date time of your timezone.",
            inline=False
        )
        embed_help_menu.set_image(url=help_page6)
    return embed_help_menu

def time_converter(seconds):
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    # return "%d hrs %02d mins %02d secs" % (hours, mins, secs)
    if hours == 0: 
        return "%02d mins %02d secs" % (mins, secs)
    if hours > 0: 
        if len(str(secs)) == 1:
            secs = "0" + str(secs)
            return "%d hrs %02d mins %02d secs" % (hours, mins, secs)

def youtube_download(ctx, url):
    if True:
        with youtube_dl.YoutubeDL(ydl_op) as ydl:
            URL = ydl.extract_info(url, download=False)["formats"][0]["url"]
    return URL

def requests_query():
    global cursor
    operation = "INSERT INTO requests(number)VALUES({})".format(num)
    cursor.execute(operation)

def number_of_requests():
    global num  # num = 0
    num += 1
    requests_query()

def play_music(voice, URL_queue):
    voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))

# ----------------------------------------- EVENTS --------------------------------------

@bot.event
async def on_ready():
    print("{0.user} is now online.".format(bot))
    stop = 0

    # QUIPS
    global dialogue_list
    site = (
        requests.get("https://geektrippers.com/spiderman-quotes/")
        .content.decode()
        .replace("<br>", "\n")
        .replace("<strong>", " ")
        .replace("</strong>", " ")
        .replace("<em>", " ")
        .replace("</em>", " ")
        .replace("&#8217;", "'")
        .replace("&#8221;", '"\n\r')
        .replace("&#8230;", "...")
        .replace("&#8220;", '"')
        .replace("&nbsp;", " ")
        .replace("&#8211;", "-")
        .replace("&#8216;", "'")
        .replace("]", "]\n")
        .replace("[", "\n[")
    )

    for i in range(0, 1000):
        q = site.find('<p class="has-background" style="background-color:#dedfe0">', stop) + len('<p class="has-background style="background-color:#dedfe0">')
        w = site.find("</p>", stop)
        stop = w + len("</p>")
        dialogues = ""
        if not site[q:w]: 
            continue
        else:
            dialogues = site[q:w]
            dialogue_list += [dialogues]

    # STATUSES
    @tasks.loop(minutes=10)
    async def multiple_statuses():
        while True:
            for status in status_list:
                await asyncio.sleep(300)
                await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=status))
    multiple_statuses.start()

    # UPDATION
    @tasks.loop(seconds=5.0)
    async def updation():
        # REQUESTS UPDATE
        global cursor
        global num
        op = "SELECT MAX(number) FROM requests"
        cursor.execute(op)
        req1 = cursor.fetchall()
        req2 = str(req1).replace("[(", " ").replace(",)]", " ")
        num = int(req2)
        conn.commit()
    updation.start()
 
@bot.event
async def on_message(message):
    if f"<@{bot.user.id}>" == message.content:
        number_of_requests()
        embed = nextcord.Embed(
            title="Your friendly neighborhood spider-bot",
            description=f"Hi {message.author.name}!\nI am `Thwipper`. My name comes from the onomatopoeia of Spider-Man's Webshooters. Pretty slick, eh? I have lots of cool features that you may find interesting. Check them out with `_help` command. As always, more exciting features are always in the works. Stay tuned and have fun with them.\n_Excelsior!_",
            color=color
        )
        embed.add_field(name="Made by", value="[Tamonud](https://www.github.com/spidey711)", inline=True)
        embed.add_field(name="Source Code", value="[Github Repo](https://www.github.com/spidey711/Thwipper-bot)", inline=True)
        embed.set_thumbnail(url=bot.user.avatar.url)
        await message.reply(embed=embed)
    else:
        await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if not message.channel.id in list(deleted_messages.keys()): 
        deleted_messages[message.channel.id] = []
    if len(message.embeds) <= 0: 
        deleted_messages[message.channel.id].append((str(message.author.id), message.content))
    else: 
        deleted_messages[message.channel.id].append((str(message.author.id), message.embeds[0], True))

@bot.event
async def on_reaction_add(reaction, user):
    number_of_requests()
    if not user.bot:
        
        if reaction.emoji == "🖱":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
            try:
                sub = reddit.subreddit(default_topic[str(reaction.message.guild.id)]).random()
                embed = nextcord.Embed(description=f"**Caption:\n**{sub.title}", color=color)
                embed.set_author(name=f"Post by: {sub.author}", icon_url=url_reddit_author)
                # embed.set_thumbnail(url=url_reddit_thumbnail)
                embed.set_image(url=sub.url)
                embed.set_footer(text=f"🔺: {sub.ups}   🔻: {sub.downs}   💬: {sub.num_comments}")
                await reaction.message.edit(embed=embed)
            except Exception:
                embed = nextcord.Embed(description="Default topic is not set", color=color)
                embed.set_author(name="Uh oh...", icon_url=url_reddit_author)
                await reaction.message.edit(embed=embed)


        global help_toggle
        if reaction.emoji == "➡":
            help_toggle += 1
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                await reaction.message.edit(embed=help_menu())


        if reaction.emoji == "⬅":
            help_toggle -= 1
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                await reaction.message.edit(embed=help_menu())


        if reaction.emoji == "🕸":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)

                embed = nextcord.Embed(title="🕸Mutual Guilds🕸", description="\n".join([servers.name for servers in user.mutual_guilds]), color=color)
                embed.set_thumbnail(url=random.choice(url_thumbnails))
                embed.set_footer(text="New Features Coming Soon 🛠")
                await reaction.message.edit(embed=embed)


        # MUSIC PLAYER
        voice = nextcord.utils.get(bot.voice_clients, guild=reaction.message.guild)
        voice_client = reaction.message.guild.voice_client
        if not voice_client:
            return 
        playing = reaction.message.guild.voice_client.is_playing()
        pause = reaction.message.guild.voice_client.is_paused()

        # SERVER QUEUE
        operation_view = f"SELECT song_name, song_url FROM music_queue WHERE server={str(reaction.message.guild.id)}"
        cursor.execute(operation_view)
            # due to enumerate() in below line, some reactions may stop working, I'll fix them soon
        server_queue = list(enumerate(cursor.fetchall(), start=0)) #song[0] is counter, song[1] is (name, url)
        members_in_vc = [str(names) for names in reaction.message.guild.voice_client.channel.members]
        string = ""


        if reaction.emoji == "🔇":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if members_in_vc.count(str(user)) > 0:
                    try:        
                        if voice_client.is_connected():
                            embed = nextcord.Embed(description=f"Disconnected from {reaction.message.guild.voice_client.channel.name}", color=color)
                            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                            embed.set_footer(text=random.choice(disconnections))
                            await reaction.message.edit(embed=embed)
                            await voice_client.disconnect()
                    except AttributeError:
                        embed = nextcord.Embed(description="I am not connected to a voice channel", color=color)
                        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description="Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)


        # under works
        if reaction.emoji == "🔼":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                
    
        # under works
        if reaction.emoji == "🔽":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)


        # under works                        
        if reaction.emoji == "🔠":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                embed = nextcord.Embed(description="Working on lyrics...", color=color)
                embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                await reaction.message.edit(embed=embed)


        if reaction.emoji == "▶":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if members_in_vc.count(str(user)) > 0:
                    try:
                        if server_index[str(reaction.message.guild.id)] is not None:
                            if pause == True:
                                voice_client.resume()
                                embed = nextcord.Embed(description="Song has resumed playing 🎸", color=color)
                                embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                                embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                                await reaction.message.edit(embed=embed)
                            else:
                                if playing == True:
                                    embed = nextcord.Embed(description="Song is not paused 🤔", color=color)
                                else:
                                    embed = nextcord.Embed(description="Nothing is playing right now ❗", color=color)
                                embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                                embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                                await reaction.message.edit(embed=embed)
                        else:
                            if playing != True:
                                voice_client.resume()
                                embed = nextcord.Embed(description="Song has resumed playing ▶", color=color)
                            else:
                                embed = nextcord.Embed(description="Song is already playing 🎸", color=color)
                            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                            embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                            await reaction.message.edit(embed=embed)
                    except Exception as e:
                        embed = nextcord.Embed(description=str(e), color=color)
                        embed.set_author(name="Error", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description=f"Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)


        if reaction.emoji == "⏸":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if members_in_vc.count(str(user)) > 0:
                    try:
                        if playing == True:
                            voice_client.pause()
                            embed = nextcord.Embed(description="Song is paused ⏸", color=color)
                            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                            embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                            await reaction.message.edit(embed=embed)
                        else:
                            if pause == True:
                                embed = nextcord.Embed(description="Song is already paused ⏸", color=color)
                            else:
                                embed = nextcord.Embed(description="No song playing currently ❗", color=color)
                            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                            embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                            await reaction.message.edit(embed=embed)
                    except Exception as e:
                        embed = nextcord.Embed(description=str(e), color=color)
                        embed.set_author(name="Error", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description=f"Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)


        if reaction.emoji == "⏮":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                server_index[str(reaction.message.guild.id)] -= 1
                if members_in_vc.count(str(user)) > 0:
                    try:
                        URL_queue = youtube_download(reaction.message, server_queue[server_index[str(reaction.message.guild.id)]][1])
                        if playing != True:
                            pass
                        else:
                            voice.stop()
                        embed = nextcord.Embed(description="**Song: **{a}\n**Queue Index: **{b}".format(a=server_queue[server_index[str(reaction.message.guild.id)]][0], b=server_index[str(reaction.message.guild.id)],).replace(" - YouTube", " "), color=color,)
                        embed.set_author(name="Now playing", icon_url=url_author_music)
                        embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).thumbnail_url)
                        embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).author, inline=True)
                        embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).length), inline=True)
                        embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                        await reaction.message.edit(embed=embed)
                        voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))
                        
                    except IndexError:
                        embed = nextcord.Embed(description="Looks like there is no song at this index", color=color)
                        embed.set_author(name="Oops...", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description=f"Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)


        if reaction.emoji == "⏭":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                server_index[str(reaction.message.guild.id)] += 1
                if members_in_vc.count(str(user)) > 0:
                    try:
                        URL_queue = youtube_download(reaction.message, server_queue[server_index[str(reaction.message.guild.id)]][1])
                        if playing != True:
                            pass
                        else:
                            voice.stop()
                        embed = nextcord.Embed(description="**Song: **{a}\n**Queue Index: **{b}".format(
                            a=server_queue[server_index[str(reaction.message.guild.id)]][0], 
                            b=server_index[str(reaction.message.guild.id)]).replace(" - YouTube", " "), 
                            color=color
                        )
                        embed.set_author(name="Now Playing", icon_url=url_author_music)
                        embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).thumbnail_url)
                        embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).author, inline=True)
                        embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).length), inline=True)
                        embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                        await reaction.message.edit(embed=embed)
                        voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))

                    except IndexError:
                        embed = nextcord.Embed(description="Looks like there is no song at this index", color=color)
                        embed.set_author(name="Oops...", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description=f"Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)


        if reaction.emoji == "⏹":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if members_in_vc.count(str(user)) > 0:
                    try:
                        if playing == True or pause == True:
                            voice_client.stop()
                            embed = nextcord.Embed(description="Song has been stopped ⏹", color=color)
                        else:
                            embed = nextcord.Embed(description="Nothing is playing at the moment❗", color=color)
                        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                        embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(reaction.message.guild.voice_client.channel.bitrate/1000))
                        await reaction.message.edit(embed=embed)
                    except Exception as e:
                        embed = nextcord.Embed(description=str(e), color=color)
                        embed.set_author(name="Error", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description=f"Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)


        if reaction.emoji == "*️⃣":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if len(server_queue) <= 0:
                    embed = nextcord.Embed(description=random.choice(empty_queue), color=color)
                    embed.set_author(name="Uh oh...", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)
                else:    
                    try:   
                        try:
                            embed = nextcord.Embed(
                                description="**Song: **{a}\n**Index: **{b}\n**Views: **{c}\n**Description: **\n{d}".format(
                                    a=server_queue[server_index[str(reaction.message.guild.id)]][0],
                                    b=server_index[str(reaction.message.guild.id)],
                                    c=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).views,
                                    d=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).description),
                                color=color
                            )
                            embed.set_author(name="Currently Playing", url=server_queue[server_index[str(reaction.message.guild.id)]][1], icon_url=url_author_music)
                            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(reaction.message.guild.voice_client.channel.bitrate/1000))
                            embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).thumbnail_url)
                            await reaction.message.edit(embed=embed)
                        # if description crosses embed length
                        except nextcord.errors.HTTPException: 
                            embed = nextcord.Embed(description="**Song: **{a}\n**Index: **{b}\n**Views: **{c}\n**Description: **\n{d}".format(
                                    a=server_queue[server_index[str(reaction.message.guild.id)]][0],
                                    b=server_index[str(reaction.message.guild.id)],
                                    c=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).views,
                                    d=random.choice(description_embed_errors)),
                                color=color
                            )
                            embed.set_author(name="Currently Playing", url=server_queue[server_index[str(reaction.message.guild.id)]][1], icon_url=url_author_music)
                            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(reaction.message.guild.voice_client.channel.bitrate/1000))
                            embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).thumbnail_url)
                            await reaction.message.edit(embed=embed) 
                    except KeyError:
                        embed = nextcord.Embed(description=random.choice(default_index), color=color)
                        embed.set_author(name="Uh oh...", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)


        if reaction.emoji == "🔂":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if members_in_vc.count(str(user)) > 0:
                    try:
                        URL_queue = youtube_download(reaction.message, server_queue[server_index[str(reaction.message.guild.id)]][1])
                        if reaction.message.guild.voice_client.is_playing() != True:
                            pass
                        else:
                            voice.stop()
                        embed = nextcord.Embed(description="**Song: **{}".format(server_queue[server_index[str(reaction.message.guild.id)]][0]).replace(" - YouTube", " "), color=color)
                        embed.set_author(name="Repeating Song", icon_url=url_author_music)
                        embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).thumbnail_url)
                        embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).author, inline=True)
                        embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[server_index[str(reaction.message.guild.id)]][1]).length), inline=True)
                        embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(reaction.message.guild.voice_client.channel.bitrate/1000))
                        await reaction.message.edit(embed=embed)
                        voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))
                    
                    except Exception as e:
                        embed = nextcord.Embed(description=str(e), color=color)
                        embed.set_author(name="Error", icon_url=url_author_music)
                        await reaction.message.edit(embed=embed)
                else:
                    embed = nextcord.Embed(description=f"Connect to the voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)
        
        
        if reaction.emoji == "🔀":
            if str(user) != str(bot.user) and reaction.message.author == bot.user:
                await reaction.remove(user)
                if members_in_vc.count(str(user)) > 0:
                    # choosing a random song
                    random_song = random.choice(server_queue)
                    queue_index = server_index[str(reaction.message.guild.id)]
                    for index in range(len(server_queue)):
                        if random_song == server_queue[index]:
                            # random song has set index
                            queue_index = int(index) 
                    # setting server index to new randomly chosen index
                    server_index[str(reaction.message.guild.id)] = queue_index
                    URL_shuffle = youtube_download(reaction.message, random_song[1])
                    if reaction.message.guild.voice_client.is_playing() != True:
                        pass
                    else:
                        voice.stop()
                    embed = nextcord.Embed(description=f"**Song: **{random_song[0]}\n**Queue Index: **{queue_index}".replace(" - YouTube", " "), color=color)
                    embed.set_author(name="Shuffle Play", icon_url=url_author_music)
                    embed.set_thumbnail(url=pytube.YouTube(url=random_song[1]).thumbnail_url)
                    embed.add_field(name="Uploader", value=pytube.YouTube(url=random_song[1]).author, inline=True)
                    embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=random_song[1]).length), inline=True)
                    embed.set_footer(text=f"Voice Channel Bitrate: {reaction.message.guild.voice_client.channel.bitrate/1000} kbps")
                    await reaction.message.edit(embed=embed)
                    voice.play(nextcord.FFmpegPCMAudio(URL_shuffle, **FFMPEG_OPTS))
                
                else:
                    embed = nextcord.Embed(description=f"Connect to a voice channel first 🔊", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    await reaction.message.edit(embed=embed)

# ---------------------------------------------- STANDARD ----------------------------------------------------

@bot.command(aliases=["hello", "hi", "hey", "hey there", "salut", "kon'nichiwa", "hola", "aloha"])
async def greet_bot(ctx):
    number_of_requests()

    greetings = [f"Hey {ctx.author.name}!", f"Hi {ctx.author.name}!", f"How's it going {ctx.author.name}?", f"What can I do for you {ctx.author.name}?", f"What's up {ctx.author.name}?", f"Hello {ctx.author.name}!", f"So {ctx.author.name}, how's your day going?"]
    await ctx.send(random.choice(greetings))


@bot.command(aliases=["img", "gif"])
async def sendCoolPhotos(ctx):
    number_of_requests()
    
    embed = nextcord.Embed(color=color)
    embed.set_author(name="", icon_url=ctx.author.avatar.url)
    embed.set_image(url=random.choice(hello_urls))
    await ctx.send(embed=embed)


@bot.command(aliases=["help", "use"])
async def embed_help(ctx):
    number_of_requests()
    
    message = await ctx.send(embed=help_menu())
    await message.add_reaction("⬅")
    await message.add_reaction("🕸")
    await message.add_reaction("➡")


@bot.command(aliases=["quips"])
async def get_quips(ctx):
    number_of_requests()

    try:
        embed = nextcord.Embed(title=random.choice(titles), description=random.choice(dialogue_list), color=color)
        embed.set_thumbnail(url=random.choice(url_thumbnails))
        embed.set_footer(text=random.choice(footers), icon_url=bot.user.avatar.url)
        await ctx.send(embed=embed)
        print("Quip successfully sent!")

    except Exception as e:
        embed = nextcord.Embed(title="Error", description=str(e), color=color)

# ----------------------------------------------- INTERNET ---------------------------------------------

@bot.command(aliases=["imdb"])
async def IMDb_movies(ctx, *, movie_name=None):
    number_of_requests()

    if movie_name is None:
        embed = nextcord.Embed(description=random.choice(imdb_responses), color=color)
        embed.set_author(name="Ahem ahem", icon_url=url_imdb_author)
        await ctx.send(embed=embed)

    if movie_name is not None:
        try:
            db = imdb.IMDb()
            movie = db.search_movie(movie_name)
            title = movie[0]["title"]
            movie_summary = (
                db.get_movie(movie[0].getID()).summary()
                .replace("=", "")
                .replace("Title", "**Title**")
                .replace("Movie", "")
                .replace("Genres", "**Genres**")
                .replace("Director", "**Director**")
                .replace("Writer", "**Writer(s)**")
                .replace("Cast", "**Cast**")
                .replace("Country", "**Country**")
                .replace("Language", "**Language**")
                .replace("Rating", "**Rating**")
                .replace("Plot", "**Plot**")
                .replace("Runtime", "**Runtime (mins)**")
            )
            movie_cover = movie[0]["full-size cover url"]
            embed = nextcord.Embed(title="🎬 {} 🍿".format(title), description=movie_summary, color=color)
            embed.set_thumbnail(url=url_imdb_thumbnail)  # 🎥 🎬 📽
            embed.set_image(url=movie_cover)
            await ctx.send(embed=embed)
        
        except Exception:
            embed = nextcord.Embed(description="I couldn't find `{}`.\nTry again and make sure you enter the correct movie name.".format(movie_name), color=color)
            embed.set_author(name="Movie Not Found 💬", icon_url=url_imdb_author)
            await ctx.send(embed=embed)


@bot.command(aliases=["reddit", "rd"])
async def reddit_memes(ctx, *, topic):
    number_of_requests()
    
    sub = reddit.subreddit(topic).random()
    if str(ctx.guild.id) not in default_topic:
        default_topic[str(ctx.guild.id)] = str(topic)
    if str(ctx.guild.id) in default_topic:
        default_topic[str(ctx.guild.id)] = str(topic)

    try:
        embed = nextcord.Embed(description="**Caption:\n**{}".format(sub.title), color=color)
        embed.set_author(name="Post by: {}".format(sub.author), icon_url=url_reddit_author)
        # embed.set_thumbnail(url=url_reddit_thumbnail)
        embed.set_image(url=sub.url)
        embed.set_footer(text="🔺: {}   🔻: {}   💬: {}".format(sub.ups, sub.downs, sub.num_comments))
        message = await ctx.send(embed=embed)
        await message.add_reaction("🖱")
    except Exception:
        default_topic[str(ctx.guild.id)] = ""
        embed = nextcord.Embed(description="Looks like the subreddit is either banned or does not exist 🤔", color=color)
        embed.set_author(name="Subreddit Not Found", icon_url=url_reddit_author)
        await ctx.send(embed=embed)


@bot.command(aliases=["wiki", "w"])
async def wikipedia_results(ctx, *, thing_to_search):
    number_of_requests()

    try:
        try:
            title = wikipedia.page(thing_to_search)
            embed = nextcord.Embed(description=wikipedia.summary(thing_to_search), color=color)
            embed.set_author(name=title.title, icon_url=url_wiki)
            embed.add_field(name="Search References", value=", ".join([x for x in wikipedia.search(thing_to_search)][:5]), inline=False)
            embed.set_footer(text="Searched by: {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
            print("Results for wikipedia search sent...")
    
        except wikipedia.PageError as pe:
            embed = nextcord.Embed(description=str(pe), color=color)
            embed.set_author(name="Error", icon_url=url_wiki)
            await ctx.send(embed=embed)    
            
    except wikipedia.DisambiguationError as de:
        embed = nextcord.Embed(description=str(de), color=color)
        embed.set_author(name="Hmm...", icon_url=url_wiki)
        await ctx.send(embed=embed)


@bot.command(aliases=["google", "g"])
async def google_results(ctx, *, thing_to_search):
    number_of_requests()

    results = ""
    for result in googlesearch.search(thing_to_search, 7, "en"):
        results += result + "\n"

    await ctx.send("Search results for: **{}**".format(thing_to_search))
    await ctx.send(results)
    print("Results for google search sent.")

# ------------------------------------------------- UTILITY -------------------------------------------------

@bot.command(aliases=["delete", "del"])
async def clear(ctx, num=10000000000000):
    number_of_requests()

    await ctx.channel.purge(limit=1)
    await ctx.channel.purge(limit=num)


@bot.command(aliases=["[X]"])
async def stop_program(ctx):
    
    voice_client = ctx.message.guild.voice_client
    if ctx.author.id == 622497106657148939:
        conn.commit()
        try:
            await voice_client.disconnect()
        except: 
            pass
        await ctx.send("Alright, see ya!")
        exit()
    else:
        await ctx.send("Access Denied")


@bot.command(aliases=["say"])
async def replicate_user_text(ctx, *, text):
    number_of_requests()

    await ctx.channel.purge(limit=1)
    await ctx.send(text)


@bot.command(aliases=["polls", "poll"])
async def conduct_poll(ctx, emojis=None, title=None, *, description=None):
    number_of_requests()

    poll_channel = None
    for i in ctx.guild.channels:
        for j in poll_channels:
            if i.name == j:
                send_to = i.name = j
                poll_channel = nextcord.utils.get(ctx.guild.channels, name=send_to)
                
    if title is not None:
        if "_" in title:
            title = title.replace("_", " ")
            
    if emojis is not None and title is not None and description is not None:
        embed = nextcord.Embed(title=f"Topic: {title}", description=description, color=color)
        embed.set_footer(text=f"Conducted by: {ctx.author.name}", icon_url=ctx.author.avatar.url)
        message = await poll_channel.send(embed=embed)

        if emojis == "y/n" or emojis == "yes/no":
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        elif emojis == "t/t" or emojis == "this/that":
            await message.add_reaction("👈🏻")
            await message.add_reaction("👉🏻")
        else:
            emojis_list = list(emojis.split(","))
            for emoji in emojis_list:
                await message.add_reaction(emoji)
        if ctx.channel.name != poll_channel:
            await ctx.send(embed=nextcord.Embed(description="Poll Sent Successfully 👍🏻", color=color))
    
    elif title is None and description is None and emojis is None:
        embed = nextcord.Embed( title="Polls", description="Command: `_polls emojis title description`", color=color)
        embed.add_field(name="Details", value="`emojis:` enter emojis for the poll and they will be added as reactions\n`title:` give a title to your poll.\n`description:` tell everyone what the poll is about.", inline=False)
        embed.add_field(name="Notes", value="To add reactions to poll the multiple emojis should be separated by a `,`.\nIf you wish to use default emojis, `y/n` for yes or no and `t/t` for this or that.\nIf the title happens to be more than one word long, use `_` in place of spaces as demonstrated below.\nExample: `The_Ultimate_Choice` will be displayed in the title of poll as `The Ultimate Choice`.", inline=False)
        embed.set_thumbnail(url=random.choice(url_thumbnails))
        await ctx.send(embed=embed)


@bot.command(aliases=["req", "requests"])
async def total_requests(ctx):
    number_of_requests()

    operation = "SELECT MAX(number) FROM requests"
    cursor.execute(operation)
    total = cursor.fetchall()
    embed = nextcord.Embed(description=f"""**Requests Made:\n**{str(total).replace("[(", " ").replace(",)]", " ")}""", color=color)
    await ctx.send(embed=embed)


@bot.command(aliases=["web"])
async def snipe(ctx):
    number_of_requests()

    try:
        message = deleted_messages[ctx.channel.id][-1]
    
        if len(message) < 3:
            embed = nextcord.Embed(title="Deleted Message", description=message[1], color=color)
            embed.set_footer(text=f"Sent by: {bot.get_user(int(message[0]))}", icon_url=bot.get_user(int(message[0])).avatar.url,)
            await ctx.send(embed=embed)
    
        else:
            embed = nextcord.Embed(description="Embed deleted 👇🏻", color=color)
            embed.set_author(name=bot.get_user(int(message[0])), icon_url=bot.get_user(int(message[0])).avatar.url)
            await ctx.send(embed=embed)
            await ctx.send(embed=message[1])    
    
    except KeyError:
        await ctx.send(embed=nextcord.Embed(description="There is nothing to web up 🕸", color=color))


@bot.command(aliases=["pfp"])
async def user_pfp(ctx, member: nextcord.Member = None):
    number_of_requests()

    if member is None:
        embed = nextcord.Embed(title="Profile Picture : {}".format(ctx.author.name), color=color)
        embed.set_image(url=ctx.author.avatar.url)
    
    else:
        embed = nextcord.Embed(title="Profile Picture : {}".format(member.name), color=color)
        embed.set_image(url=member.avatar.url)
    embed.set_footer(text=random.choice(compliments))
    await ctx.send(embed=embed)


@bot.command(aliases=["ping"])
async def get_ping(ctx):
    number_of_requests()

    ping = round(bot.latency * 1000)
    c1 = "🟢"
    c2 = "🟡"
    c3 = "🔴"
    
    if ping >= 350:
        embed = nextcord.Embed(description=f"{c3} {ping} ms", color=color)
        await ctx.send(embed=embed)
    
    elif ping <= 320:
        embed = nextcord.Embed(description=f"{c1} {ping} ms", color=color)
        await ctx.send(embed=embed)
    
    elif ping > 320 and ping < 350:
        embed = nextcord.Embed(description=f"{c2} {ping} ms", color=color)
        await ctx.send(embed=embed)


@bot.command(aliases=["serverinfo", "si"])
async def server_information(ctx):
    number_of_requests()

    name = str(ctx.guild.name)
    ID = str(ctx.guild.id)
    description = str(ctx.guild.description)
    owner = str(ctx.guild.owner)
    region = str(ctx.guild.region)
    num_mem = str(ctx.guild.member_count)
    icon = str(ctx.guild.icon.url if ctx.guild.icon else None)
    role_count = len(ctx.guild.roles)

    embed = nextcord.Embed(title=f"📚 {name} 📚", color=color)
    embed.add_field(name="Owner", value=f"`{owner}`", inline=True)
    embed.add_field(name="Member Count", value=f"`{num_mem}`", inline=True)
    embed.add_field(name="Role Count", value=f"`{role_count}`", inline=True)
    embed.add_field(name="Region", value=f"`{region}`", inline=True)
    embed.add_field(name="Server ID", value=f"`{ID}`", inline=False)
    embed.add_field(name="Description", value=f"```{description}```", inline=False)
    embed.set_footer(text=f"Created on {ctx.guild.created_at.__format__('%A, %B %d, %Y @ %H:%M:%S')}", icon_url=ctx.author.avatar.url)
    embed.set_image(url=icon)
    await ctx.send(embed=embed)

# --------------------------------------- ENCRYPER DECRYPTER ---------------------------------

@bot.command(aliases=["hush"])
async def encrypt_data(ctx, mode, *, message):
    number_of_requests()

    res = message.encode()
    try:
        
        if mode == "en":
            await ctx.channel.purge(limit=1)
            await ctx.send("**Message Encrypted 🔐**\n```{}```".format(str(cipher.encrypt(res).decode('utf-8'))))
        
        if mode == "dec":
            await ctx.channel.purge(limit=1)
            await ctx.send("**Message Decrypted 🔓**\n```{}```".format(str(cipher.decrypt(res).decode('utf-8'))))

    except Exception as error:
        await ctx.send("**Error**\nSorry, I was not able to decode that. Perhaps its already decoded? 🤔\n{}".format(error))

# ------------------------------------- DATE TIME CALENDAR ---------------------------------------------

@bot.command(aliases=["dt"])
async def date_time_ist(ctx, timezone=None):
    number_of_requests()

    embed = nextcord.Embed(color=color)
    if timezone is None:
        tzinfo = pytz.timezone(default_tz)
        embed.set_footer(text=f"Timezone: {default_tz}")
    else:
        tzinfo = pytz.timezone(timezone)
        embed.set_footer(text=f"Timezone: {timezone}")
    dateTime = datetime.datetime.now(tz=tzinfo)
    embed.add_field(name="Date", value="%s/%s/%s" % (dateTime.day, dateTime.month, dateTime.year), inline=True)
    embed.add_field(name="Time", value="%s:%s:%s" % (dateTime.hour, dateTime.minute, dateTime.second), inline=True)
    await ctx.send(embed=embed)


@bot.command(aliases=["cal"])
async def get_calendar(ctx, year, month):
    number_of_requests()
    
    try:
        embed = nextcord.Embed(description="```{}```".format(calendar.month(int(year), int(month))), color=color)
        embed.set_author(name="Calendar")
        await ctx.send(embed=embed)
        
    except IndexError:
        embed = nextcord.Embed(description="{}, this month doesn't exist 📆".format(ctx.author.name), color=color)
        embed.set_author(name="Calendar", icon_url=url_dtc)
        await ctx.send(embed=embed)

# ------------------------------------------ SHELLS --------------------------------------------

@bot.command(aliases=[";"])
async def sql_shell(ctx, *, expression):
    number_of_requests()

    try:
        output = ""
        cursor_test.execute(expression)
        for item in cursor_test.fetchall():
            output += str(item) + "\n"
        if output == "":
            output = "---"
            
        conn_test.commit()
        embed = nextcord.Embed(description=f"**Query**\n{str(expression)}\n**Output**\n{str(output)}", color=color)
        embed.set_author(name="MySQL Shell", icon_url=url_author_sql)
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed_err = nextcord.Embed(title="Error", description=str(e), color=color)
        embed_err.set_author(name="MySQL Shell", icon_url=url_author_sql)
        await ctx.send(embed=embed_err)


@bot.command(aliases=["py"])
async def python_shell(ctx, *, expression):
    number_of_requests()

    if expression in denied or denied[-2] in expression or denied[-1] in expression:
        embed = nextcord.Embed(description=random.choice(denied_responses), color=color)
        embed.set_author(name="Access Denied", icon_url=url_author_python)
        await ctx.send(embed=embed)

    else:
        try:
            embed_acc = nextcord.Embed(description=f"**Input**\n{str(expression)}\n**Output**\n{str(eval(expression))}", color=color)
            embed_acc.set_author(name="Python Shell", icon_url=url_author_python)
            await ctx.send(embed=embed_acc)
        except Exception as e:
            embed_err = nextcord.Embed(title="Error", description=str(e), color=color)
            embed_err.set_author(name="Python Shell", icon_url=url_author_python)
            await ctx.send(embed=embed_err)


@bot.command(aliases=["pydoc"])
async def function_info(ctx, func):
    number_of_requests()

    try:

        if "(" in [char for char in func] and ")" in [char for char in func]:
            embed = nextcord.Embed(description=random.choice(no_functions), color=color)
            embed.set_author(name="Access Denied", icon_url=url_author_python)
            await ctx.send(embed=embed)

        else:
            function = eval(func)
            embed = nextcord.Embed(description=function.__doc__, color=color)
            embed.set_author(name="Info: {}".format(func), icon_url=url_author_python)
            await ctx.send(embed=embed)

    except Exception as e:
        embed = nextcord.Embed(description=str(e), color=color)
        embed.set_author(name="Error", icon_url=url_author_python)
        await ctx.send(embed=embed)

# ----------------------------------------------- MUSIC ----------------------------------------------------

@bot.command(aliases=["cn", "connect"])
async def join_vc(ctx):
    number_of_requests()

    voice = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:

        if not ctx.message.author.voice:
            embed = nextcord.Embed(description="{}, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
            await ctx.send(embed=embed)

        if voice == None:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            embed = nextcord.Embed(description=f"Connected to {ctx.guild.voice_client.channel.name}", color=color)
            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
            embed.set_footer(text=random.choice(connections))
            await ctx.send(embed=embed)

        if voice != None:
            embed = nextcord.Embed(description="Already connected to a voice channel ✅", color=color)
            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
            await ctx.send(embed=embed)

    except Exception as e:
        embed = nextcord.Embed(description="Error:\n" + str(e), color=color)
        embed.set_author(name="Error", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["dc", "disconnect"])
async def leave_vc(ctx):
    number_of_requests()

    try:
        if ctx.author.id in [member.id for member in ctx.voice_client.channel.members]:
            voice_client = ctx.message.guild.voice_client

            try:
                if voice_client.is_connected():
                    embed = nextcord.Embed(description=f"Disconnected from {ctx.guild.voice_client.channel.name}", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    embed.set_footer(text=random.choice(disconnections))
                    await ctx.send(embed=embed)
                    await voice_client.disconnect()

            except AttributeError:
                embed = nextcord.Embed(description="I am not connected to a voice channel", color=color)
                embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                await ctx.send(embed=embed)

        else:
            embed = nextcord.Embed(description="{}, buddy, connect to the voice channel first 🔊".format(ctx.author.name), color=color)
            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
            await ctx.send(embed=embed)

    except AttributeError:
        embed = nextcord.Embed(description="I am not connected to a voice channel", color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["setbit", "bit"])
async def set_bitrate(ctx, kbps):
    number_of_requests()

    for items in ydl_op["postprocessors"]:
        items["preferredquality"] = str(kbps)
        embed = nextcord.Embed(description="**Bitrate:** {} kbps".format(kbps), color=color)
        embed.set_author(name="Audio Quality", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["queue", "q"])
async def queue_song(ctx, *, name=None):
    number_of_requests()

    if ctx.author.id not in ([member.id for member in ctx.guild.voice_client.channel.members] if ctx.guild.voice_client else []):
        embed = nextcord.Embed(description="Either I am not connected or you're not 🔊", color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)

    else:
        if name is not None:
            # WEB SCRAPE
            name = name.replace(" ", "+")
            htm = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + name)
            video = regex.findall(r"watch\?v=(\S{11})", htm.read().decode())
            url = "https://www.youtube.com/watch?v=" + video[0]
            htm_code = str(urllib.request.urlopen(url).read().decode())
            starting = htm_code.find("<title>") + len("<title>")
            ending = htm_code.find("</title>")
            name_of_the_song = (htm_code[starting:ending].replace("&#39;", "'").replace("&amp;", "&"))

            # check if song is already queued
            operation_check = (f"SELECT song_url FROM music_queue WHERE server={str(ctx.guild.id)}")
            cursor.execute(operation_check)
            check_list, links = [], cursor.fetchall()
            for link in links:
                link = str(link).replace("(", "").replace(",)", "").replace("'", "")
                check_list.append(link)

            if url in check_list:
                def song_position():
                    for position in range(len(check_list)):
                        if url == check_list[position]:
                            return position
                embed = nextcord.Embed(description=f"{random.choice(already_queued)}\nSong Postion: {song_position()}", color=color)
                embed.set_author(name="Already Queued", icon_url=url_author_music)
                await ctx.send(embed=embed)
            else:
                operation_add_song = f"""INSERT INTO music_queue(song_name, song_url, server)VALUES("{name_of_the_song}","{url}","{str(ctx.guild.id)}")"""
                cursor.execute(operation_add_song)
                embed = nextcord.Embed(description=f"{name_of_the_song}".replace(" - YouTube", " ").replace("&quot;", '"'), color=color)
                embed.set_author(name="Song added", icon_url=url_author_music)
                await ctx.send(embed=embed)

        else:
            operation_view = ("SELECT song_name, song_url FROM music_queue WHERE server={}".format(str(ctx.guild.id)))
            cursor.execute(operation_view)
            songs = (list(enumerate(cursor.fetchall(), start=0))) #song[0] is counter, song[1] is (name, url)

            if len(songs) > 0:
                # bot will still show queue regardless if server's counter is present or not
                try:
                    if server_index[str(ctx.guild.id)] == None: 
                        server_index[str(ctx.guild.id)] = 0
                except KeyError:
                    server_index[str(ctx.guild.id)] = 0
                if server_index[str(ctx.guild.id)] > len(songs):
                        # if user enters a song position which doesn't exist, .: song position shouldn't be more than number of songs
                    server_index[str(ctx.guild.id)] = len(songs) - 1
                else:
                    try: 
                        string = ""
                        # queue display for songs
                        if server_index[str(ctx.guild.id)] > 7:
                            start = server_index[str(ctx.guild.id)] - 7
                            stop = server_index[str(ctx.guild.id)] + 7
                        else:
                            start, stop = 0, 14
                        for song in songs[start:stop]: 
                            string += (str(song[0]) + ") " + f"{song[1][0]}\n".replace(" - YouTube", " ").replace("&quot;", '"'))

                        embed = nextcord.Embed(description=string, color=color)
                        embed.set_author(name=f"{ctx.guild.name}'s Playlist", icon_url=url_author_music)
                        embed.set_thumbnail(url=random.choice(url_thumbnail_music))
                        embed.set_footer(text=f"Number Of Songs: {len(songs)}")
                        player = await ctx.send(embed=embed)

                        await player.add_reaction("⏮")  # previous track
                        await player.add_reaction("▶")  # resume
                        await player.add_reaction("⏸")  # pause
                        await player.add_reaction("⏭")  # next
                        await player.add_reaction("🔂")  # repeat
                        await player.add_reaction("⏹")  # stop
                        await player.add_reaction("🔀")  # shuffle
                        await player.add_reaction("*️⃣")  # current song
                        await player.add_reaction("🔠")  # display queue
                        await player.add_reaction("🔼")  # scroll
                        await player.add_reaction("🔽")  # scroll
                        await player.add_reaction("🔇") # disconnect

                    except KeyError:
                        embed = nextcord.Embed(description=random.choice(default_index), color=color)
                        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                        await ctx.send(embed=embed)

            else:
                embed = nextcord.Embed(description=random.choice(empty_queue), color=color)
                embed.set_author(name=f"{ctx.guild.name}'s Playlist", icon_url=url_author_music)
                embed.set_thumbnail(url=random.choice(url_thumbnail_music))
                embed.set_footer(text="Pull up the help menu with _help or t!help")
                await ctx.send(embed=embed)


@bot.command(aliases=["play", "p"])
async def play_music(ctx, *, char):
    number_of_requests()

    voice = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)
    try:
        if ctx.author.id in [member.id for member in ctx.voice_client.channel.members]:
            try:

                if char.isdigit() == False:
                    if str(ctx.guild.id) not in server_index:
                        server_index[str(ctx.guild.id)] = 0

                    # Web Scrape
                    char = char.replace(" ", "+")
                    htm = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + char)
                    video = regex.findall(r"watch\?v=(\S{11})", htm.read().decode())
                    url = "https://www.youtube.com/watch?v=" + video[0]
                    htm_code = str(urllib.request.urlopen(url).read().decode())
                    starting = htm_code.find("<title>") + len("<title>")
                    ending = htm_code.find("</title>")
                    name_of_the_song = (
                        htm_code[starting:ending]
                        .replace("&#39;", "'")
                        .replace("&amp;", "&")
                        .replace(" - YouTube", " ")
                    )
                    URL_direct = youtube_download(ctx, url)

                    if ctx.voice_client.is_playing() != True:
                        pass
                    else:
                        voice.stop()
                    embed = nextcord.Embed(description="**Song: **{}".format(name_of_the_song).replace(" - YouTube", " "), color=color)
                    embed.set_author(name="Now playing", url=url, icon_url=url_author_music)
                    embed.set_thumbnail(url=pytube.YouTube(url=url).thumbnail_url)
                    embed.add_field(name="Uploader", value=pytube.YouTube(url=url).author, inline=True)
                    embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                    embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=url).length), inline=True)
                    player = await ctx.send(embed=embed)
                    voice.play(nextcord.FFmpegPCMAudio(URL_direct, **FFMPEG_OPTS))

                    await player.add_reaction("▶")  # resume
                    await player.add_reaction("⏸")  # pause
                    await player.add_reaction("⏹")  # stop
                    await player.add_reaction("🔇") # disconnect


                if char.isdigit() == True:
                    # Server Specific Queue
                    operation = (f"SELECT * FROM music_queue WHERE server={str(ctx.guild.id)}")
                    cursor.execute(operation)
                    server_queue = cursor.fetchall()

                    if str(ctx.guild.id) not in server_index:
                        server_index[str(ctx.guild.id)] = int(char)
                    if str(ctx.guild.id) in server_index:
                        server_index[str(ctx.guild.id)] = int(char)

                    try:
                        URL_queue = youtube_download(ctx, server_queue[int(char)][1])

                        if ctx.voice_client.is_playing() != True:
                            pass
                        else:
                            voice.stop()
                        embed = nextcord.Embed(
                            description="**Song: **{a}\n**Queue Index: **{b}".format(a=server_queue[int(char)][0], b=char).replace(" - YouTube", " "), color=color)
                        embed.set_author(name="Now playing", icon_url=url_author_music)
                        embed.set_thumbnail(url=pytube.YouTube(url=server_queue[int(char)][1]).thumbnail_url)
                        embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                        embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[int(char)][1]).author, inline=True)
                        embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[int(char)][1]).length), inline=True)
                        voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))
                        player = await ctx.send(embed=embed)

                        await player.add_reaction("⏮")  # previous track
                        await player.add_reaction("▶")  # resume
                        await player.add_reaction("⏸")  # pause
                        await player.add_reaction("⏭")  # next
                        await player.add_reaction("🔂")  # repeat
                        await player.add_reaction("⏹")  # stop
                        await player.add_reaction("🔀")  # shuffle
                        await player.add_reaction("*️⃣")  # current song
                        await player.add_reaction("🔠")  # display queue
                        await player.add_reaction("🔼")  # scroll
                        await player.add_reaction("🔽")  # scroll
                        await player.add_reaction("🔇") # disconnect

                    except IndexError:
                        embed = nextcord.Embed(description=random.choice(no_song_at_index), color=color)
                        embed.set_author(name="Oops...", icon_url=url_author_music)
                        await ctx.send(embed=embed)

            except AttributeError:
                embed = nextcord.Embed(description="I am not connected to a voice channel".format(ctx.author.name), color=color)
                embed.set_author(name="Voice", icon_url=url_author_music)
                await ctx.send(embed=embed)

        else:
            embed = nextcord.Embed(description="{}, buddy, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
            await ctx.send(embed=embed)

    except AttributeError:
        embed = nextcord.Embed(description="I am not connected to a voice channel".format(ctx.author.name), color=color)
        embed.set_author(name="Voice", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["songinfo"])
async def fetch_current_song(ctx):
    number_of_requests()

    global server_index
    operation = "SELECT * FROM music_queue WHERE server={}".format(str(ctx.guild.id))
    cursor.execute(operation)
    server_queue = cursor.fetchall()

    if len(server_queue) <= 0:
        embed = nextcord.Embed(description="There are no songs in the queue currently 🤔")
        embed.set_author(name="Uh oh...", icon_url=url_author_music)
        await ctx.send(embed=embed)

    else:
        try:
            embed = nextcord.Embed(
                description="**Song: **{a}\n**Index: **{b}\n**Views: **{c}\n**Description: **\n{d}".format(
                    a=server_queue[server_index[str(ctx.guild.id)]][0],
                    b=server_index[str(ctx.guild.id)],
                    c=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).views,
                    d=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).description), 
                color=color
            )
            embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).thumbnail_url)
            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
            embed.set_author(name="Currently Playing", icon_url=url_author_music)
            player = await ctx.send(embed=embed)
            
            await player.add_reaction("⏮")  # previous track
            await player.add_reaction("▶")  # resume
            await player.add_reaction("⏸")  # pause
            await player.add_reaction("⏭")  # next
            await player.add_reaction("🔂")  # repeat
            await player.add_reaction("⏹")  # stop
            await player.add_reaction("🔀")  # shuffle
            await player.add_reaction("*️⃣")  # current song
            await player.add_reaction("🔠")  # lyrics
            await player.add_reaction("🔼")  # scroll
            await player.add_reaction("🔽")  # scroll
            await player.add_reaction("🔇") # disconnect

        except KeyError:
            embed = nextcord.Embed(description=random.choice(default_index), color=color)
            embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
            await ctx.send(embed=embed)


@bot.command(aliases=["prev", "previous"])
async def previous_song(ctx):
    number_of_requests()

    global server_index
    server_index[str(ctx.guild.id)] -= 1
    operation = "SELECT * FROM music_queue WHERE server={}".format(str(ctx.guild.id))
    cursor.execute(operation)
    server_queue = cursor.fetchall()
    voice = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if ctx.author.id in [member.id for member in ctx.voice_client.channel.members]:
        try:
            URL_queue = youtube_download(ctx, server_queue[server_index[str(ctx.guild.id)]][1])

            if ctx.voice_client.is_playing() != True:
                pass
            else:
                voice.stop()
                
            embed = nextcord.Embed(description="**Song: **{}".format(server_queue[server_index[str(ctx.guild.id)]][0]).replace(" - YouTube", " "), color=color)
            embed.set_author(name="Now playing", icon_url=url_author_music)
            embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).thumbnail_url)
            embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).author, inline=True)
            embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).length), inline=True)
            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
            player = await ctx.send(embed=embed)
            voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))

            await player.add_reaction("⏮")  # previous track
            await player.add_reaction("▶")  # resume
            await player.add_reaction("⏸")  # pause
            await player.add_reaction("⏭")  # next
            await player.add_reaction("🔂")  # repeat
            await player.add_reaction("⏹")  # stop
            await player.add_reaction("🔀")  # shuffle
            await player.add_reaction("*️⃣")  # current song
            await player.add_reaction("🔠")  # lyrics
            await player.add_reaction("🔼")  # scroll
            await player.add_reaction("🔽")  # scroll
            await player.add_reaction("🔇") # disconnect

        except IndexError:
            embed = nextcord.Embed(description="Looks like there is no song at this index", color=color)
            embed.set_author(name="Oops...", icon_url=url_author_music)
            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
            await ctx.send(embed=embed)

    else:
        embed = nextcord.Embed(description="{}, buddy, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)
        

@bot.command(aliases=["rep", "repeat"])
async def repeat_song(ctx):
    number_of_requests()

    operation = "SELECT * FROM music_queue WHERE server={}".format(str(ctx.guild.id))
    cursor.execute(operation)
    server_queue = cursor.fetchall()
    voice = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    try:
        URL_queue = youtube_download(ctx, server_queue[server_index[str(ctx.guild.id)]][1])

        if ctx.voice_client.is_playing() != True:
            pass
        else:
            voice.stop()
        embed = nextcord.Embed(description="**Song: **{}".format(server_queue[server_index[str(ctx.guild.id)]][0]).replace(" - YouTube", " "), color=color)
        embed.set_author(name="Repeating Song", icon_url=url_author_music)
        embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).thumbnail_url)
        embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).author, inline=True)
        embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).length), inline=True)
        embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
        player = await ctx.send(embed=embed)
        voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS), after=lambda e: play_music(voice, URL_queue))

        await player.add_reaction("⏮")  # previous track
        await player.add_reaction("▶")  # resume
        await player.add_reaction("⏸")  # pause
        await player.add_reaction("⏭")  # next
        await player.add_reaction("🔂")  # repeat
        await player.add_reaction("⏹")  # stop
        await player.add_reaction("🔀")  # shuffle
        await player.add_reaction("*️⃣")  # current song
        await player.add_reaction("🔠")  # lyrics
        await player.add_reaction("🔼")  # scroll
        await player.add_reaction("🔽")  # scroll
        await player.add_reaction("🔇") # disconnect

    except Exception as e:
        embed = nextcord.Embed(description=str(e), color=color)
        embed.set_author(name="Error", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["skip", "next"])
async def skip_song(ctx):
    number_of_requests()

    global server_index
    server_index[str(ctx.guild.id)] += 1
    operation = "SELECT * FROM music_queue WHERE server={}".format(str(ctx.guild.id))
    cursor.execute(operation)
    server_queue = cursor.fetchall()
    voice = nextcord.utils.get(bot.voice_clients, guild=ctx.guild)

    if ctx.author.id in [member.id for member in ctx.voice_client.channel.members]:
        try:
            URL_queue = youtube_download(ctx, server_queue[server_index[str(ctx.guild.id)]][1])

            if ctx.voice_client.is_playing() != True:
                pass
            else:
                voice.stop()
            embed = nextcord.Embed(description="**Song: **{}".format(server_queue[server_index[str(ctx.guild.id)]][0]).replace(" - YouTube", " "), color=color)
            embed.set_author(name="Now Playing", icon_url=url_author_music)
            embed.set_thumbnail(url=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).thumbnail_url)
            embed.add_field(name="Uploader", value=pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).author, inline=True)
            embed.add_field(name="Duration", value=time_converter(pytube.YouTube(url=server_queue[server_index[str(ctx.guild.id)]][1]).length), inline=True)
            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
            player = await ctx.send(embed=embed)
            voice.play(nextcord.FFmpegPCMAudio(URL_queue, **FFMPEG_OPTS))
            
            await player.add_reaction("⏮")  # previous track
            await player.add_reaction("▶")  # resume
            await player.add_reaction("⏸")  # pause
            await player.add_reaction("⏭")  # next
            await player.add_reaction("🔂")  # repeat
            await player.add_reaction("⏹")  # stop
            await player.add_reaction("🔀")  # shuffle
            await player.add_reaction("*️⃣")  # current song
            await player.add_reaction("🔠")  # lyrics
            await player.add_reaction("🔼")  # scroll
            await player.add_reaction("🔽")  # scroll
            await player.add_reaction("🔇") # disconnect
            
        except IndexError:
            embed = nextcord.Embed(description="Looks like there is no song at this index", color=color)
            embed.set_author(name="Oops...", icon_url=url_author_music)
            embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
            await ctx.send(embed=embed)

    else:
        embed = nextcord.Embed(description="{}, buddy, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["pause"])
async def pause_song(ctx):
    number_of_requests()

    voice_client = ctx.message.guild.voice_client
    pause = ctx.voice_client.is_paused()
    playing = ctx.voice_client.is_playing()

    if ctx.author.id in [mem.id for mem in ctx.voice_client.channel.members]:
        try:
            if playing == True:
                voice_client.pause()
                message = await ctx.send("Song paused")
                await message.add_reaction("⏸")
            else:
                if pause == True:
                    embed = nextcord.Embed(description="Song is already paused ❗", color=color)
                    embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                    await ctx.send(embed=embed)
                else:
                    embed = nextcord.Embed(
                        description="No song playing currently ❗", color=color)
                    embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                    await ctx.send(embed=embed)

        except Exception as e:
            embed = nextcord.Embed(description=str(e), color=color)
            embed.set_author(name="Error", icon_url=url_author_music)
            await ctx.send(embed=embed)

    else:
        embed = nextcord.Embed(description="{}, buddy, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["resume", "res"])
async def resume_song(ctx):
    number_of_requests()

    voice_client = ctx.message.guild.voice_client
    pause = ctx.voice_client.is_paused()
    playing = ctx.voice_client.is_playing()

    if ctx.author.id in [member.id for member in ctx.voice_client.channel.members]:
        try:
            if pause == True:
                voice_client.resume()
                message = await ctx.send("Song resumed")
                await message.add_reaction("▶")

            else:
                if playing == True:
                    embed = nextcord.Embed(description="Song is not paused 🤔", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                    await ctx.send(embed=embed)
                else:
                    embed = nextcord.Embed(description="Nothing is playing right now", color=color)
                    embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                    embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                    await ctx.send(embed=embed)

        except Exception as e:
            embed = nextcord.Embed(description=str(e), color=color)
            embed.set_author(name="Error", icon_url=url_author_music)
            await ctx.send(embed=embed)

    else:
        embed = nextcord.Embed(description="{}, buddy, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["stop", "st"])
async def stop_song(ctx):
    number_of_requests()

    voice_client = ctx.message.guild.voice_client
    pause = ctx.voice_client.is_paused()
    playing = ctx.voice_client.is_playing()

    if ctx.author.id in [member.id for member in ctx.voice_client.channel.members]:
        try:
            if playing == True or pause == True:
                voice_client.stop()
                message = await ctx.send("Song stopped")
                await message.add_reaction("⏹")
            else:
                embed = nextcord.Embed(description="Nothing is playing right now", color=color)
                embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
                embed.set_footer(text="Voice Channel Bitrate: {} kbps".format(ctx.guild.voice_client.channel.bitrate/1000))
                await ctx.send(embed=embed)

        except Exception as e:
            embed = nextcord.Embed(description=str(e), color=color)
            embed.set_author(name="Error", icon_url=url_author_music)
            await ctx.send(embed=embed)

    else:
        embed = nextcord.Embed(description="{}, buddy, connect to a voice channel first 🔊".format(ctx.author.name), color=color)
        embed.set_author(name="Spider-Punk Radio™", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["rem", "remove"])
async def remove_song(ctx, index):
    number_of_requests()

    operation_view = 'SELECT * FROM music_queue WHERE server="{}"'.format(str(ctx.guild.id))
    cursor.execute(operation_view)
    songs = cursor.fetchall()
    try:
        embed = nextcord.Embed(description="{}".format(songs[int(index)][0]), color=color)
        embed.set_author(name="Song removed", icon_url=url_author_music)
        await ctx.send(embed=embed)
        operation_remove = ("DELETE FROM music_queue WHERE song_url = '{a}' AND server='{b}'".format(a=songs[int(index)][1], b=str(ctx.guild.id)))
        cursor.execute(operation_remove)
    except IndexError:
        embed = nextcord.Embed(description=random.choice(no_song_at_index), color=color)
        embed.set_author(name="Uh oh...", icon_url=url_author_music)
        await ctx.send(embed=embed)


@bot.command(aliases=["clear_queue", "cq"])
async def clear_song_queue(ctx):
    number_of_requests()

    operation_queue = "SELECT * FROM music_queue WHERE server={}".format(str(ctx.guild.id))
    cursor.execute(operation_queue)
    songs = cursor.fetchall()

    if len(songs) > 0:
        operation_clear_song = "DELETE FROM music_queue WHERE server={}".format(str(ctx.guild.id))
        cursor.execute(operation_clear_song)
        message = await ctx.send("Queue Cleared")
        await message.add_reaction("✅")

    else:
        embed_empty = nextcord.Embed(description=random.choice(empty_queue), color=color)
        embed_empty.set_author(name="Hmm...", icon_url=url_author_music)
        await ctx.send(embed=embed_empty)

# -------------------------------------------------- EXTRA ---------------------------------------------------------

@bot.command(aliases=["addbday"])
async def add_user_bday(ctx, member: nextcord.Member, month, day):
    number_of_requests()

    op_check = "SELECT mem_id FROM birthdays"
    cursor.execute(op_check)
    memIDs = cursor.fetchall()
    toggle = 0

    try:
        for tup_memID in memIDs:
            if str(member.id) in tup_memID:
                await ctx.send(embed=nextcord.Embed(description=f"{member.name}'s birthday is already in my database 🤔", color=color))
                toggle = 1
        if toggle == 0:
            cursor.execute(f"INSERT INTO birthdays VALUES('{member.id}', {month}, {day}, '{ctx.guild.id}')")
            await ctx.send(embed=nextcord.Embed(description=f"{member.name}'s birthday added to database 👍🏻", color=color))
    except Exception as e:
        await ctx.send(str(e))


@bot.command(aliases=["rembday"])
async def remove_user_bday(ctx, member: nextcord.Member):
    number_of_requests()

    op_check = "SELECT mem_id FROM birthdays"
    cursor.execute(op_check)
    memIDs = cursor.fetchall()
    toggle = 0

    try:
        for tup_memID in memIDs:
            if str(member.id) in tup_memID:
                op_insert = "DELETE FROM birthdays WHERE mem_id={}".format(member.id)
                cursor.execute(op_insert)
                await ctx.send(embed=nextcord.Embed(description="{}'s birthday removed from database 👍🏻".format(member.display_name), color=color))
                toggle = 1
        if toggle == 0:
            await ctx.send(embed=nextcord.Embed(description="{}'s birthday does not exist in my database 🤔".format(member.display_name), color=color))
    except Exception as e:
        await ctx.send(str(e))


@bot.command(aliases=["bday"])
async def check_user_bdays_and_wish(ctx):
    number_of_requests()

    op_check = "SELECT * FROM birthdays"
    cursor.execute(op_check)
    bdays = cursor.fetchall()
    channel = None
    toggle = 0

    # automatically check server for which channel to send the wish in
    for i in ctx.guild.channels:
        for j in announcement_channels:
            if i.name == j:
                send_to = i.name = j
                channel = nextcord.utils.get(ctx.guild.channels, name=send_to)

    for bday in bdays:  # bday[0]   bday[1]  bday[2]
        if datetime.datetime.today().month == bday[1]and datetime.datetime.today().day == bday[2]:
            name = bot.get_user(int(bday[0])).name
            wishes = [
                f"🎊 Happy Birthday {name} 🎊",
                f"🎉 Happy Birthday {name} 🎉",
                f"✨ Happy Birthday {name} ✨",
                f"🎇 Happy Birthday {name} 🎇",
            ]
            embed = nextcord.Embed(title=random.choice(wishes), description=random.choice(descriptions), color=color)
            embed.set_image(url=random.choice(url_bdays_spiderman))
            embed.set_thumbnail(url=bot.get_user(int(bday[0])).avatar.url)
            await channel.send(f"<@{bot.get_user(int(bday[0])).id}>")
            message = await channel.send(embed=embed)

            await ctx.send(embed=nextcord.Embed(description="Wish Sent 🥳", color=color))
            await message.add_reaction("🎁")
            await message.add_reaction("🎈")
            await message.add_reaction("🎂")
            await message.add_reaction("🎆")
            await message.add_reaction("🎉")
            toggle = 1

    if toggle == 0:
        await ctx.send(embed=nextcord.Embed(description=random.choice(none_today), color=color))

# ------------------------------------------------------------------------------------------------------------------------------
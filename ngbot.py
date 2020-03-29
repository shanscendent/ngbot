import discord
from discord.ext import commands
import discord

import time, os
import shlex
import subprocess
from random import randint
import configparser

import requests

import time

config = configparser.ConfigParser()
config.read('ngbot.conf')

bot_channel = config['DEFAULT']['BotChannel']
bot_token = config['DEFAULT']['Token']
bot = commands.Bot(command_prefix='~')

start_time = time.time()

@bot.command()
async def status(ctx):
    """Get bot uptime"""
    if ctx.channel.name != bot_channel:
        return
    current_time = time.time() - start_time
    current_time = int(current_time)
    await ctx.send("{0} seconds uptime".format(current_time))

@bot.command()
async def ping(ctx, arg):
    """Ping an IP FROM the server. Suggested usage: ~ping google.com"""
    if ctx.channel.name != bot_channel:
        return
    await ctx.send("Pinging server...")
    await ctx.trigger_typing()
    # Argument sanitization
    command = 'ping {} -c 4'.format(shlex.quote(arg))
    command = shlex.split(command)
    res = subprocess.check_output(command)
    line = res.splitlines()[-1]
    #await ctx.delete_message()
    await ctx.send(line.decode().split("/")[4] + "ms average to " + arg)

@bot.command()
async def insult(ctx, arg):
    """Insult. Suggested usage: ~insult"""
    if ctx.channel.name != bot_channel:
        return
    r = requests.get('https://insult.mattbas.org/api/insult')
    status_code = r.status_code
    if status_code != 200:
        return
    text = r.text + ", " + arg 
    print(arg)
    await ctx.send("{0}".format(text))

@bot.command()
async def rps(ctx, arg1, arg2):
    if ctx.channel.name != bot_channel:
        return
    """Rock paper scissors. Suggested usage: ~rps <name1> <name2>"""
    t = ["Rock", "Paper", "Scissors"]

    p1 = t[randint(0,2)]
    p2 = t[randint(0,2)]

    trumped_by = {
        'Rock': ['Paper'],
        'Paper': ['Scissors'],
        'Scissors': ['Rock']
    }

    if p1 == p2:
        out = "{1} plays {0}. {2} plays {0}. Tie!".format(p1, arg1, arg2)   
    else:
        if p2 in trumped_by[p1]:
            out = "{2} plays {0}. {3} plays {1}. {3} wins!".format(p1, p2, arg1, arg2)
        else:
            out = "{2} plays {0}. {3} plays {1}. {2} wins!".format(p1, p2, arg1, arg2)

    await ctx.send(out)

# Events
@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    if before.channel != None:
        return
    member_id = member.id
    guild = bot.get_guild(member.guild.id)
    for voice_channel in guild.voice_channels:
        if voice_channel.name == after.channel.name:
            members = voice_channel.members
            break
    message = "<@!{}> has joined".format(member.id)
    i = 0
    if len(members) == 1:
        message += " {}, anyone there?".format(after.channel)
    else:
        for member in members:
            i += 1
            if member.id == member_id:
                continue
            message += " <@!{}>".format(member.id)
            if i != len(members):
                message += ","
        message += " in {}.".format(after.channel)
    for channel in bot.get_all_channels():
        if channel.name == bot_channel:
            await channel.send(message, delete_after=300)

member_dict = {}
@bot.event
async def on_member_update(before, after):
    if before.bot:
        return
    if before.activity == None: before_activity = None
    else: before_activity = before.activity.type
    if after.activity == None: after_activity = None
    else: after_activity = after.activity.type
    if before_activity != discord.ActivityType.playing and after_activity == discord.ActivityType.playing:
        if before.id in member_dict:
            if (time.time() - member_dict[before.id]) < 5:
                return
        member_dict[before.id] = time.time()
        message = "<@!{}> is playing {}".format(before.id, after.activity.name)
        for channel in bot.get_all_channels():
            if channel.name == bot_channel:
                await channel.send(message, delete_after=300)

bot.run(bot_token)
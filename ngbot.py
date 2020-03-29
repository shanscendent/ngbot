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
import asyncio

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
async def timer(ctx, *args):
    """Countdown timer in minutes. Suggested usage: ~timer 5, or ~timer 5 @someone to nag them past timer stop"""
    arg = args[0] # minutes
    # terminated?
    terminated = False
    # test
    interval_seconds = 5
    # initialize embed
    description = "{}'s {}m timer. ❌ to stop".format(ctx.author.mention, arg)
    embedded = discord.Embed(
        title = "Timer Running",
        description=description
    )
    start_time = time.time()
    end_time = start_time + int(float(arg)*60)
    embedded.insert_field_at(index=0, name="Time Left", value="{}m".format(arg), inline=False)
    # if additional user argument
    if len(args) == 2:
        monitored_user = args[1]
        embedded.insert_field_at(index=1, name="Waiting for", value="{}".format(monitored_user), inline=False)
    # start timer routine
    async with ctx.typing():
        await ctx.message.delete() # delete command message
        message = await ctx.send(embed=embedded) # send embed
        await message.add_reaction('❌') # add reaction
        # start embed live update
        while end_time > time.time():
            # check for reactions in reaction_dict
            if message.id in reaction_dict:
                if reaction_dict[message.id][0] == ctx.author.id and reaction_dict[message.id][1] == '❌':
                    terminated = True
                    elapsed_time = time.time() - start_time
                    break # terminate function
            await asyncio.sleep(interval_seconds)
            remaining_time = end_time - time.time()
            # if remaining_time is less than interval, stop
            if remaining_time < interval_seconds:
                await asyncio.sleep(int(remaining_time))
                break
            remaining_time_str = "{}m {}s".format(int(remaining_time/60), int(remaining_time%60))
            # update embed
            embedded.set_field_at(index=0, name="Time Left", value=remaining_time_str, inline=False)
            await message.edit(embed=embedded)
        # delete message
        if message.id in reaction_dict:
            reaction_dict.pop(message.id) # clear storage
        await message.delete() # delete message
        if terminated:
            elapsed_time_str = "{}m {}s".format(int(elapsed_time/60), int(elapsed_time%60))
            await ctx.send("{}, cancelled timer. {} elapsed".format(ctx.author.mention, elapsed_time_str)) # notify user who terminated command
        else:
            await ctx.send("{}, {}m timer is up".format(ctx.author.mention, arg)) # notify user who initiated command
        # If there is a monitored user, continue
        if len(args) == 2:
            # start you are late live update
            main_message = await ctx.send("{}, YOU ARE LATE! NAGGING EVERY MINUTE\nNote: only {} can cancel with ❌".format(monitored_user, ctx.author.mention))
            await main_message.add_reaction('❌') # add reaction
            await asyncio.sleep(60)
            i = 1
            while True:
            # check for reactions in reaction_dict
                if main_message.id in reaction_dict:
                    if i > 29:
                        await main_message.delete()
                        try:
                            await message.delete()
                        except discord.NotFound:
                            pass
                        await ctx.send("{}, nagging cancelled for {} due to timeout. {}m elapsed".format(ctx.author.mention, monitored_user, i)) # notify user who terminated command
                        return # terminate function
                    if reaction_dict[main_message.id][0] == ctx.author.id and reaction_dict[main_message.id][1] == '❌':
                        reaction_dict.pop(main_message.id)
                        await main_message.delete()
                        try:
                            await message.delete()
                        except discord.NotFound:
                            pass
                        break # terminate function
                if message.id in reaction_dict:
                    if reaction_dict[message.id][0] == ctx.author.id and reaction_dict[message.id][1] == '❌':
                        reaction_dict.pop(message.id)
                        await main_message.delete()
                        try:
                            await message.delete()
                        except discord.NotFound:
                            pass
                        break # terminate function
                message = await ctx.send("{}, YOU ARE LATE BY {}m!".format(monitored_user, i))
                await message.add_reaction('❌') # add reaction
                await asyncio.sleep(60)
                await message.delete()
                i += 1
            await ctx.send("{} cancelled nagging for {}. {}m elapsed".format(ctx.author.mention, monitored_user, i)) # notify user who terminated command


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

reaction_dict = {}
@bot.event
async def on_reaction_add(reaction, user):
    if user.id == bot.user.id:
        return
    reaction_dict[reaction.message.id] = [user.id, reaction.emoji]

bot.run(bot_token)
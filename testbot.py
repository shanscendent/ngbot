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
config.read('testbot.conf')

bot_channel = config['DEFAULT']['BotChannel']
bot_token = config['DEFAULT']['Token']
bot = commands.Bot(command_prefix='~')

start_time = time.time()

site_dict = {}
checksite_stop = False

@bot.command()
async def status(ctx):
    """Get bot uptime"""
    current_time = time.time() - start_time
    current_time = int(current_time)
    await ctx.send("{0} seconds uptime".format(current_time))

@bot.command()
async def checksite(ctx, arg):
    """Check site availability. Example: ~checksite https://gamershideout.com.my, or ~checksite stop to stop."""
    global checksite_stop
    global site_dict
    if arg.lower() == "stop":
        checksite_stop = True
        site_dict.clear()
        return
    if arg not in site_dict:
        try:
            r = requests.get(arg, timeout=10)
            site_dict[arg] = r.status_code
        except requests.exceptions.RequestException:
            await ctx.send("`Couldn't connect. Please make sure this is the correct spelling: {}`".format(arg))
        await ctx.send("`Periodically checking availability of {}.`".format(arg))
            
        while not checksite_stop:
            try:
                r = requests.get(arg, timeout=10)
                site_dict[arg] = r.status_code
                if r.status_code == 200:
                    checksite_stop = False
                    site_dict.pop(arg)
                    await ctx.send("`{} is online! Stopping check.`".format(arg))
                    return
            except requests.exceptions.RequestException:
                site_dict[arg] = 0
            print(arg, site_dict[arg])
            await asyncio.sleep(60)

        checksite_stop = False
    else:
        await ctx.send("`{} already in site list.`".format(arg))

@bot.command()
async def sitelist(ctx):
    """Lists sites being checked. Example: ~sitelist"""
    output = "`"
    if len(site_dict) == 0:
        output += "No sites being checked.`"
    else:
        for site in site_dict:
            output += "{} is offline, status code {}.\n".format(site, site_dict[site])
        output += "`"
    await ctx.send(output)

bot.run(bot_token)
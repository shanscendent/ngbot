# Nerdgasm Server Discord Bot
Bot for quality of life improvements

## Getting started
Install the necessary dependencies: [discord.py](https://discordpy.readthedocs.io/en/latest/), `requests`\
`venv` recommended.
```
pip install -U discord.py
```

## Configuration file format
The configuration file `ngbot.conf` is not pushed as it contains important credentials\
Format:
```
[DEFAULT]
BotChannel = <Bot channel name>
Token = <Discord bot token>
```

## What is working
- Commands:
  - Uptime
  - Ping (Uses `ping` from bash, `shlex` to sanitize user inputs)
  - Insult
  - Rock, paper, scissors
- Events:
  - Send message to bot channel on member voice channel join
  - Send message to bot channel on member game start
  
## To-do
- Make it work on multiple guilds

## Bugs
- 

## Notes
- `on_member_update()` is called many times, need to figure out a way to prevent multiple messages *efficiently*
# Nerdgasm Server Discord Bot
Bot for quality of life improvements

## Getting started
Install the necessary dependencies: `discord.py`
`venv` recommended.
```
pip install -U discord.py
```

## Configuration file format
The configuration file `ngbot.conf` is not pushed as it contains important credentials
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

## Bugs
- Game start event breaks sometimes:
```
File "ngbot.py", line 118, in on_member_update
if before.activity.type != discord.ActivityType.playing and after.activity.type == discord.ActivityType.playing:
AttributeError: 'NoneType' object has no attribute 'type'
```
# shadesv2

uses https://github.com/sherjilozair/char-rnn-tensorflow , read for info on training

a discord bot but is actually a real boy

requires tensorflow, put trained models in /shadesv2/saves/{server_id}/
for connected server ids look into info/servers_disambig.txt

you need to create Config.py file with those variables:

---
DISCORD_TOKEN = 'your token'
IMGUR_CLIENT_ID = 'your imgur client id'
IMGUR_CLIENT_SECRET = 'your imgur client secret'
---

run DiscrodBot.py

these files are irrelevant and might soon be removed: 
  main.py
  Markov.py
  TwitchUtil.py
  MessageReceiver.py
  StrUtil.py
  Whisperer.py
  CommandQueue.py

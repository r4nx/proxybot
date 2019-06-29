# proxybot

proxybot is a tiny single-file python script that creates gateway between Telegram groups and users. Users can send messages to certain group and receive messages from that group.

## Who needs this
If you got banned (e.g. for spam), you cannot use public chats. Ask chat admin to add the your bot and you can communicate again!

## Installation and running
You need Python 3 (tested with Python 3.7.2) and [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) library (tested with 3.6.6). Create new bot via [Bot Father](https://t.me/botfather). **[!]** Attention - disable privacy mode in the bot settings, that's very important, otherwise your bot won't be able to access group messages. Get your token and paste it to `config.json`. After that, simple run it with `python proxybot.py` without any arguments.

## Usage
Firstly, you need to retrieve your user ID. Send `/getid` command to bot. Then open `config.json` with text editor and add yourself to admin list:

```json
"admins": {
    "yournickname": 12345678
},
```

Replace `yournickname` and `12345678` with any nick (not necessarely your username) and your ID respectively. Restart the bot and you are ready to go! Check out command reference below to get involeved in the bot usage.

## Command reference
**/getid**
> ID of chat (user id if sent directly to bot or group id if sent in the group)

**/groups**
> List of available groups

**/addgroup <group_id>**
> Add new group

**/removegroup <group_index>**
> Remove the group *(pay attention to parameter - it is index that showed by `/groups` command)*

**/switchgroup <group_index>**
> Select group to send messages from users (users receive messages from all groups regardless of this option)

**/users**
> List of all users

**/adduser <user_id> <alias>**
> Add new user *(alias doesn't have to be username, any alphanumeric text)*

**/removeuser <alias>**
> Remove the user

**/noforwardprefix <prefix>**
> If PM -> Group message starts with this prefix, bot won't forward your message and will send its text only. Allowed characters to use are `!#$&*+<=>-~`. To disable this feature simply send `/noforwardprefix` without arguments

## Permission system
Users have access to `/groups`, `/switchgroup` and `/users` commands. Admins have access to all the commands, including user commands.  
Note that only users get their messages sent to groups and receive messages from groups, it won't work if you only in admins group and not in users.

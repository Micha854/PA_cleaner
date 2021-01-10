# PA_cleaner

this is a cleaner specially developed for pokealarm. but it is also suitable for eg poracle

A TIME field is read from the message and must be in the format:

```
BETRWEEN 00:00:00 AND 23:59:59
```

if this format is not available or if the message is not deleted, it will be deleted after one hour to be on the safe side (only messages with a recognizable TIME field are deleted)

using this central message, the pokemon icon and the location message can be removed. set in the config

## Please note:
add your telegram bot in all channels that should be cleaned up. the personal chat with the bot can also be cleaned up. all chatid must also be specified in the config

messages with a different TIME format are not deleted, e.g. 00:00 is not deleted

if another format is to be supported, a PR can be made

## Start
`python3 clean.py`

## Option
if you want not fetch new messages use the option -nofetch

`python3 clean.py -nofetch`
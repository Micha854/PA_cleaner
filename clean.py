#!/usr/bin/env python3
__author__ = "Micha854"
__copyright__ = "Copyright 2020, Micha854"
__version__ = "0.0.69"
__status__ = "beta"

# generic/built-in and other libs
import telepot
import sys
import os
import json
import time
import re
import datetime
import config

# function add to JSON
def write_json(feeds):
    with open(chatid + '.json', mode='w', encoding='utf8') as data:
        json.dump(feeds, data, ensure_ascii=False, indent=4)

### option no fetching
try:
    if sys.argv[1] == '-nofetch':
        fetching = False
    else:
        fetching = None
except:
    fetching = True

if fetching == None:
    sys.exit(' no correct option, aborted\n\n availeble option:\n\n  -nofetch     [no fetching new messages]\n')

### read config file
token  = config.token
chatid = config.chatid

bot = telepot.Bot(token)

### readout next update_id
if os.path.isfile('update.txt'):
    datei = open('update.txt','r')
    check_offset = datei.read()
    offset = check_offset
### set default update_id
else:
    offset = 100000001

feeds = {}
fetch = {}
title = {}

### readout all json files of given chatids
for chatid in config.chatid:
    if os.path.isfile(chatid + ".json"):
        with open(chatid + ".json") as feedsjson:
            feeds[chatid] = json.load(feedsjson)
    else:
        feeds[chatid] = []
    
    fetch[chatid] = 0
    title[chatid] = None

last_update = 0
deleted = 0

while 1 == 1:
    if fetching == True:
        while True:
            try:
                ### load response from getUpdates
                response = bot.getUpdates(offset=offset, allowed_updates=['channel_post', 'message'])

                ### load getUpdates data to json file of chatid
                for message in response:
                    try:
                        if 'channel_post' in message:
                            id    = message['channel_post']['chat']['id']
                            titl = message['channel_post']['chat']['title']
                        elif 'message' in message:
                            id    = message['message']['chat']['id']
                            titl = message['message']['chat']['username']
                    except:
                        id = None
                        title = None

                    if not id == None and id in config.chatid:
                        if title[str(id)] == None:
                            title[str(id)] = titl

                    for chatid in config.chatid:
                        if not message['update_id'] in feeds[chatid] and str(id) == chatid:
                            feeds[chatid].append(message)
                            if message['update_id'] > last_update:
                                last_update = message['update_id']
                            fetch[chatid] += 1

                offset = last_update + 1

                if len(response) < 100:
                    break

                else:
                    print(" ...fetching " + str(fetch[chatid]) + " messages")
            except Exception as e:
                print(" cannot fetch new data, try again in " + str(config.sleeptime) + " seconds...")
                print(" error: " + str(e))
                time.sleep(config.sleeptime)
    else:
        print('---------- no fetching new messages ----------')


    ### save next update_id
    if int(last_update):
        f = open('update.txt', 'w')
        f.write(str(last_update+1))
        f.close()

    for chatid in config.chatid:
        # add two dummy entries if file is empty
        try:
            feeds[chatid][0]
        except:
            feeds[chatid].append({"update_id": None,"message": {"message_id": None,"chat": {"id": chatid,"username": None},"date": None,"text": "FIRST_DUMMY"}})
            try:
                feeds[chatid][1]
            except:
                feeds[chatid].append({"update_id": None,"message": {"message_id": None,"chat": {"id": chatid,"username": None},"date": None,"text": "SECOND_DUMMY"}})
        
        icon = feeds[chatid][0]
        message = feeds[chatid][1]

        ### go through all messages
        for location in feeds[chatid][2:]:
            try:
                if 'channel_post' in message:
                    message_messageid = message['channel_post']['message_id']
                    message_chatid    = message['channel_post']['chat']['id']
                    message_date      = message['channel_post']['date']
                    message_title     = message['channel_post']['chat']['title']
                elif 'message' in message:
                    message_messageid = message['message']['message_id']
                    message_chatid    = message['message']['chat']['id']
                    message_date      = message['message']['date']
                    message_title     = message['message']['chat']['username']
            except:
                message_messageid  = None
                message_chatid     = None

            # check of sticker
            try:
                if 'channel_post' in icon:
                    icon_is        = icon['channel_post']['sticker']
                    icon_messageid = icon['channel_post']['message_id']
                    icon_chatid    = icon['channel_post']['chat']['id']
                    icon_title     = icon['channel_post']['chat']['title']
                elif 'message' in icon:
                    icon_is        = icon['message']['sticker']
                    icon_messageid = icon['message']['message_id']
                    icon_chatid    = icon['message']['chat']['id']
                    icon_title     = icon['message']['chat']['username']
            except:
                icon_is = None

            # check of location
            try:
                if 'channel_post' in location:
                    location_is        = location['channel_post']['location']
                    location_messageid = location['channel_post']['message_id']
                    location_chatid    = location['channel_post']['chat']['id']
                    location_title     = location['channel_post']['chat']['title']
                elif 'message' in location:
                    location_is        = location['message']['location']
                    location_messageid = location['message']['message_id']
                    location_chatid    = location['message']['chat']['id']
                    location_title     = location['message']['chat']['username']
            except:
                location_is = None

            # search for time in message
            try:
                if 'channel_post' in message:
                    message_text = message['channel_post']['text']
                elif 'message' in message:
                    message_text = message['message']['text']
                result = re.search(config.pattern, message_text)
                group = result.group()
                despawn = group[:]
            except:
                despawn = None
                message_text = None

            # check if time has expired
            try:
                now = time.strftime('%H:%M:%S')
                now_time = datetime.datetime.strptime(str(now), '%H:%M:%S').timestamp()
                despawn_time = datetime.datetime.strptime(str(despawn), '%H:%M:%S').timestamp()
                diff = int(now_time - despawn_time)
            except:
                diff = None

            
            if not diff == None:
                old_diff = int(time.time()) - message_date
                # message is outdated and can be delete
                if diff > 0 or old_diff > 3600:
                    # handling of daychange
                    if not (despawn[:2] == '00' and now[:2] == '23'):
                        tabs = '     '
                        print('')
                        # delete back message (pokemon icon)
                        if config.delete_icon:
                            if not icon_is == None:
                                try:
                                    bot.deleteMessage((icon_chatid, icon_messageid))
                                    feeds[chatid].remove(icon)
                                    print(' delete icon ' + tabs[:4] + ' message(' + str(icon_messageid) + ') from "' + str(icon_title) + '"')
                                except telepot.exception.TelegramError as e:
                                    if e.error_code == 400:
                                        feeds[chatid].remove(icon)
                                        print(' *** icon ' + tabs[:4] + ' message(' + str(icon_messageid) + ') does not exist and will be removed from the json file')
                                except:
                                    print(' !!! cannot be delete icon ' + tabs[:4] + ' message(' + str(icon_messageid) + ') from "' + str(icon_title) + '", skip...')
                        # delete central message with despawn time
                        try:
                            bot.deleteMessage((message_chatid, message_messageid))
                            feeds[chatid].remove(message)
                            print(' delete main ' + tabs[:4] + ' message(' + str(message_messageid) + ') from "' + str(message_title) + '"')
                        except telepot.exception.TelegramError as e:
                            if e.error_code == 400:
                                feeds[chatid].remove(message)
                                print(' *** main ' + tabs[:4] + ' message(' + str(message_messageid) + ') does not exist and will be removed from the json file')
                            if e.error_code == 429:
                                print(' Too Many Requests...')
                        except:
                            print(' !!! cannot be delete main ' + tabs[:4] + ' message(' + str(message_messageid) + ') from "' + str(message_title) + '", skip...')
                        # delete forward message (map)
                        if config.delete_location:
                            if not location_is == None:
                                try:
                                    bot.deleteMessage((location_chatid, location_messageid))
                                    feeds[chatid].remove(location)
                                    print(' delete location ' + tabs[:0] + ' message(' + str(location_messageid) + ') from "' + str(location_title) + '"')
                                except telepot.exception.TelegramError as e:
                                    if e.error_code == 400:
                                        feeds[chatid].remove(location)
                                        print(' *** location ' + tabs[:0] + ' message(' + str(location_messageid) + ') does not exist and will be removed from the json file')
                                except:
                                    print(' !!! cannot be delete location ' + tabs[:0] + ' message(' + str(location_messageid) + ') from "' + str(location_title) + '", skip...')
                        deleted +=1

            icon = message
            message = location

        ### save json file of given chatid
        write_json(feeds[chatid])

        ### result output
        if not fetch[chatid] == 0:
            if deleted > 0:
                print('')
            print(' >>> Fetching ' + str(fetch[chatid]) + ' Messages from "' + str(title[chatid]) + '"')
            fetch[chatid] = 0
            deleted = 0

    time.sleep(config.sleeptime)
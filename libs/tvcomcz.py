# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from xbmcvfs import translatePath

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

import json
import codecs
from datetime import datetime
import time

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def call_api(url, data):
    addon = xbmcaddon.Addon()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0', 'Accept': 'application/json; charset=utf-8'}    
    if data != None:
        data = urlencode(data)
        data = data.encode('utf-8')
    request = Request(url = url , data = data, headers = headers)
    if addon.getSetting('log_api_calls') == 'true':
        xbmc.log(str(url))
        xbmc.log(str(data))
    try:
        html = urlopen(request).read()
        if addon.getSetting('log_api_calls') == 'true':
            xbmc.log(str(html))
        if html and len(html) > 0:
            data = json.loads(html)
            return data
        else:
            return []
    except HTTPError as e:
        return { 'err' : e.reason }      

def load_SportTypes():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'SportTypes.txt')
    data = {}
    if os.path.exists(filename):
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as file:
                for row in file:
                    data = json.loads(row[:-1])
        except IOError as error:
            if error.errno != 2:
                xbmcgui.Dialog().notification('TVcom.cz', 'Chyba při načtení cache', xbmcgui.NOTIFICATION_ERROR, 5000)
    return data

def save_SportTypes(data):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    if not os.path.exists(addon_userdata_dir):
        os.makedirs(addon_userdata_dir)
    valid_to = int(time.time()) + 60*60*24
    data = json.dumps({'data' : data, 'valid_to' : valid_to})
    filename = os.path.join(addon_userdata_dir, 'SportTypes.txt')
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % data)
    except IOError:
        xbmcgui.Dialog().notification('TVcom.cz', 'Chyba uložení cache', xbmcgui.NOTIFICATION_ERROR, 5000)  

def load_SportLeagues():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'SportLeagues.txt')
    data = {}
    if os.path.exists(filename):
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as file:
                for row in file:
                    data = json.loads(row[:-1])
        except IOError as error:
            if error.errno != 2:
                xbmcgui.Dialog().notification('TVcom.cz', 'Chyba při načtení cache', xbmcgui.NOTIFICATION_ERROR, 5000)
    return data

def save_SportLeagues(data):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    if not os.path.exists(addon_userdata_dir):
        os.makedirs(addon_userdata_dir)
    data = json.dumps(data)
    filename = os.path.join(addon_userdata_dir, 'SportLeagues.txt')
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % data)
    except IOError:
        xbmcgui.Dialog().notification('TVcom.cz', 'Chyba uložení cache', xbmcgui.NOTIFICATION_ERROR, 5000)  

def load_mainlist():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'mainlist.txt')
    data = []
    if os.path.exists(filename):
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as file:
                for row in file:
                    data = json.loads(row[:-1])
        except IOError as error:
            if error.errno != 2:
                xbmcgui.Dialog().notification('TVcom.cz', 'Chyba při načtení vybraných sportů a soutěží', xbmcgui.NOTIFICATION_ERROR, 5000)
    return data

def save_mainlist(data):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    if not os.path.exists(addon_userdata_dir):
        os.makedirs(addon_userdata_dir)    
    data = json.dumps(data)
    filename = os.path.join(addon_userdata_dir, 'mainlist.txt')
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % data)
    except IOError:
        xbmcgui.Dialog().notification('TVcom.cz', 'Chyba uložení vybraných sportů a soutěží', xbmcgui.NOTIFICATION_ERROR, 5000)  

def change_mainlist(toggle, SportTypeId):
    mainlist = load_mainlist()
    if toggle == 1:
        mainlist.append(SportTypeId)
    else:
        mainlist.remove(SportTypeId)
    save_mainlist(data = mainlist)            
    xbmc.executebuiltin('Container.Refresh')        

def load_blacklist():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'blacklist.txt')
    data = {}
    if os.path.exists(filename):
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as file:
                for row in file:
                    data = json.loads(row[:-1])
        except IOError as error:
            if error.errno != 2:
                xbmcgui.Dialog().notification('TVcom.cz', 'Chyba při načtení vybraných sportů a soutěží', xbmcgui.NOTIFICATION_ERROR, 5000)
    if 'SportTypeIds' not in data:
        data.update({'SportTypeIds' : []})
    if 'SportLeagueIds' not in data:
        data.update({'SportLeagueIds' : []})
    return data

def save_blacklist(data):
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    if not os.path.exists(addon_userdata_dir):
        os.makedirs(addon_userdata_dir)    
    data = json.dumps(data)
    filename = os.path.join(addon_userdata_dir, 'blacklist.txt')
    try:
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write('%s\n' % data)
    except IOError:
        xbmcgui.Dialog().notification('TVcom.cz', 'Chyba uložení výbraných sportů a soutěží', xbmcgui.NOTIFICATION_ERROR, 5000)       

def change_blacklist(toggle, SportTypeId, SportLeagueId):
    blacklist = load_blacklist()
    if 'SportTypeIds' not in blacklist:
        blacklist.update({'SportTypeIds' : []})
    if 'SportLeagueIds' not in blacklist:
        blacklist.update({'SportLeagueIds' : []})
    if SportTypeId is not None and SportLeagueId is None:
        if SportTypeId == -999:
            if toggle == 1:
                SportTypes = get_SportTypes(filtered = False)
                for SportType in SportTypes:
                    if SportType['id'] >= 0:
                            if SportType['id'] not in blacklist['SportTypeIds']:
                                blacklist['SportTypeIds'].append(SportType['id'])
            else:
                blacklist.update({'SportTypeIds' : []})
        else:
            if toggle == 1:
                blacklist['SportTypeIds'].append(SportTypeId)
            else:
                blacklist['SportTypeIds'].remove(SportTypeId)
    elif SportLeagueId is not None and SportLeagueId == -999:
        SportLeagues = get_SportLeagues(SportTypeId, filtered = False)
        for SportLeague in SportLeagues:
            if toggle == 1 and SportLeague['id'] not in blacklist['SportLeagueIds']:
                blacklist['SportLeagueIds'].append(SportLeague['id'])
            elif toggle == 0 and SportLeague['id'] in blacklist['SportLeagueIds']:
                blacklist['SportLeagueIds'].remove(SportLeague['id'])
    if SportLeagueId is not None and SportLeagueId > 0:
        if toggle == 1:
            blacklist['SportLeagueIds'].append(SportLeagueId)
        else:
            blacklist['SportLeagueIds'].remove(SportLeagueId)
    save_blacklist(data = blacklist)            
    xbmc.executebuiltin('Container.Refresh')

def get_SportTypes(filtered = True):
    SportTypes = []
    if filtered == True:
        blacklist = load_blacklist()
    data = load_SportTypes()
    if 'valid_to' not in data or data['valid_to'] < int(time.time()):
        post = {'Lang' : 'cz'}
        response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetSportType.ashx', data = post)
        if not 'message' in response or response['message'] != 'OK':
            xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením sportů', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()         
        for item in response['data']:
            if item['Id'] > 0:
                if filtered == False or item['Id'] not in blacklist['SportTypeIds']:
                    SportTypes.append({'id' : item['Id'], 'sport' : item['Value'], 'other' : False})
            elif item['Id'] == -1 and 'OtherSports' in item:
                SportTypes.append({'id' : item['Id'], 'sport' : item['Value'], 'other' : False})
                for othersport in item['OtherSports']:
                    if {'id' : othersport['Id'], 'sport' : othersport['Value'], 'other' : False} not in SportTypes:
                        if filtered == False or othersport['Id'] not in blacklist['SportTypeIds']:
                            SportTypes.append({'id' : othersport['Id'], 'sport' : othersport['Value'], 'other' : True})
        save_SportTypes(SportTypes)
    else:
        for SportType in data['data']:
            if filtered == False or SportType['id'] not in blacklist['SportTypeIds']:
                SportTypes.append({'id' : SportType['id'], 'sport' : SportType['sport'], 'other' : SportType['other']})
    return SportTypes

def get_SportLeagues(SportTypeId, filtered = True):
    SportLeagues = []
    if filtered == True:
        blacklist = load_blacklist()  
    data = load_SportLeagues()
    if str(SportTypeId) not in data or data[str(SportTypeId)]['valid_to'] < int(time.time()):
        post = {'Lang' : 'cz'}
        post.update({'SportTypeId' : SportTypeId, 'Live' : 0})
        response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetSportLeague.ashx', data = post)
        if not 'message' in response or response['message'] != 'OK':
            xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením lig', xbmcgui.NOTIFICATION_ERROR, 5000)
            sys.exit()         
        for item in response['data']:
            if filtered == False or item['Id'] not in blacklist['SportLeagueIds']:
                SportLeagues.append({'id' : item['Id'], 'league' : item['Value']})
        valid_to = int(time.time()) + 60*60*24
        data.update({SportTypeId: { 'data' : SportLeagues, 'valid_to' : valid_to}})
        save_SportLeagues(data)
    else:
        for SportLeague in data[str(SportTypeId)]['data']:
            if filtered == False or SportLeague['id'] not in blacklist['SportLeagueIds']:
                SportLeagues.append({'id' : SportLeague['id'], 'league' : SportLeague['league']})
    return SportLeagues

def get_Videos(SportTypeId, SportLeagueId, Live):
    streams = []
    post = {'Lang' : 'cz'}
    post.update({'Live' : Live})
    if SportTypeId is not None:
        post.update({'SportTypeId' : SportTypeId})    
    if SportLeagueId is not None:
        post.update({'SportLeagueId' : SportLeagueId})    
    response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetVideo.ashx', data = post)
    if not 'message' in response or response['message'] != 'OK':
        xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením videí', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()    
    for video in response['data']['videos']:
        streams.append({'id' : video['Id'], 'date' : video['Date'], 'title' : video['Value'], 'url' : video['Stream'], 'img' : video['Thumbnail'], 'available' : True})
    return streams

def get_VideoDetail(VideoId):
    post = {'Lang' : 'cz'}
    post.update({'VideoId' : VideoId})
    response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetVideoDetail.ashx', data = post)
    if not 'message' in response or response['message'] != 'OK':
        xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením videí', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()    
    return {'StreamHls' : response['data']['StreamHls'], 'Stream' : response['data']['Stream'], 'StreamDash' : response['data']['StreamDash']}

def play_tvcomcz_stream(url):
    list_item = xbmcgui.ListItem()
    list_item.setProperty('inputstream','inputstream.adaptive')
    list_item.setProperty('inputstream.adaptive.manifest_type','hls')
    list_item.setPath(url)
    xbmcplugin.setResolvedUrl(_handle, True, list_item)

def list_streams(streams):
    for stream in streams:
        if stream['available'] == True:
            list_item = xbmcgui.ListItem(label = stream['title'] + '\n[COLOR=gray]' + stream['date'] + '[/COLOR]')
            list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title'] + '\n' + stream['date']}) 
            list_item.setArt({'icon': stream['img']})
            url = get_url(action='play_tvcomcz_stream', url = stream['url']) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        else:
            list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] + '\n' + stream['date'] + '[/COLOR]')
            list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title'] + '\n' + stream['date']}) 
            list_item.setArt({'icon': stream['img']})
            url = get_url(action='play_tvcomcz_stream', url = stream['url']) 
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

def list_tvcomcz_league(SportTypeId, SportLeagueId, label):
    xbmcplugin.setPluginCategory(_handle, label)
    SportTypeId = int(SportTypeId)
    SportLeagueId = int(SportLeagueId)
    streams = get_Videos(SportTypeId = SportTypeId, SportLeagueId = SportLeagueId, Live = 0)
    list_streams(streams)
    xbmcplugin.endOfDirectory(_handle)

def list_tvcomcz_leagues(SportTypeId, label):
    SportTypeId = int(SportTypeId)
    SportLeagues = get_SportLeagues(SportTypeId = SportTypeId)
    for SportLeague in SportLeagues:
        list_item = xbmcgui.ListItem(label = SportLeague['league'])
        url = get_url(action='list_tvcomcz_league', SportTypeId = SportTypeId, SportLeagueId = SportLeague['id'], label = label + ' \ ' + SportLeague['league'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def list_tvcomcz_submenu(SportTypeId, label):
    xbmcplugin.setPluginCategory(_handle, label)
    SportTypeId = int(SportTypeId)
    SportTypes = get_SportTypes()
    
    if SportTypeId >= 0:
        list_item = xbmcgui.ListItem(label = 'Soutěže')
        url = get_url(action='list_tvcomcz_leagues', SportTypeId = SportTypeId, label = label + ' \ ' + 'Soutěže')  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

        streams = get_Videos(SportTypeId = SportTypeId, SportLeagueId = None, Live = 0)
        list_streams(streams)
    else:
        for SportType in SportTypes:
            if SportType['other'] == True:
                list_item = xbmcgui.ListItem(label = SportType['sport'])
                url = get_url(action='list_tvcomcz_submenu', SportTypeId = SportType['id'], label = label + ' \ ' + SportType['sport'])
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def list_tvcomcz_today(label):
    xbmcplugin.setPluginCategory(_handle, label)
    post = {'Lang' : 'cz'}
    post.update({'ymd' : datetime.now().strftime('%Y%m%d')})
    response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetSportTypeDay.ashx', data = post)
    if not 'message' in response or response['message'] != 'OK':
        xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením dnešních přenosů', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()        
    SportTypes = get_SportTypes()
    SportTypeIds = []
    streams = []
    for sport in response['data']:
        if sport['Id'] in [x['id'] for x in SportTypes] and (int(sport['Lives']) > 0 or int(sport['Future']) > 0):
            SportTypeIds.append(sport['Id'])
    if len(SportTypeIds) > 0:
        for SportTypeId in SportTypeIds:
            post = {'Lang' : 'cz'}
            post.update({'SportTypeId' : SportTypeId, 'ymd' : datetime.now().strftime('%Y%m%d')})
            response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetSportLeagueDay.ashx', data = post)
            if not 'message' in response or response['message'] != 'OK':
                xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením dnešních přenosů', xbmcgui.NOTIFICATION_ERROR, 5000)
                sys.exit()      
            for item in response['data']:
                SportLeagues = get_SportLeagues(SportTypeId)
                if item['Id'] in [x['id'] for x in SportLeagues] or (item['Id'] == 0 and len(SportLeagues) == 0):
                    for video in item['Videos']:
                        if video['VideoType'] == 'L':
                            streams.append({'id' : video['Id'], 'date' : video['Date'], 'title' : video['Value'], 'url' : video['Stream'], 'img' : video['Thumbnail'], 'available' : True})
                        elif video['VideoType'] == 'F':
                            streams.append({'id' : video['Id'], 'date' : video['Date'], 'title' : video['Value'], 'url' : video['Stream'], 'img' : video['Thumbnail'], 'available' : False})
    # streams = sorted(streams, key=lambda d: d['date'])
    list_streams(streams)
    xbmcplugin.endOfDirectory(_handle)

def get_tvcomcz_live_streams():
    live_streams = []

    post = {'Lang' : 'cz'}
    post.update({'ymd' : datetime.now().strftime('%Y%m%d')})
    response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetSportTypeDay.ashx', data = post)
    if not 'message' in response or response['message'] != 'OK':
        xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením dnešních přenosů', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()        
    SportTypes = get_SportTypes()
    SportTypeIds = []
    for sport in response['data']:
        if sport['Id'] in [x['id'] for x in SportTypes] and (int(sport['Lives']) > 0 or int(sport['Future']) > 0):
            SportTypeIds.append(sport['Id'])
    if len(SportTypeIds) > 0:
        for SportTypeId in SportTypeIds:
            post = {'Lang' : 'cz'}
            post.update({'SportTypeId' : SportTypeId, 'ymd' : datetime.now().strftime('%Y%m%d')})
            response = call_api(url = 'http://mobileapi.tvcom.cz/MobileApi2/GetSportLeagueDay.ashx', data = post)
            if not 'message' in response or response['message'] != 'OK':
                xbmcgui.Dialog().notification('TVcom.cz', 'Problém s načtením dnešních přenosů', xbmcgui.NOTIFICATION_ERROR, 5000)
                sys.exit()      
            for item in response['data']:
                SportLeagues = get_SportLeagues(SportTypeId)
                if item['Id'] in [x['id'] for x in SportLeagues] or (item['Id'] == 0 and len(SportLeagues) == 0):
                    for video in item['Videos']:
                        startts = int(time.mktime(time.strptime(video['Date'].replace('. ', '.'), '%d.%m.%Y %H:%M:%S')))
                        if video['VideoType'] == 'L':
                            live_streams.append({ 'service' : 'tvcom.cz', 'type' : 'live', 'link' : video['Stream'], 'playable' : 1, 'cas' : video['Date'], 'startts' : startts, 'endts' : None, 'title' : video['Value'], 'image' : video['Thumbnail']})
                        elif video['VideoType'] == 'F':
                            live_streams.append({ 'service' : 'tvcom.cz', 'type' : 'future', 'link' : video['Stream'], 'playable' : 0, 'cas' : video['Date'], 'startts' : startts, 'endts' : None, 'title' : video['Value'], 'image' : video['Thumbnail']})
    return live_streams

def list_bl_SportTypes(label):
    xbmcplugin.setPluginCategory(_handle, label)
    blacklist = load_blacklist()
    mainlist = load_mainlist()
    
    list_item = xbmcgui.ListItem(label = 'Zakázat vše')
    url = get_url(action='change_blacklist', SportTypeId = -999, toggle = 1)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label = 'Povolit vše')
    url = get_url(action='change_blacklist', SportTypeId = -999, toggle = 0)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    SportTypes = get_SportTypes(filtered = False)
    for SportType in sorted(SportTypes, key=lambda d: d['sport']):
        if 'SportTypeIds' not in blacklist or SportType['id'] not in blacklist['SportTypeIds']:
            if SportType['id'] >= 0:
                if SportType['id'] in mainlist:
                    list_item = xbmcgui.ListItem(label = '[B]' + SportType['sport'] + '[/B]')
                    list_item.addContextMenuItems([('Zakázat', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_blacklist&toggle=1&SportTypeId=' + str(SportType['id']) + ')'),
                                                    ('Odebrat z hlavní obrazovky', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_mainlist&toggle=0&SportTypeId=' + str(SportType['id']) + ')')])                   
                else:
                    list_item = xbmcgui.ListItem(label = SportType['sport'])
                    list_item.addContextMenuItems([('Zakázat', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_blacklist&toggle=1&SportTypeId=' + str(SportType['id']) + ')'),
                                                    ('Přidat na hlavní obrazovku', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_mainlist&toggle=1&SportTypeId=' + str(SportType['id']) + ')')])                   
        else:
            if SportType['id'] in mainlist:
                list_item = xbmcgui.ListItem(label = '[B][COLOR=gray]' + SportType['sport'] + '[/COLOR][/B]')
                list_item.addContextMenuItems([('Povolit', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_blacklist&toggle=0&SportTypeId=' + str(SportType['id']) + ')'),                   
                                                ('Odebrat z hlavní obrazovky', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_mainlist&toggle=0&SportTypeId=' + str(SportType['id']) + ')')])                   
            else:
                list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + SportType['sport'] + '[/COLOR]')
                list_item.addContextMenuItems([('Povolit', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_blacklist&toggle=0&SportTypeId=' + str(SportType['id']) + ')')])
        url = get_url(action='list_bl_SportLeagues', SportTypeId = SportType['id'], label = label + ' \ ' + SportType['sport'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)        

def list_bl_SportLeagues(SportTypeId, label):
    xbmcplugin.setPluginCategory(_handle, label)
    SportTypeId = int(SportTypeId)
    blacklist = load_blacklist()

    list_item = xbmcgui.ListItem(label = 'Zakázat vše')
    url = get_url(action='change_blacklist', SportTypeId = SportTypeId, SportLeagueId = -999, toggle = 1)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label = 'Povolit vše')
    url = get_url(action='change_blacklist', SportTypeId = SportTypeId, SportLeagueId = -999, toggle = 0)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    

    SportLeagues = get_SportLeagues(SportTypeId, filtered = False)
    for SportLeague in SportLeagues:
        if SportLeague['id'] > 0:
            if 'SportLeagueIds' not in blacklist or SportLeague['id'] not in blacklist['SportLeagueIds']:
                list_item = xbmcgui.ListItem(label = SportLeague['league'])
                list_item.addContextMenuItems([('Zakázat', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_blacklist&toggle=1&SportLeagueId=' + str(SportLeague['id']) + ')')])                   
            else:            
                list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + SportLeague['league'] + '[/COLOR]')
                list_item.addContextMenuItems([('Povolit', 'RunPlugin(plugin://plugin.video.sportstreams.cz?action=change_blacklist&toggle=0&SportLeagueId=' + str(SportLeague['id']) + ')')])                   
            url = get_url(action='list_bl_SportLeagues', SportTypeId = SportTypeId, label = label)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)        

def list_tvcomcz_main(label):
    xbmcplugin.setPluginCategory(_handle, label)
    addon = xbmcaddon.Addon()
    list_item = xbmcgui.ListItem(label = 'Dnes')
    url = get_url(action='list_today', label = 'Dnes')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    SportTypes = get_SportTypes()
    mainlist = load_mainlist()
    if len(mainlist) == 0:
        for SportType in SportTypes:
            if SportType['other'] == False:
                list_item = xbmcgui.ListItem(label = SportType['sport'])
                url = get_url(action='list_tvcomcz_submenu', SportTypeId = SportType['id'], label = SportType['sport'])
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    else:
        for SportType in SportTypes:
            if SportType['id'] in mainlist:
                list_item = xbmcgui.ListItem(label = SportType['sport'])
                url = get_url(action='list_tvcomcz_submenu', SportTypeId = SportType['id'], label = SportType['sport'])
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

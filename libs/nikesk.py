# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from urllib.error import HTTPError

import json
from datetime import datetime
import time

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])
    
def call_api(url, data = None, method = None):
    addon = xbmcaddon.Addon()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0', 'Accept': 'application/json; charset=utf-8'}    
    if data != None:
        data = urlencode(data)
        data = data.encode('utf-8')
    if method is not None:
        request = Request(url = url , data = data, method = method, headers = headers)
    else:
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

def get_nikesk_live_streams():
    live_streams = []
    response = call_api(url = 'https://api.nike.sk/api/nikeone/v1/stream/lobby')
    if len(response) > 0:
        for event in response:
            if 'match' in event and event['betOffer'] in ['LIVE', 'PREMATCH']:
                if 'stream' in event and 'streamParamId' in event['stream'] and event['stream']['streamParamId'] != 'NTV_DEFAULT':
                    url = event['stream']['streamParamId']
                else:
                    url = None
                title = event['match']['home']['sk'] + ' - ' + event['match']['away']['sk']
                description = event['tournamentName']['sk']
                startts = int(time.mktime(time.strptime(event['match']["startTime"][:-6], '%Y-%m-%dT%H:%M:%S')))
                image = 'https://api.nike.sk/api/cake-cms/nike-tv-image/?matchId=' + str(event['match']['id']) + '&tournamentId=' + str(event['match']['tournamentId']) + '&awayId=' + str(event['participants'][1]) + '&homeId=' + str(event['participants'][0]) + '&subTypeId=&mimeType=webp'
                if event['match']['isLive'] == True and event['stream']['streamParamId'] != 'NTV_DEFAULT':
                    live_streams.append({ 'service' : 'nike.sk', 'type' : 'live', 'link' : url, 'playable' : 1, 'cas' : time.strftime('%H:%M', time.strptime(event['match']["startTime"][:-6], '%Y-%m-%dT%H:%M:%S')),  'startts' : startts, 'endts' : None, 'title' : title, 'image' : image})
                else:
                    live_streams.append({ 'service' : 'nike.sk', 'type' : 'future', 'link' : url, 'playable' : 0, 'cas' : time.strftime('%d.%m.%Y %H:%M', time.strptime(event['match']["startTime"][:-6], '%Y-%m-%dT%H:%M:%S')), 'startts' : startts, 'endts' : None, 'title' : title, 'image' : image})
    return live_streams

def list_nikesk_live(label):
    xbmcplugin.setPluginCategory(_handle, label)
    streams = get_nikesk_live_streams()
    for stream in streams:
        if stream['type'] == 'live':
            list_item = xbmcgui.ListItem(label = stream['title'] +  ' (' + stream["cas"] + ')')
            list_item.setInfo('video', {'title' : stream['title']}) 
            list_item.setArt({'icon': stream['image']})
            url = get_url(action='play_nikesk_stream', id = stream['link'], type = 'live') 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        if stream['type'] == 'future':
            list_item = xbmcgui.ListItem(label = '[COLOR = gray]' + stream['title'] +  ' (' + stream["cas"] + ')' + '[/COLOR]')
            list_item.setInfo('video', {'title' : stream['title']}) 
            list_item.setArt({'icon': stream['image']})
            url = get_url(action='play_nikesk_stream', id = stream['link'], type = 'future') 
            list_item.setProperty('IsPlayable', 'false')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)    

def play_nikesk_stream(id, type = 'archiv'):
    if type == 'archiv':
        response = call_api(url = 'https://www.nike.sk/api/nike-tv-archive/stream/archive/' + str(id))
        if 'urlServerAuth' in response:
            url = response['urlServerAuth']
    else:
        url = id
    list_item = xbmcgui.ListItem()
    list_item.setProperty('inputstream','inputstream.adaptive')
    list_item.setProperty('inputstream.adaptive.manifest_type','hls')
    list_item.setPath(url)
    xbmcplugin.setResolvedUrl(_handle, True, list_item)

def list_nikesk_tournament(label, category, tournament):
    xbmcplugin.setPluginCategory(_handle, label)
    response = call_api(url = 'https://api.nike.sk/api/cake-cms/nike-tv-archive-overview-by-sport?sportCode=' + category + '&type=all&tournamentName=' + quote(tournament))
    if 'items' in response:
        for item in response['items']:
            list_item = xbmcgui.ListItem(label = item['title'] + '\n[COLOR=gray]' + time.strftime('%d.%m.%Y %H:%M', time.strptime(item["startTime"][:-6], '%Y-%m-%dT%H:%M:%S')) + '[/COLOR]')
            list_item.setInfo('video', {'title' : item['title'], 'plot' : item['title'] + '\n' + time.strftime('%d.%m.%Y %H:%M', time.strptime(item["startTime"][:-6], '%Y-%m-%dT%H:%M:%S'))}) 
            list_item.setArt({'icon': 'https://api.nike.sk/api/cake-cms/nike-tv-image/?archive=' + item['archive']['poster'] + '&mimeType=webp'})
            url = get_url(action='play_nikesk_stream', id = item['id'], type = 'archiv' ) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

def list_nikesk_category(label, category):
    xbmcplugin.setPluginCategory(_handle, label)
    response = call_api(url = 'https://api.nike.sk/api/cake-cms/nike-tv-archive-overview-by-sport?sportCode=' + category + '&type=all')
    if 'items' in response:
        if 'tournaments' in response:
            for item in response['tournaments']:
                list_item = xbmcgui.ListItem(label = item['name'])
                url = get_url(action='list_nikesk_tournament', label = label + ' / ' + item['name'], category = category, tournament = item['name'])  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        for item in response['items']:
            list_item = xbmcgui.ListItem(label = item['title'] + '\n[COLOR=gray]' + time.strftime('%d.%m.%Y %H:%M', time.strptime(item["startTime"][:-6], '%Y-%m-%dT%H:%M:%S')) + '[/COLOR]')
            list_item.setInfo('video', {'title' : item['title'], 'plot' : item['title'] + '\n' + time.strftime('%d.%m.%Y %H:%M', time.strptime(item["startTime"][:-6], '%Y-%m-%dT%H:%M:%S'))}) 
            list_item.setArt({'icon': 'https://api.nike.sk/api/cake-cms/nike-tv-image/?archive=' + item['archive']['poster'] + '&mimeType=webp'})
            url = get_url(action='play_nikesk_stream', id = item['id'], type = 'archiv' ) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

def list_nikesk_main(label):
    xbmcplugin.setPluginCategory(_handle, label)

    list_item = xbmcgui.ListItem(label = 'Live a plánované streamy')
    url = get_url(action='list_nikesk_live', label = 'Live a plánované streamy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    response = call_api(url = 'https://api.nike.sk/api/cake-cms/nike-tv-archive-overview-v2?type=all')
    if 'sports' in response:
        for category in response['sports']:
            list_item = xbmcgui.ListItem(label = category['sportName'])
            url = get_url(action='list_nikesk_category', label = category['sportName'], category = category['sportCode'])  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

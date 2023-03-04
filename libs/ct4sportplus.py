# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

import json, gzip
import xml.etree.ElementTree as ET
from datetime import datetime,timedelta

from libs.utils import get_url

_url = sys.argv[0]
if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def call_api(url, data, compression = 0):
    addon = xbmcaddon.Addon()
    if compression == 0:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0', 'Accept': 'application/json; charset=utf-8'}    
    else:
        headers = {'Accept': 'application/json', 'Accept-Encoding': 'gzip'}    
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
            if compression == 1:
                html = gzip.decompress(html)
            data = json.loads(html)
            return data
        else:
            return []
    except HTTPError as e:
        return { 'err' : e.reason }      

def call_api_xml(url, data):
    addon = xbmcaddon.Addon()    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}    
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
            data = ET.fromstring(html).text
            return data
        else:
            return []
    except HTTPError as e:
        return { 'err' : e.reason }      

def play_ct4sportplus_stream(url):
    list_item = xbmcgui.ListItem(path = url)    
    list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    list_item.setProperty('inputstream', 'inputstream.adaptive')
    list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    list_item.setMimeType('application/dash+xml')
    list_item.setContentLookup(False)       
    xbmcplugin.setResolvedUrl(_handle, True, list_item)

def list_ct4sportplus_main(label):
    xbmcplugin.setPluginCategory(_handle, label)
    live_streams = get_ct4sportplus_live_streams()
    for stream in live_streams:
        if stream['type'] == 'live':
            list_item = xbmcgui.ListItem(label = stream['title'] +  ' (' + stream["cas"] + ')')
            list_item.setInfo('video', {'title' : stream['title']}) 
            list_item.setArt({'icon': stream['image']})
            url = get_url(action='play_ct4sportplus_stream', url = stream['link']) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        if stream['type'] == 'future':
            list_item = xbmcgui.ListItem(label = '[COLOR = gray]' + stream['title'] +  ' (' + stream["cas"] + ')' + '[/COLOR]')
            list_item.setInfo('video', {'title' : stream['title']}) 
            list_item.setArt({'icon': stream['image']})
            url = get_url(action='play_ct4sportplus_stream', url = stream['link']) 
            list_item.setProperty('IsPlayable', 'false')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)    

def get_ct4sportplus_live_streams():
    live_streams = []
    post = {'user' : 'iDevicesMotion'} 
    token = call_api_xml(url = 'https://www.ceskatelevize.cz/services/ivysilani/xml/token/', data = post)
    if len(token) == 0:
        xbmcgui.Dialog().notification('ČT4 Sport Plus', 'Nepodařilo se získat token', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit()         
    
    response = call_api(url = 'https://feed-sport.ceskatelevize.cz/current-shows', data = None)
    for channel in response:
        for type in response[channel]:
            if type == 'live':
                title = response[channel][type]['programTitle']
                img = response[channel][type]['imageUrl']
                start = datetime.fromtimestamp(int(response[channel][type]['time']))
                end = start + timedelta(minutes = int(response[channel][type]['footage']))
                startts = int(response[channel][type]['time'])
                endts = startts + int(response[channel][type]['footage']) * 60
                cas = start.strftime('%H:%M') + ' - ' + end.strftime('%H:%M')
                post = {'token' : token, 'ID' : 'CT' + channel, 'playerType' : 'iPad', 'quality' : '1080p'}
                program = call_api_xml(url = 'https://www.ceskatelevize.cz/services/ivysilani/xml/playlisturl', data = post)
                data = call_api( url= program, data = None)
                if 'playlist' in data:
                    for item in data['playlist']:
                        url = item['streamUrls']['main']
                        live_streams.append({ 'service' : 'ct4sportplus', 'type' : 'live', 'link' : url, 'playable' : 1, 'cas' : cas, 'startts' : startts, 'endts' : endts, 'title' : title, 'image' : img})
            if type == 'next':
                title = response[channel][type]['programTitle']
                img = response[channel][type]['imageUrl']
                start = datetime.fromtimestamp(int(response[channel][type]['time']))
                end = start + timedelta(minutes = int(response[channel][type]['footage']))
                startts = int(response[channel][type]['time'])
                endts = startts + int(response[channel][type]['footage']) * 60
                cas = start.strftime('%H:%M') + ' - ' + end.strftime('%H:%M')
                live_streams.append({ 'service' : 'ct4sportplus', 'type' : 'future', 'link' : None, 'playable' : 0, 'cas' : cas, 'startts' : startts, 'endts' : endts, 'title' : title, 'image' : img})
    live_streams = sorted(live_streams, key=lambda d: d['startts'])
    return live_streams




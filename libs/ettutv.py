# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

import json
from datetime import datetime
import time

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

tz_offset = int((time.mktime(datetime.now().timetuple())-time.mktime(datetime.utcnow().timetuple())))

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

def get_ettutv_live_streams():
    live_streams = []
    response = call_api(url = 'https://www.ettu.tv/api/content-box/?baseconfig=81&module=9960&live=true&limit=50&requiresFilters=false')
    if 'data' in response and len(response['data']) > 0:
        for event in response['data']:
            event_id = event['id']
            title = event['editorial']['languages'][0]['title']
            description = event['editorial']['languages'][0]['description']
            image = 'https://www.ettu.tv/image/400/225/' + event['editorial']['image']['path']
            startts = int(time.mktime(time.strptime(event['start_datetime']['date'], '%Y-%m-%d %H:%M:%S'))) + tz_offset
            if startts < time.mktime(datetime.now().timetuple()):
                live_streams.append({ 'service' : 'ettu.tv', 'type' : 'live', 'link' : event_id, 'playable' : 1, 'cas' : datetime.strftime(datetime.fromtimestamp(startts), '%H:%M'), 'startts' : startts, 'endts' : None, 'title' : title, 'image' : image})
            else:
                live_streams.append({ 'service' : 'ettu.tv', 'type' : 'future', 'link' : event_id, 'playable' : 0, 'cas' : datetime.strftime(datetime.fromtimestamp(startts), '%d.%m.%Y %H:%M'), 'startts' : startts, 'endts' : None, 'title' : title, 'image' : image})
    return live_streams

def list_ettutv_schedule(label):
    xbmcplugin.setPluginCategory(_handle, label)
    streams = get_ettutv_live_streams()
    for stream in streams:
        if stream['type'] == 'live':
            list_item = xbmcgui.ListItem(label = stream['title'] +  ' (' + stream["cas"] + ')')
            list_item.setInfo('video', {'title' : stream['title']}) 
            list_item.setArt({'icon': stream['image']})
            url = get_url(action='play_ettutv_stream', id = stream['link']) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        if stream['type'] == 'future':
            list_item = xbmcgui.ListItem(label = '[COLOR = gray]' + stream['title'] +  ' (' + stream["cas"] + ')' + '[/COLOR]')
            list_item.setInfo('video', {'title' : stream['title']}) 
            list_item.setArt({'icon': stream['image']})
            url = get_url(action='play_ettutv_stream', id = stream['link']) 
            list_item.setProperty('IsPlayable', 'false')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)    

def play_ettutv_stream(id):
    response = call_api(url = 'https://www.ettu.tv/api/v3/contents/' + str(id) + '/access/hls', data = None, method = 'POST')
    if 'data' in response and 'stream' in response['data']:
        url = response['data']['stream']
        list_item = xbmcgui.ListItem()
        list_item.setProperty('inputstream','inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type','hls')
        list_item.setPath(url)
        xbmcplugin.setResolvedUrl(_handle, True, list_item)

def list_ettutv_filter(label, id, cat_id, page):
    addon = xbmcaddon.Addon()
    pagesize = addon.getSetting('pagesize')
    if int(id) == -1:
        url = 'https://www.ettu.tv/api/module/39781/content?limit=' + str(pagesize) + '&page=' + str(page) + '&userCountry=CZ'
    else:
        if int(cat_id) == '-1':
            url = 'https://www.ettu.tv/api/module/39781/content?limit=' + str(pagesize) + '&page=' + str(page) + '&userCountry=CZ&metadata_id=' + id
        else:
            url = 'https://www.ettu.tv/api/module/39781/content?limit=' + str(pagesize) + '&page=' + str(page) + '&userCountry=CZ&cat' + cat_id + '_id=' + id
    response = call_api(url = url)
    if 'data' in response and len(response['data']) > 0:
        last_page = int(response['meta']['last_page'])
        for event in response['data']:
            event_id = event['id']
            title = event['editorial']['languages'][0]['title']
            description = event['editorial']['languages'][0]['description']
            image = 'https://www.ettu.tv/image/400/225/' + event['editorial']['image']['path']
            startts = int(time.mktime(time.strptime(event['start_datetime']['date'], '%Y-%m-%d %H:%M:%S'))) + tz_offset
            list_item = xbmcgui.ListItem(label = title + ' (' + datetime.strftime(datetime.fromtimestamp(startts), '%d.%m.%Y %H:%M') + ')\n' + description)
            list_item.setInfo('video', {'title' : title, 'plot' : title + '\n' + description}) 
            list_item.setArt({'icon': image})
            url = get_url(action='play_ettutv_stream', id = event_id) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        if int(page) < last_page:
            list_item = xbmcgui.ListItem(label = 'Další strana (' + str(int(page) + 1) + '/' + str(last_page) + ')')
            url = get_url(action='list_ettutv_filter', label = label, id = str(id), cat_id = str(cat_id), page = int(page) + 1)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_ettutv_categories(label, filter, is_category = 0):
    xbmcplugin.setPluginCategory(_handle, label)
    response = call_api(url = 'https://www.ettu.tv/api/module/39781/content?limit=1&page=1&userCountry=CZ')
    if 'filters' in response and 'filter1' in response['filters']:
        for category in response['filters'][filter]:
            id = category['id']
            if int(is_category) == 0:
                cat_id = -1
            else:
                cat_id = category['category']['metadata_category_type_id']
            name = category['display_name']
            if name is None:
                name = category['category']['avcmp_name']
            list_item = xbmcgui.ListItem(label = name)
            url = get_url(action='list_ettutv_filter', label = name, id = str(id), cat_id = str(cat_id), page = 1)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

def list_ettutv_main(label):
    xbmcplugin.setPluginCategory(_handle, label)

    list_item = xbmcgui.ListItem(label = 'Live a plánované streamy')
    url = get_url(action='list_ettutv_schedule', label = 'Live a plánované streamy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = 'Všechny')
    url = get_url(action='list_ettutv_filter', label = 'Všechny', id = -1, cat_id = -1, page = 1)  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = 'Soutěže')
    url = get_url(action='list_ettutv_categories', label = 'Soutěže', category_filter = 'filter1', is_category = 1)  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = 'Sezóny')
    url = get_url(action='list_ettutv_categories', label = 'Sezóny', category_filter = 'filter3', is_category = 0)  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label = 'Kategorie')
    url = get_url(action='list_ettutv_categories', label = 'Kategorie', category_filter = 'filter5', is_category = 0)  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup
import requests
import re

import json
from datetime import datetime
import time

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

tz_offset = int((time.mktime(datetime.now().timetuple())-time.mktime(datetime.utcnow().timetuple())))

def call_api(url, data = None, method = None):
    addon = xbmcaddon.Addon()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0', 'Accept': 'application/json; charset=utf-8', 'X-Requested-With' : 'XMLHttpRequest'}    
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
    except URLError as e:
        return { 'err' : e.reason }      

def format_datetime(date):
    if 'Z' in date:
        return date.replace('Z','')
    if '+' in date:
        return date[:-6]
    return date

def play_volejtv_live_stream(id):
    from random import randint
    userid = randint(100000000000, 999999999999)
    response = call_api(url = 'https://api-volejtv-prod.apps.okd4.devopsie.cloud/api/match/' + str(id) + '?userId=' + str(userid))
    if response['livematch']['video_url'] is not None:
        url = 'https:' + response['livematch']['video_url']
        list_item = xbmcgui.ListItem()
        list_item.setPath(url + '|Referer=https://volej.tv/')    
        list_item.setContentLookup(False)
        xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Volej.tv', 'Stream není k dispozici', xbmcgui.NOTIFICATION_ERROR, 5000)

def load_page(url):
    r = requests.get(url , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def get_video_url(url):
    soup = load_page(url)
    scripts = soup.find_all('script')
    urls = []
    for script in scripts:
        match = re.findall('https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(script))
        for url in match:
            if '.m3u8' in url:
                urls.append(url.rstrip(',').rstrip('\''))
    if len(urls) > 0:
        return urls[0]
    else:
        return None

def play_tipossk_stream(url):
    url = get_video_url(url)
    if url is not None:
        list_item = xbmcgui.ListItem()
        list_item.setProperty('inputstreamaddon','inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type','hls')
        list_item.setPath(url)
        xbmcplugin.setResolvedUrl(_handle, True, list_item)

def get_tipossk_live_streams():
    today_date = datetime.today() 
    today_end_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day).timetuple())) + 60*60*24-1
    live_streams = []
    response = call_api(url = 'https://www.tipos.sk/Millennium.TiposTV/TIPOSTV/GetSchedule')
    if len(response) > 0:
        for item in response:
            title = item['team1'] + ' - ' + item['team2'] + '\n' + '[COLOR=gray]' + item['competition'] + ' - ' + item['tournament'] + '[/COLOR]'
            startts = int(time.mktime(time.strptime(format_datetime(item['date']), '%Y-%m-%dT%H:%M:%S')))
            if startts < time.mktime(datetime.now().timetuple()) and startts > today_end_ts-(24*60*60):
                live_streams.append({ 'service' : 'tipos.sk', 'type' : 'live', 'link' : item['live'], 'playable' : 1, 'cas' : datetime.strftime(datetime.fromtimestamp(startts), '%H:%M'), 'startts' : startts, 'endts' : None, 'title' : title, 'image' : ''})
            elif startts < today_end_ts and startts > today_end_ts-(24*60*60):
                live_streams.append({ 'service' : 'tipos.sk', 'type' : 'future', 'link' : item['live'], 'playable' : 0, 'cas' : datetime.strftime(datetime.fromtimestamp(startts), '%H:%M'), 'startts' : startts, 'endts' : None, 'title' : title, 'image' : ''})                
    return live_streams

def list_tipossk_live(label):
    xbmcplugin.setPluginCategory(_handle, label)
    streams = get_tipossk_live_streams()
    for stream in streams:
        if stream['type'] == 'live':
            list_item = xbmcgui.ListItem(label = stream['title'] +  ' (' + datetime.strftime(datetime.fromtimestamp(stream['startts']), '%d.%m.%Y %H:%M') + ')')
            list_item.setInfo('video', {'title' : stream['title']}) 
            url = get_url(action='play_tipossk_stream', url = stream['link']) 
            list_item.setContentLookup(False)          
            list_item.setProperty('IsPlayable', 'true')        
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        else:
            list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] +  ' (' + datetime.strftime(datetime.fromtimestamp(stream['startts']), '%d.%m.%Y %H:%M') + ')' + '[/COLOR]')
            list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title']}) 
            url = get_url(action='list_volejtv_live', label = label)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)  

def list_tipossk_archiv(label):
    xbmcplugin.setPluginCategory(_handle, label)
    response = call_api(url = 'https://www.tipos.sk/Millennium.TiposTV/TIPOSTV/GetArchive')
    if len(response) > 0:
        for item in response:
            if item['competition'] + ' - ' + item['tournament'] == label:
                title = item['team1'] + ' - ' + item['team2']
                startts = int(time.mktime(time.strptime(format_datetime(item['date']), '%Y-%m-%dT%H:%M:%S')))
                list_item = xbmcgui.ListItem(label = title + ' (' + datetime.strftime(datetime.fromtimestamp(startts), '%d.%m.%Y %H:%M') + ')\n' + '[COLOR=gray]' + item['competition'] + ' - ' + item['tournament'] + '[/COLOR]')
                list_item.setInfo('video', {'title' : title, 'plot' : title + '\n' + item['competition'] + ' - ' + item['tournament']}) 
                url = get_url(action='play_tipossk_stream', url = item['archive']) 
                list_item.setContentLookup(False)          
                list_item.setProperty('IsPlayable', 'true')        
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

def list_tipossk_main(label):
    xbmcplugin.setPluginCategory(_handle, label)

    list_item = xbmcgui.ListItem(label = 'Live a plánované streamy')
    url = get_url(action='list_tipossk_live', label = 'Live a plánované streamy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    response = call_api(url = 'https://www.tipos.sk/Millennium.TiposTV/TIPOSTV/GetArchive')
    if len(response) > 0:
        competitions = []
        for item in response:
            competition = item['competition'] + ' - ' + item['tournament']
            if competition not in competitions:
                competitions.append(competition)

        for competition in competitions:
            list_item = xbmcgui.ListItem(label = competition)
            url = get_url(action='list_tipossk_archiv', label = competition)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle, cacheToDisc = True)

# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin

from bs4 import BeautifulSoup

import requests

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def play_pingpongtv_video(link):
    if not xbmc.getCondVisibility('System.HasAddon(plugin.video.youtube)'):
        xbmcgui.Dialog().notification('Ping-pong.tv', 'Pro přehrávání videí je třeba mít nainstalovaný Youtube doplněk!', xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        soup = load_page('https://www.ping-pong.tv' + link)
        iframe = soup.find('iframe')
        videoid = ''
        videoid = iframe.get('src').replace('https://www.youtube.com/embed/', '')
        if len(videoid) > 0:
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % videoid
            list_item = xbmcgui.ListItem()
            list_item.setPath(url)
            xbmcplugin.setResolvedUrl(_handle, True, list_item)    

def list_pingpongtv_streams(label, filter, value):
    xbmcplugin.setPluginCategory(_handle, label)
    soup = load_page('https://www.ping-pong.tv/?' + filter + '=' + value + '&page=9999') 
    items = soup.find_all('div', {'class' : 'hp-tv__item'})
    for item in items:
        href = item.find('a').get('href')
        img = item.find('img').get('src')
        title = item.find('h3').text
        subtitle = ''
        subtitles = item.find('span').text.strip().replace('\n', '').split('/')
        for part in subtitles:
            if len(subtitle) == 0:
                subtitle = part.strip()
            else:
                subtitle = subtitle + ' / ' + part.strip()
        list_item = xbmcgui.ListItem(label = title + '\n' + '[COLOR=gray]' + subtitle + '[/COLOR]')
        list_item.setInfo('video', {'title' : title}) 
        url = get_url(action='play_pingpongtv_video', link = href) 
        list_item.setArt({'icon': img})
        list_item.setContentLookup(False)          
        list_item.setProperty('IsPlayable', 'true')        
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)        

def list_pingpongtv_filter_items(label, filter):
    xbmcplugin.setPluginCategory(_handle, label)
    soup = load_page('https://www.ping-pong.tv')
    select_filter = soup.find_all('select', {'id': filter})
    for select in select_filter:
        for option in select.find_all('option'):
            list_item = xbmcgui.ListItem(label = option.text)
            if len(option.get('value')) == 0:
                value = 0
            else:
                value = option.get('value')
            url = get_url(action = 'list_pingpongtv_streams', select_filter = filter, value = value, label = option.text)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_pingpongtv_main(label):
    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = 'Podle kategorie')
    url = get_url(action = 'list_pingpongtv_filter_items', select_filter = 'category', label = 'Kategorie')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = 'Podle soutěže')
    url = get_url(action = 'list_pingpongtv_filter_items', select_filter = 'competition', label = 'Soutěže')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = 'Podle týmu')
    url = get_url(action = 'list_pingpongtv_filter_items', select_filter = 'team', label = 'Týmy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = 'Podle štítku')
    url = get_url(action = 'list_pingpongtv_filter_items', select_filter = 'tag', label = 'Štítky')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = 'Vše')
    url = get_url(action = 'list_pingpongtv_streams', select_filter = 'all', value = ' ', label = 'Vše')
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def load_page(url):
    r = requests.get(url , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

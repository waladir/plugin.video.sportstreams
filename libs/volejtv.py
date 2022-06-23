# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin

from urllib.parse import parse_qsl
from urllib.parse import urlencode

from bs4 import BeautifulSoup
import re

import requests

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def play_volejtv_video(link):
    soup = load_page(link)
    scripts = soup.find_all('script')
    url = None
    for script in scripts:
        match = re.findall('http?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(script))
        for link in match:
            url = link
    if url is not None:
        list_item = xbmcgui.ListItem()
        list_item.setPath(url)
        xbmcplugin.setResolvedUrl(_handle, True, list_item)

def list_volejtv_streams(link, label):
    xbmcplugin.setPluginCategory(_handle, label)

    soup = load_page(link)
    items = soup.find_all('div', {'class': 'col-md-4'})
    
    for item in items:
        league = item.find('div', {'class' : 'soutez'}).getText()
        date = item.find('div', {'class' : 'text-uppercase'}).getText()
        divHome = item.find('div', {'class' : 'domaciLogo'})
        homeTeam = divHome.find('img').get('title')
        divHost = item.find('div', {'class' : 'hosteLogo'})
        hostTeam = divHost.find('img').get('title')
        score = item.find('div', {'class' : 'score'}).getText()
        img = 'https://volej.tv/' + divHome.find('img').get('src').replace('_logo','').replace('klub','team').replace('png','webp')
        href = 'https://volej.tv/' + item.find('a', {'class' : 'smallPlayer'}).get('href')

        title = homeTeam + ' - ' + hostTeam + '  ' + '[COLOR=gray] ' + date + ' [/COLOR]' + '\n' + league

        list_item = xbmcgui.ListItem(label = title)
        list_item.setInfo('video', {'title' : title}) 
        url = get_url(action='play_volejtv_video', link = href) 
        list_item.setArt({'icon': img})
        list_item.setContentLookup(False)          
        list_item.setProperty('IsPlayable', 'true')        
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_volejtv_main(label):
    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label = 'Extraliga muži')
    url = get_url(action='list_volejtv_streams', link = 'https://volej.tv/extraliga-muzi/', label = 'Extraliga muži')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    list_item = xbmcgui.ListItem(label = 'Extraliga ženy')
    url = get_url(action='list_volejtv_streams', link = 'https://volej.tv/extraliga-zeny/', label = 'Extraliga ženy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    list_item = xbmcgui.ListItem(label = 'Ostatní přenosy')
    url = get_url(action='list_volejtv_streams', link = 'https://volej.tv/ostatni/', label = 'Ostatní přenosy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    list_item = xbmcgui.ListItem(label = 'Poslední streamy')
    url = get_url(action='list_volejtv_streams', link = 'https://volej.tv/', label = 'Poslední streamy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        

    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def load_page(url):
    r = requests.get(url , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

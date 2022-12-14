# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from xbmcvfs import translatePath

import json
import codecs
from datetime import date
import time

from bs4 import BeautifulSoup
import re

import requests

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def load_scheduler():
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'scheduler.txt')
    data = {}
    if os.path.exists(filename):
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as file:
                for row in file:
                    data = json.loads(row[:-1])
        except IOError as error:
            if error.errno != 2:
                xbmcgui.Dialog().notification('Huste.tv', 'Chyba při načtení plánovače', xbmcgui.NOTIFICATION_ERROR, 5000)
    return data

def get_live_video_url(link, quality):
    soup = load_page(link)
    items = soup.find('div',{'class' : 'b-iframe-video'}).find_all('iframe')
    for item in items:
        embeded = item.get('src')
        soup = load_page(embeded)
        scripts = soup.find_all('script')
        urls = []
        for script in scripts:
            match = re.findall('https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(script))
            for url in match:
                print(url)
                if '.m3u8' in url:
                    urls.append(url.rstrip(',').rstrip('\''))
    link = None
    if len(urls) > 0:
        if quality == 'nízká':
            link = urls[0]
        else:
            link = urls[-1]
    return link

def get_video_url(link, quality):
    soup = load_page(link)
    items = soup.find('div',{'class' : 'b-iframe-video'}).find_all('iframe')
    for item in items:
        embeded = item.get('src')
        soup = load_page(embeded)
        scripts = soup.find_all('script')
        urls = []
        for script in scripts:
            match = re.findall('https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(script))
            for url in match:
                if '.mp4' in url:
                    urls.append(url.rstrip(',').rstrip('\''))
    link = None
    if len(urls) > 0:
        if quality == 'nízká':
            link = urls[0]
        else:
            link = urls[-1]
    return link

def play_hustetv_video_scheduler(link, label):
    import xbmc
    addon = xbmcaddon.Addon()
    link = get_live_video_url(link, addon.getSetting('quality'))
    addon = None
    if link is not None:
        playlist=xbmc.PlayList(1)
        playlist.clear()
        list_item = xbmcgui.ListItem(path = link)
        list_item.setProperty('inputstreamaddon','inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type','hls')
        list_item.setInfo('video', {'title' : label}) 
        xbmc.PlayList(1).add(link, list_item)
        xbmc.Player().play(playlist)    

def play_hustetv_live_video(link, label):
    addon = xbmcaddon.Addon()
    link = get_live_video_url(link, addon.getSetting('quality'))
    if link is not None:
        list_item = xbmcgui.ListItem()
        list_item.setProperty('inputstreamaddon','inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type','hls')
        list_item.setPath(link)
        xbmcplugin.setResolvedUrl(_handle, True, list_item)

def play_hustetv_video(link, label):
    addon = xbmcaddon.Addon()
    link = get_video_url(link, addon.getSetting('quality'))
    if link is not None:
        list_item = xbmcgui.ListItem()
        list_item.setPath(link)
        xbmcplugin.setResolvedUrl(_handle, True, list_item)

def list_hustetv_items(link, label):
    xbmcplugin.setPluginCategory(_handle, label)
    soup = load_page(link)
    items = soup.find_all('article', {'class': 'b-article'})
    previous_page = None
    next_page = None
    if soup.find('ul', {'class': 'pagination'}):
        previous_page = soup.find('ul', {'class': 'pagination'}).find('a', {'aria-label' : 'Naspäť'})
        next_page = soup.find('ul', {'class': 'pagination'}).find('a', {'aria-label' : 'Ďalej'})

    if previous_page is not None:
        list_item = xbmcgui.ListItem(label = 'Předchozí strana')
        url = get_url(action='list_hustetv_items', link = previous_page.get('href'), label = label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    for item in items:
        a = item.find('h3', {'class' : 'title'}).find('a')
        title = a.get('title')
        a_sub = item.find('h4', {'class' : 'subtitle'}).find('a')
        subtitle = ''
        for row in a_sub.contents:
            subtitle = subtitle + str(row)
        if len(subtitle) > 0:
            title = title + ' (' + subtitle + ')'
        link = a.get('href')

        img = item.find('img').get('data-original')

        list_item = xbmcgui.ListItem(label = title)
        list_item.setInfo('video', {'title' : title}) 
        url = get_url(action='play_hustetv_video', link = link, label = label + ' / ' + title) 
        list_item.setArt({'icon': img})
        list_item.setContentLookup(False)          
        list_item.setProperty('IsPlayable', 'true')        
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)

    if next_page is not None:
        list_item = xbmcgui.ListItem(label = 'Následující strana')
        url = get_url(action='list_hustetv_items', link = next_page.get('href'), label = label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def list_hustetv_submenu(link, label):
    xbmcplugin.setPluginCategory(_handle, label)    
    soup = load_page(link)
    navbar_root = soup.find_all('li', {'class' : 'sub'})
    for item_root in navbar_root:
        navbar = item_root.find_all('div', {'class' : 'w-more'})
        for item in navbar:
            a = item.find('a')
            if  a.get('title') == label:
                navbar_row = item_root.find('ul', {'class' : 'nav'})
                for item_row in navbar_row.find_all('a'):
                    title = item_row.get('title')
                    link = item_row.get('href')
                    list_item = xbmcgui.ListItem(label = title)
                    url = get_url(action='list_hustetv_items', link = link, label = label + ' / ' + title)  
                    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def list_hustetv_archiv(link, label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)
    soup = load_page(link)
    archiv_list = soup.find('div', {'class': 'e-filter'}).find_all('a')
    categories = {}
    for a in archiv_list:
        title = a.get('title')
        link = a.get('href')
        categories.update({title : link})
    
    if addon.getSetting('category_order') == 'podle abecedy':
        category_keys = sorted(categories.keys())
    else:
        category_keys = categories.keys()
    for category in category_keys:
        list_item = xbmcgui.ListItem(label = category)
        url = get_url(action='list_hustetv_items', link = categories[category], label = label + ' / ' + category)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        
    xbmcplugin.endOfDirectory(_handle)

def list_hustetv_live(label):
    addon = xbmcaddon.Addon()
    xbmcplugin.setPluginCategory(_handle, label)
    live_streams = get_hustetv_live_streams()

    for stream in live_streams:
        if stream['type'] == 'live':
            if int(stream['playable']) == 1:
                list_item = xbmcgui.ListItem(label = stream['title'])
                list_item.setInfo('video', {'title' : stream['title']}) 
                url = get_url(action='play_hustetv_live_video', link = stream['link'], label = label + ' / ' + stream['title']) 
                list_item.setContentLookup(False)          
                list_item.setProperty('IsPlayable', 'true')        
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
            else:
                list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] + '[/COLOR]')
                url = get_url(action='list_hustetv_live', label = label)  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        if stream['type'] == 'future':
            list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] + '[/COLOR]')
            url = get_url(action='list_hustetv_live', label = label)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def get_hustetv_live_streams():
    live_streams = []
    link = 'https://huste.joj.sk/live'
    soup = load_page(link)
    today = soup.find('div', {'class' : 'b-live-games'})
    datum = date.today().strftime('%d.%m.%Y')
    if today:
        games = today.find_all('article', {'class' : 'b-article'})
        for game in games:
            if game.find('a', {'class' : 'label-live'}):
                link = game.find('a', {'class' : 'label-live'}).get('href')
                cas = 'LIVE'
            else:
                cas = game.find('div', {'class' : 'date'}).get_text()
            title = game.find('h3', {'class' : 'title'}).get_text()
            titles = []
            for row in title.split('\n'):
                if len(row.strip()) > 0: 
                    titles.append(row.strip())
            categories = game.find('ul', {'class' : 'e-breadcrumbs'}).find_all('a')
            category_title = []
            for category in categories:
                category_title.append(category.get_text())
            title = (' - ').join(titles) + ' (' + datum + ' ' + cas + ')'
            if cas == 'LIVE':
                live_streams.append({ 'service' : 'huste.tv', 'type' : 'live', 'link' : link, 'playable' : 1, 'cas' : 'LIVE', 'startts' : -1, 'endts' : None, 'title' : title, 'image' : None})
            else:
                startts = int(time.mktime(time.strptime(datum + ' ' + cas, '%d.%m.%Y %H:%M')))
                live_streams.append({'service' : 'huste.tv', 'type' : 'live', 'link' : None, 'playable' : 0, 'cas' : datum + ' ' + cas, 'startts' : startts, 'endts' : None, 'title' : title, 'image' : None})

    future = soup.find_all('div', {'class' : 'b-live-calendar'})
    for day in future:
        datum = day.find('h3', {'class' : 'title'}).get_text()
        games = day.find_all('div', {'class' : 'b-l-game'})
        for game in games:
            cas = game.find('div', {'class' : 'date'}).get_text()
            hrefs = game.find_all('a')
            titles = []
            for href in hrefs:
                if href.get('class') and href.get('class')[0] == 'i':
                    titles.append(href.get('title'))
            categories = game.find('ul', {'class' : 'e-breadcrumbs'}).find_all('a')
            category_title = []
            for category in categories:
                category_title.append(category.get_text())

            title = (' - ').join(titles) + ' (' + datum + ' ' + cas + ')'
            startts = int(time.mktime(time.strptime(datum + ' ' + cas, '%d.%m.%Y %H:%M')))
            live_streams.append({ 'service' : 'huste.tv', 'type' : 'future', 'link' : None, 'playable' : 0, 'cas' : datum + ' ' + cas, 'startts' : startts, 'endts' : None, 'title' : title, 'image' : None})
    return live_streams


def list_hustetv_main(label):
    xbmcplugin.setPluginCategory(_handle, label)

    list_item = xbmcgui.ListItem(label = 'Live a plánované streamy')
    url = get_url(action='list_hustetv_live', label = 'Live a plánované streamy')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    soup = load_page('https://huste.joj.sk/')
    navbar = soup.find_all('div', {'class' : 'w-more'})
    for item in navbar:
        a = item.find('a')
        title = a.get('title')
        link = a.get('href')
        list_item = xbmcgui.ListItem(label = title)
        url = get_url(action='list_hustetv_submenu', link = link, label = title)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def load_page(url):
    r = requests.get(url , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

addon = None
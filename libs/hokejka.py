# -*- coding: utf-8 -*-
import sys
import os
import xbmcgui
import xbmcplugin
import xbmcaddon
from xbmcvfs import translatePath

from bs4 import BeautifulSoup
from urllib.parse import quote
import requests
import random
import json
import time

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def play_hokejka_stream(link):
    cookies = get_cookies()
    r = requests.get('https://www.hokej.cz' + link, cookies = cookies)
    for row in r.text.split('\n'):
        if '//videoID' in row:
            id = row.strip().replace("video: '","").replace("', //videoID","")
            r = requests.get('https://play.elh.livebox.cz/js/vod-dev.js?__tok' + str(random.randrange(100000000, 999999999)) + '__=' + str(random.randrange(100000000, 999999999)))
            for row in r.text.split('\n'):
                if 'my.token = ' in row:
                    auth = row.strip().replace("my.token = '","").replace("';","")
                    url = 'https://n3.tmo.livebox.cz/elh-vod/_definst_/' + id + '.smil/playlist.m3u8?auth=' + quote(auth)
            list_item = xbmcgui.ListItem(path = url)
            xbmcplugin.setResolvedUrl(_handle, True, list_item)    
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_hokejka_streams(label, link):
    xbmcplugin.setPluginCategory(_handle, label)
    soup = load_page('https://www.hokej.cz' + link)
    items = soup.find_all('li', {'class' : 'menu-item'})
    for item in items:
        if item.find('a').get('href') is not None and link in item.find('a').get('href'):
            submenus = item.find_all('a', {'class' : 'submenu-link'})
            for submenu in submenus:
                if submenu.get('href') != link:
                    text = submenu.text
                    submenu_link = submenu.get('href') 
                    list_item = xbmcgui.ListItem(label = text)
                    url = get_url(action = 'list_hokejka_streams', link = submenu_link, label = text)
                    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        
    load = True
    cnt = 0
    links = []
    while load == True and cnt < 5:
        videos = soup.find_all('article', {'class' : 'video'})
        for video in videos:
            stream = video.find('h3', {'class' : 'video-title'})
            if stream is not None:
                img = video.find('img').get('src')
                a = stream.find('a')
                link = a.get('href')
                if link not in links:
                    list_item = xbmcgui.ListItem(label = a.text)
                    links.append(link)
                    url = get_url(action = 'play_hokejka_stream', link = link, label = a.text)
                    list_item.setArt({'icon': img})
                    list_item.setContentLookup(False)          
                    list_item.setProperty('IsPlayable', 'true')        
                    xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        nexts = soup.find_all('a', {'class' : 'js-load-content'})
        load = False
        for next in nexts:
            soup = load_page('https://www.hokej.cz' + next.get('href'))
            load = True
            cnt = cnt + 1
    nexts = soup.find_all('a', {'class' : 'js-load-content'})
    for next in nexts:
        list_item = xbmcgui.ListItem(label = 'Další')
        url = get_url(action = 'list_hokejka_menu', link = next.get('href'), label = label)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)    

def list_hokejka_main(label):
    xbmcplugin.setPluginCategory(_handle, label)
    soup = load_page('https://www.hokej.cz/tv/hokejka')
    items = soup.find_all('a', {'class' : 'widget-menu-link'})
    for item in items:
        if 'widget-menu-link-ext' not in item.get('class'):
            text = item.text
            link = item.get('href') 
            list_item = xbmcgui.ListItem(label = text)
            url = get_url(action = 'list_hokejka_streams', link = link, label = text)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def load_page(url):
    cookies = get_cookies()
    r = requests.get(url , cookies = cookies, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def get_cookies():
    addon = xbmcaddon.Addon()
    if len(addon.getSetting('hokejka_username')) > 0:
        return load_session()
    else:
        return None

def login():
    addon = xbmcaddon.Addon()
    session = requests.Session()
    post = 'username=' + addon.getSetting('hokejka_username') + '&password=' + addon.getSetting('hokejka_password') + '&do=login-form-submit&send=Odeslat&'
    req = session.post('https://www.hokej.cz/tv/hokejka?restore=true', data = post, headers = {'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With' : 'XMLHttpRequest'})
    if req.status_code not in [200] or 'redirect' not in str(req.content):
        xbmcgui.Dialog().notification('Hokejka TV', 'Chyba při přihlášení', xbmcgui.NOTIFICATION_ERROR, 5000)
        sys.exit() 
    cookies = session.cookies.get_dict()
    save_session(cookies)
    return cookies
   
def load_session():
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'hokejka_session.txt')
    data = None
    try:
        with open(filename, "r") as f:
            for row in f:
                data = row[:-1]
    except IOError as error:
        if error.errno != 2:
            xbmcgui.Dialog().notification('Hokejka TV', 'Chyba  při načtení session', xbmcgui.NOTIFICATION_ERROR, 5000)
    if data is not None:
        data = json.loads(data)
        cookies = data['cookies']
        expires = int(data['expires'])
        if expires < int(time.time()):
            return login()
        else:
            return cookies
    else:
        return login()

def save_session(cookies):
    data = json.dumps({'cookies' : cookies, 'expires' : int(time.time()) + 7200})
    addon = xbmcaddon.Addon()
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    filename = os.path.join(addon_userdata_dir, 'hokejka_session.txt')
    try:
        with open(filename, "w") as f:
            f.write('%s\n' % data)
    except IOError:
        xbmcgui.Dialog().notification('Hokejka TV', 'Chyba při uložení session', xbmcgui.NOTIFICATION_ERROR, 5000)    

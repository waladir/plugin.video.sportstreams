import sys 

import xbmcgui
import xbmcplugin

import requests
from bs4 import BeautifulSoup

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def list_sporttotalcz_submenu(link, label):
    xbmcplugin.setPluginCategory(_handle, label)    
    soup = load_page(link)
    items = soup.find_all('a', {'class' : 'qb'})
    for item in items:
        if item.get('href') is not None:
            print(item.get('href'))
            print(item.find('span', {'class' : 'gi'}).text)
            print(item.find('span', {'class' : 'fb'}).text)


def list_sporttotalcz_main(label):
    soup = load_page('https://sporttotal.cz/')
    menu_items = {}
    menu = soup.find_all('a', {'class' : 'cb_'})
    for item in menu:
        menu_items.update({item.get('href') : item.find('span').text})
    menu = soup.find_all('a', {'class' : 'eb_'})
    for item in menu:
        menu_items.update({item.get('href') : item.find('span').text})

    for menu_item in menu_items:
        list_item = xbmcgui.ListItem(label = menu_items[menu_item])
        url = get_url(action='list_sporttotalcz_submenu', link = 'https://sporttotal.cz' + menu_item, label = menu_items[menu_item])  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)


    # r = requests.get('https://sporttotal.cz/…f7a' , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'})
    # soup = str(r.content)
    # idx = soup.find('index.m3u8')
    # idx_rev = soup.rfind('"', 0, idx)
    # stream = soup[idx_rev+1:idx + len('index.m3u8')]

def load_page(url):
    r = requests.get(url , headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0', 'Accept-Language' : 'cs'})
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup
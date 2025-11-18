# -*- coding: utf-8 -*-
import sys
import os
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.parse import parse_qsl
from datetime import datetime

from libs.utils import get_url
from libs.ct4sportplus import list_ct4sportplus_main, play_ct4sportplus_stream, get_ct4sportplus_live_streams
from libs.tvcomcz import list_tvcomcz_main, list_tvcomcz_submenu, list_tvcomcz_today, play_tvcomcz_stream, list_tvcomcz_league, list_tvcomcz_leagues, list_bl_SportTypes, list_bl_SportLeagues, change_blacklist, change_mainlist, get_tvcomcz_live_streams
from libs.hustetv import list_hustetv_main, list_hustetv_live, list_hustetv_archiv, list_hustetv_submenu, list_hustetv_items, play_hustetv_video, play_hustetv_live_video, get_hustetv_live_streams
from libs.volejtv import list_volejtv_main, list_volejtv_category, play_volejtv_stream, list_volejtv_live, play_volejtv_live_stream, get_volejtv_live_streams
from libs.pingpongtv import list_pingpongtv_main, list_pingpongtv_filter_items, list_pingpongtv_streams, play_pingpongtv_video
from libs.ettutv import list_ettutv_main, list_ettutv_categories, list_ettutv_filter, play_ettutv_stream, get_ettutv_live_streams, list_ettutv_schedule
from libs.nikesk import list_nikesk_main, list_nikesk_category, list_nikesk_tournament, play_nikesk_stream, list_nikesk_live, get_nikesk_live_streams
from libs.tipossk import list_tipossk_main, list_tipossk_live, list_tipossk_archiv, play_tipossk_stream, get_tipossk_live_streams
from libs.hokejka import list_hokejka_main, list_hokejka_streams, play_hokejka_stream

_url = sys.argv[0]
if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

addon = xbmcaddon.Addon()

def list_settings(label):
    xbmcplugin.setPluginCategory(_handle, label)
    if addon.getSetting('tvcom.cz') == 'true':
        list_item = xbmcgui.ListItem(label = 'Výběr sportů a soutěží (TVcom.cz)')
        url = get_url(action='list_bl_SportTypes', label = label + ' \\ '  + 'Výběr sportů a soutěží')  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label='Nastavení doplňku')
    url = get_url(action='addon_settings', label = 'Nastavení doplňku')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    
    xbmcplugin.endOfDirectory(_handle)    

def list_live_streams(label):
    xbmcplugin.setPluginCategory(_handle, label)
    streams = []
    if addon.getSetting('ct4sportplus') == 'true':
        streams = streams + get_ct4sportplus_live_streams()
    if addon.getSetting('tvcom.cz') == 'true':
        streams = streams + get_tvcomcz_live_streams()
    if addon.getSetting('huste.tv') == 'true':
        streams = streams + get_hustetv_live_streams()
    if addon.getSetting('volej.tv') == 'true':
        streams = streams + get_volejtv_live_streams()
    if addon.getSetting('tipos.sk') == 'true':
        streams = streams + get_tipossk_live_streams()

    streams  = sorted(streams, key=lambda d: d['startts']) 
    for stream in streams:
        if stream['startts'] > 0:
            if stream['endts'] is not None:
                cas = datetime.strftime(datetime.fromtimestamp(stream['startts']), '%H:%M') + ' - '  + datetime.strftime(datetime.fromtimestamp(stream['endts']), '%H:%M')
            else:
                cas = datetime.strftime(datetime.fromtimestamp(stream['startts']), '%H:%M')
        else:
            cas = 'LIVE'
        if stream['type'] == 'live':
            if stream['playable'] == 1:
                list_item = xbmcgui.ListItem(label = stream['title'] + ' (' + cas + ')')
                list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title']}) 
                list_item.setArt({'icon': stream['image']})
                if stream['service'] == 'ct4sportplus':
                    url = get_url(action = 'play_ct4sportplus_stream', url = stream['link']) 
                elif  stream['service'] == 'tvcom.cz':
                    url = get_url(action = 'play_tvcomcz_stream', url = stream['link']) 
                elif  stream['service'] == 'huste.tv':
                    url = get_url(action = 'play_hustetv_live_video', link = stream['link'], label = stream['title']) 
                elif stream['service'] == 'volej.tv':
                    url = get_url(action = 'play_volejtv_live_stream', id = stream['link'], label = stream['title']) 
                elif stream['service'] == 'tipos.sk':
                    url = get_url(action = 'play_tipossk_stream', url = stream['link']) 
                list_item.setContentLookup(False)          
                list_item.setProperty('IsPlayable', 'true')        
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
            else:
                list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] + ' (' + cas + ')' +  '[/COLOR]')
                list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title']}) 
                list_item.setArt({'icon': stream['image']})
                url = get_url(action = 'list_live_streams', label = label) 
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)    
    for stream in streams:
        if stream['startts'] > 0:
            if stream['cas'] is not None:
                cas = stream['cas']
            else:
                if stream['endts'] is not None:
                    cas = datetime.strftime(datetime.fromtimestamp(stream['startts']), '%H:%M') + ' - '  + datetime.strftime(datetime.fromtimestamp(stream['endts']), '%H:%M')
                else:
                    cas = ''
        else:
            cas = 'LIVE'
        if stream['type'] == 'future':
            if stream['playable'] == 1:
                list_item = xbmcgui.ListItem(label = stream['title'] + ' (' + cas + ')')
                list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title']}) 
                list_item.setArt({'icon': stream['image']})
                if stream['service'] == 'ct4sportplus':
                    url = get_url(action = 'play_ct4sportplus_stream', url = stream['link']) 
                elif stream['service'] == 'tvcom.cz':
                    url = get_url(action = 'play_tvcomcz_stream', url = stream['link']) 
                elif stream['service'] == 'huste.tv':
                    url = get_url(action = 'play_hustetv_live_video', link = stream['link'], label = stream['title']) 
                elif stream['service'] == 'volej.tv':
                    url = get_url(action = 'play_volejtv_live_stream', id = stream['link'], label = stream['title']) 
                list_item.setContentLookup(False)          
                list_item.setProperty('IsPlayable', 'true')        
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
            else:
                if cas != '':
                    list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] + ' (' + cas + ')' + '[/COLOR]')
                else:
                    list_item = xbmcgui.ListItem(label = '[COLOR=gray]' + stream['title'] + '[/COLOR]')
                list_item.setInfo('video', {'title' : stream['title'], 'plot' : stream['title']}) 
                list_item.setArt({'icon': stream['image']})
                url = get_url(action = 'list_live_streams', label = label) 
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)    
    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def list_menu():
    icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')

    list_item = xbmcgui.ListItem(label = 'Live a plánované streamy')
    url = get_url(action='list_live_streams', label = 'Live')  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    

    if addon.getSetting('ct4sportplus') == 'true':
        list_item = xbmcgui.ListItem(label = 'ČT4 Sport Plus')
        url = get_url(action='list_ct4sportplus_main', label = 'ČT4 Sport Plus')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'ct4sportplus.png'), 'icon' : os.path.join(icons_dir , 'ct4sportplus.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if addon.getSetting('hokejka') == 'true':
        list_item = xbmcgui.ListItem(label = 'Hokejka TV')
        url = get_url(action='list_hokejka_main', label = 'Hokejka TV')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'hokejka.jpg'), 'icon' : os.path.join(icons_dir , 'hokejka.jpg') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if addon.getSetting('tvcom.cz') == 'true':
        list_item = xbmcgui.ListItem(label = 'TVcom.cz')
        url = get_url(action='list_tvcomcz_main', label = 'TVcom.cz')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'tvcomcz.png'), 'icon' : os.path.join(icons_dir , 'tvcomcz.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if addon.getSetting('huste.tv') == 'true':
        list_item = xbmcgui.ListItem(label = 'Huste.tv')
        url = get_url(action='list_hustetv_main', label = 'Huste.tv')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'hustetv.png'), 'icon' : os.path.join(icons_dir , 'hustetv.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if addon.getSetting('volej.tv') == 'true':
        list_item = xbmcgui.ListItem(label = 'Volej.tv')
        url = get_url(action='list_volejtv_main', label = 'Volej.tv')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'volejtv.png'), 'icon' : os.path.join(icons_dir , 'volejtv.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if addon.getSetting('ping-pong.tv') == 'true':
        list_item = xbmcgui.ListItem(label = 'Ping-pong.tv')
        url = get_url(action='list_pingpongtv_main', label = 'Ping-pong.tv')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'pingpongtv.png'), 'icon' : os.path.join(icons_dir , 'pingpongtv.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    if addon.getSetting('tipos.sk') == 'true':
        list_item = xbmcgui.ListItem(label = 'Tipos.sk')
        url = get_url(action='list_tipossk_main', label = 'Tipos.sk')  
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'tipossk.png'), 'icon' : os.path.join(icons_dir , 'tipossk.png') })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    if addon.getSetting('hide_settings') != 'true':
        list_item = xbmcgui.ListItem(label = 'Nastavení')
        list_item.setArt({ 'thumb' : os.path.join(icons_dir , 'settings.png'), 'icon' : os.path.join(icons_dir , 'settings.png') })    
        url = get_url(action='list_settings', label = 'Nastavení')  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'list_live_streams':
            list_live_streams(params['label'])
            
        elif params['action'] == 'list_ct4sportplus_main':
            list_ct4sportplus_main(params['label'])
        elif params['action'] == 'play_ct4sportplus_stream':
            play_ct4sportplus_stream(params['url'])

        elif params['action'] == 'list_tvcomcz_main':
           list_tvcomcz_main(params['label'])
        elif params['action'] == 'list_tvcomcz_submenu':
            list_tvcomcz_submenu(params['SportTypeId'], params['label'])
        elif params['action'] == 'list_today':
            list_tvcomcz_today(params['label'])
        elif params['action'] == 'play_tvcomcz_stream':
            play_tvcomcz_stream(params['url'])
        elif params['action'] == 'list_tvcomcz_leagues':
            list_tvcomcz_leagues(params['SportTypeId'], params['label'])
        elif params['action'] == 'list_tvcomcz_league':
            list_tvcomcz_league(params['SportTypeId'], params['SportLeagueId'], params['label'])            
        elif params['action'] == 'list_bl_SportTypes':
            list_bl_SportTypes(params['label'])
        elif params['action'] == 'list_bl_SportLeagues':
            list_bl_SportLeagues(params['SportTypeId'], params['label'])
        elif params['action'] == 'change_blacklist':
            if 'SportTypeId' in params:
                if 'SportLeagueId' in params and int(params['SportLeagueId']) == -999:
                    change_blacklist(int(params['toggle']), int(params['SportTypeId']), int(params['SportLeagueId']))
                else:
                    change_blacklist(int(params['toggle']),int(params['SportTypeId']), None)
            else:
                change_blacklist(int(params['toggle']), None, int(params['SportLeagueId']))
        elif params['action'] == 'change_mainlist':
            change_mainlist(int(params['toggle']),int(params['SportTypeId']))

        elif params['action'] == 'list_hustetv_main':
           list_hustetv_main(params['label'])
        elif params['action'] == 'list_hustetv_live':
            list_hustetv_live(params['label'])
        elif params['action'] == 'list_hustetv_archiv':
            list_hustetv_archiv(params['link'], params['label'])
        elif params['action'] == 'list_hustetv_submenu':
            list_hustetv_submenu(params['link'], params['label'])
        elif params['action'] == 'list_hustetv_items':
            list_hustetv_items(params['link'], params['label'])
        elif params['action'] == 'play_hustetv_video':
            play_hustetv_video(params['link'], params['label'])
        elif params['action'] == 'play_hustetv_live_video':
            play_hustetv_live_video(params['link'], params['label'])

        elif params['action'] == 'list_volejtv_main':
            list_volejtv_main(params['label'])
        elif params['action'] == 'list_volejtv_category':
            list_volejtv_category(params['label'], params['category_id'], params['page'])
        elif params['action'] == 'play_volejtv_stream':
            play_volejtv_stream(params['id'])
        elif params['action'] == 'play_volejtv_live_stream':
            play_volejtv_live_stream(params['id'])
        elif params['action'] == 'list_volejtv_live':
            list_volejtv_live(params['label'])            

        elif params['action'] == 'list_pingpongtv_main':
            list_pingpongtv_main(params['label'])
        elif params['action'] == 'list_pingpongtv_filter_items':
            list_pingpongtv_filter_items(params['label'], params['select_filter'])
        elif params['action'] == 'list_pingpongtv_streams':
            list_pingpongtv_streams(params['label'], params['select_filter'], params['value'])
        elif params['action'] == 'play_pingpongtv_video':
            play_pingpongtv_video(params['link'])            

        elif params['action'] == 'list_ettutv_main':
            list_ettutv_main(params['label'])
        elif params['action'] == 'list_ettutv_categories':
            list_ettutv_categories(params['label'], params['category_filter'], params['is_category'])
        elif params['action'] == 'list_ettutv_filter':
            list_ettutv_filter(params['label'], params['id'], params['cat_id'], params['page'])
        elif params['action'] == 'list_ettutv_schedule':
            list_ettutv_schedule(params['label'])
        elif params['action'] == 'play_ettutv_stream':
            play_ettutv_stream(params['id'])

        elif params['action'] == 'list_nikesk_main':
            list_nikesk_main(params['label'])
        elif params['action'] == 'list_nikesk_live':
            list_nikesk_live(params['label'])            
        elif params['action'] == 'list_nikesk_category':
            list_nikesk_category(params['label'], params['category'])            
        elif params['action'] == 'list_nikesk_tournament':
            list_nikesk_tournament(params['label'], params['category'], params['tournament'])            
        elif params['action'] == 'play_nikesk_stream':
            play_nikesk_stream(params['id'], params['type'])

        elif params['action'] == 'list_tipossk_main':
            list_tipossk_main(params['label'])
        elif params['action'] == 'list_tipossk_live':
            list_tipossk_live(params['label'])            
        elif params['action'] == 'list_tipossk_archiv':
            list_tipossk_archiv(params['label'])    
        elif params['action'] == 'play_tipossk_stream':
            play_tipossk_stream(params['url'])

        elif params['action'] == 'list_hokejka_main':
            list_hokejka_main(params['label'])
        elif params['action'] == 'list_hokejka_streams':
            list_hokejka_streams(params['label'], params['link'])
        elif params['action'] == 'play_hokejka_stream':
            play_hokejka_stream(params['link'])

        elif params['action'] == 'list_settings':
            list_settings(params['label'])
        elif params['action'] == 'addon_settings':
            xbmcaddon.Addon().openSettings()
        else:
            raise ValueError('Neznámý parametr: {0}!'.format(paramstring))
    else:
         list_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])

addon = None
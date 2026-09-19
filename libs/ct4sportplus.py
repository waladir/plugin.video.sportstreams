# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from urllib.error import HTTPError

import json
from datetime import date,datetime,timedelta
import time

from libs.utils import get_url

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'
graphql_url = 'https://api.ceskatelevize.cz/graphql/'
params = {'client' : 'iVysilaniWeb', 'version' : '1.131.1', 'use-new-playability' : True}

GRAPHQL = { 
            'TvProgramDailyTablet' : "query TvProgramDailyTablet($channels: [String!]!, $date: Date!) {\n  TVProgramDailyChannelsPlanV2(channels: $channels, date: $date) {\n    __typename\n    channel\n    currentBroadcast {\n      __typename\n      item {\n        __typename\n        ...CommonTvProgramFragment\n      }\n    }\n    encoder\n    program {\n      __typename\n      ...CommonTvProgramFragment\n    }\n  }\n  liveBroadcastFind(type: all) {\n    __typename\n    current {\n      __typename\n      channelAsString\n      cardLabels {\n        __typename\n        ...CardLabelFragment\n      }\n      encoder\n      previewImage\n    }\n  }\n}\nfragment CommonTvProgramFragment on DailyChannelPlan {\n  __typename\n  idec\n  sidp\n  startTime\n  title\n  show\n  episodeTitle\n  part\n  description\n  imageUrl\n  length\n  ivysilani\n  programSource\n  isPlayableNow\n  playableFrom\n  liveOnly\n  start\n  end\n}\nfragment CardLabelFragment on CardLabels {\n  __typename\n  topLeft\n  topRight\n  center\n  bottomLeft\n  bottomRight\n}"
          }

def call_graphql(operationName, variables):
    post = {'operationName' : operationName, 'variables' : variables, 'query': GRAPHQL[operationName].replace('\t', '').replace('\n', ' ')}
    data = call_api(url = graphql_url, data = post, method = 'POST')
    if 'data' not in data or data['data'] is None:
        return None
    for result in data['data']:
        return data['data'][result]
    return None

def call_api(url, data = None, method = None):
    import requests
    addon = xbmcaddon.Addon()
    headers = {'User-Agent': ua, 'Accept-language' : 'cs', 'Accept-Encoding' : 'gzip', 'Accept': 'application/json; charset=utf-8', 'Content-type' : 'application/json;charset=UTF-8'}
    if addon.getSetting('log_api_calls') == 'true':
        xbmc.log(url)
    if method == 'POST':
        request = requests.post(url = url, params = params, json = data, headers = headers )
    else:
        request = requests.get(url = url, params = params, headers = headers )
    try:
        response = request.content
        if addon.getSetting('log_api_calls') == 'true':
            xbmc.log(str(response))
        if response and len(response) > 0:
            data = json.loads(response)
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
    day = date.today()
    tz_offset = int(time.mktime(datetime.now().timetuple())-time.mktime(datetime.utcnow().timetuple()))
    for channel in ['ctSportExtra']:
        data = call_graphql(operationName = 'TvProgramDailyTablet', variables = {'channels' : channel, 'date' : day.strftime('%m.%d.%Y')})
        for channel_program in data:
            for item in channel_program['program']:
                startts = time.mktime(time.strptime(item['start'][:-5], '%Y-%m-%dT%H:%M:%S')) + tz_offset
                endts = time.mktime(time.strptime(item['end'][:-5], '%Y-%m-%dT%H:%M:%S')) + tz_offset
                if endts>time.time():
                    title = item['title']
                    img = item['imageUrl']
                    start = datetime.fromtimestamp(startts)
                    end = datetime.fromtimestamp(endts)
                    cas = start.strftime('%H:%M') + ' - ' + end.strftime('%H:%M')
                    print(item)
                    print(item['playableFrom'])
                    print(channel_program['encoder'])
                    if 'playableFrom' in item and len(str(item['playableFrom'])) > 0 and time.mktime(time.strptime(item['start'][:-5], '%Y-%m-%dT%H:%M:%S')) + tz_offset > time.time():
                        item['isPlayableNow'] = False
                    if  'isPlayableNow' not in item and startts<time.time():
                        item['isPlayableNow'] = True
                    if 'idec' in item and item['idec'] is not None and 'isPlayableNow' in item and item['isPlayableNow'] == True:
                        data = call_api(url = 'https://api.ceskatelevize.cz/video/v1/playlist-live/v1/stream-data/channel/'+ str(channel_program['encoder']) + '?canPlayDrm=false&streamType=dash&quality=web&maxQualityCount=5', data = None)
                        if 'streamUrls' in data and 'main' in data['streamUrls']:
                            url = data['streamUrls']['main']
                            live_streams.append({ 'service' : 'ct4sportplus', 'type' : 'live', 'link' : url, 'playable' : 1, 'cas' : title, 'startts' : startts, 'endts' : endts, 'title' : item['title'], 'image' : item['imageUrl']})
                    else:
                        live_streams.append({ 'service' : 'ct4sportplus', 'type' : 'future', 'link' : None, 'playable' : 0, 'cas' : cas, 'startts' : startts, 'endts' : endts, 'title' : title, 'image' : img})

    live_streams = sorted(live_streams, key=lambda d: d['startts'])
    return live_streams
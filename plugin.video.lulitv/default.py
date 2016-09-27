# -*- coding: utf-8 -*-
import luli,plugintools,urllib,xbmcplugin,xbmc,xbmcgui

def get_shows():
    url = 'http://luli.tv/Items.aspx?pageId=1'
    showsList = luli.get_page(url)
    for show in showsList:
        plugintools.add_item(title=show.get('title'),action='showepisodes',url=show.get('url'),thumbnail=show.get('image'))
    plugintools.close_item_list()
    
def get_episodes(url):
    epsList = luli.get_page(url)
    for episode in epsList:
        plugintools.add_item(title=episode.get('title'),action='stream',url=episode.get('url'),thumbnail=episode.get('image'))
    plugintools.close_item_list()

def stream(url,title,thumbnail):
    path=luli.getEpisode(url)
    li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail,path=path)
    li.setInfo(type='Video', infoLabels={ "Title": str(title) })
    xbmc.Player().play(path,li)
    
def run():
    params = plugintools.get_params()
    action = params.get('action')
    if action == None:
        get_shows()
    elif action == 'showlist':
        get_shows()
    elif action == 'showepisodes':
        get_episodes(params.get('url'))
    elif action == 'stream':
        stream(urllib.unquote_plus(params.get('url')),params.get('title'),params.get('image'))
    
run()
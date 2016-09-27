# -*- coding: utf-8 -*-
import kidstv,plugintools,urllib,xbmcplugin

def playF4mLink(url,name,proxy=None,use_proxy_for_chunks=False,auth_string=None,streamtype='HDS',setResolved=False):
    from F4mProxy import f4mProxyHelper
    player=f4mProxyHelper()
    player.playF4mLink(url,name)

def get_shows(page='1'):
    showsList = kidstv.get_shows_menu(page)
    for show in showsList.get('shows'):
        plugintools.add_item(title=show.get('title'),action='showepisodes',page='1',mmsId=show.get('mmsId'),thumbnail=show.get('image'))
    if showsList.get('next'):
        plugintools.add_item(title=u'הבא',page=str(int(page)+1),action='showlist')
    plugintools.close_item_list()
    
def get_episodes(mmsId,page):
    epsList = kidstv.get_mms_list(mmsId,page)
    for episode in epsList.get('episodes'):
        plugintools.add_item(title=episode.get('title'),action='showstreams',page='1',token=episode.get('token'),thumbnail=episode.get('image'))
    if epsList.get('next'):
        plugintools.add_item(title=u'הבא',page=str(int(page)+1),action='showepisodes',mmsId=mmsId)
    plugintools.close_item_list()

def show_streams(token):
    streams = kidstv.getStreams(token)
    for stream in streams:
        plugintools.add_item(title = stream.get('quality'),folder=False,action='stream',url=stream.get('url'),thumbnail=stream.get('image'))
    plugintools.close_item_list()
    
def run():
    params = plugintools.get_params()
    action = params.get('action')

    if action == None:
        get_shows()
    elif action == 'showlist':
        get_shows(params.get('page'))
    elif action == 'showepisodes':
        get_episodes(params.get('mmsid'),params.get('page'))
    elif action == 'showstreams':
        show_streams(params.get('token'))
    elif action == 'stream':
        playF4mLink(urllib.unquote_plus(params.get('url')),urllib.unquote_plus(params.get('title')))

run()
        
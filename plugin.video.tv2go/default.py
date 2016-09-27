# -*- coding: utf-8 -*-
import json,urllib2,xbmc,xbmcgui,urllib,livestreamer,plugintools,os,xbmcaddon,pseudo
from __builtin__ import False
from livestreamer.stream.http import HTTPStream
tikva = '&userTimeOffset=-120'
def getAllChannels():
    plugintools.add_item(action='pseudo',title='[COLOR blue] Add to pseudoTV [/COLOR]')
    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'

    request = urllib2.Request(plugintools.get_giti_hubi(2))
    resp = urllib2.urlopen(request)
    result = resp.read()
    json_obj = json.loads(result,encoding='utf-8')
    
    channelList = json_obj.get('channels')
    
    prevChannel = ''
    prevChannelThumbnail = ''

    for channel in channelList:
        if prevChannel == '':
            prevChannelDict = channelList[len(channelList)-1]
            prevChannel = str(prevChannelDict.get('channelID'))
            prevChannelThumbnail = str(prevChannelDict.get('thumbpic'))
        title=channel.get('title').encode('utf-8')
        plugintools.add_item(title=title,thumbnail=channel.get('thumbpic'),channelID=str(channel.get('channelID')),action=channel.get('movType'),prevChannel=prevChannel,prevThumbnail=prevChannelThumbnail)
        prevChannel = str(channel.get('channelID'))
        prevChannelThumbnail = repr(channel.get('thumbpic'))
    
    plugintools.close_item_list()
david = plugintools.get_giti_hubi(1)   

def playStream(channelID,thumbnail="",prevChannel='',firstTime=True):
    if prevChannel=='':
        prevChannel = channelID
    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'

    request = urllib2.Request(david+channelID+tikva)
    resp = urllib2.urlopen(request)
    result = resp.read()
    json_obj = json.loads(result,encoding='utf-8')
    
    movie = json_obj.get('movies')[0]
    startFrom = float(0)
    if movie.get('StreamType') == 'youtube':
        if plugintools.get_setting('youtube_provider')=='1':
            link = "https://www.youtube.com/watch?v="+json_obj.get('movies')[0].get('movId')
            link = YouTubeStreams(link)
        else:
            link = 'plugin://plugin.video.youtube/play/?video_id='+json_obj.get('movies')[0].get('movId')
        title = movie.get('title').encode('utf-8')
        if firstTime:
            startFrom = float(movie.get('startFrom'))
    else:
        link = movie.get('ratesData').get('mainRate')
        title = movie.get('title').encode('utf-8')
        
    #xbmc.Player().play(link)
    player = CustomPlayer()
    player.PlayVideo(link, title, thumbnail,channelID,startFrom,prevChannel)
 

def run():
    plugintools.log("tv2go.run")
    
    # Get params
    params = plugintools.get_params()
    plugintools.log("tv2go.run params="+repr(params))
    action = params.get('action')

    if action == None:
        getAllChannels()
    elif action == 'StreamFromUrl' or action == 'YouTube_Video':
        channelID = params.get('channelid')
        try:
            thumb = urllib.unquote_plus(params.get('thumbnail'))
        except:
            thumb=''
        prev = urllib.unquote_plus(params.get('prevchannel'))
        playStream(channelID,thumb,prev)
    elif action == 'pseudo':
        pseudo.getPseudoChannels()
     
def YouTubeStreams(url):
    source = livestreamer.streams(url) 
    return source['best'].url

class CustomPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.channelID = ''
        self.thumbnail = ''
        self.youtube = False
        self.startFrom = float(0)
        self.prevChannel = ''
        self.win = xbmcgui.Window(10001)

    def PlayVideo(self,link,title, thumbnail="",channelID='',startFrom=float(0),prevChannel='', mediaType='Video') :
        """Plays a video
       
        Arguments:
        title: the title to be displayed
        thumbnail: the thumnail to be used as an icon and thumbnail
        link: the link to the media to be played
        mediaType: the type of media to play, defaults to Video. Known values are Video, Pictures, Music and Programs
        """
        self.win.setProperty('channelIDTV2GO', str(channelID))
        self.win.setProperty('thumbnailTV2GO', str(thumbnail))
        self.win.setProperty('prevChannelTV2GO', str(prevChannel))

        if 'youtube' in link:
            self.youtube = True
            self.win.setProperty('youtubeTV2GO', 'True')
            self.win.setProperty('startFromTV2GO', str(startFrom))
            self.startFrom = startFrom
        else: 
            self.youtube=False
            self.win.setProperty('youtubeTV2GO', 'False')
        
        li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail, path=link)
        li.setInfo(type=mediaType, infoLabels={ "Title": str(title) })

        self.play(link,li)


run()


# -*- coding: utf-8 -*-
import xbmc,xbmcaddon,os,plugintools,xbmcgui,pseudo,datetime,repoCheck
        
def notify(header=None, msg='', duration=2000):
    ADDON = xbmcaddon.Addon(id='plugin.video.tv2go')
    ICON_PATH = os.path.join( plugintools.get_runtime_path(), 'icon.png' )
    if header is None: header = ADDON.get_name()
    builtin = "XBMC.Notification(%s,%s, %s, %s)" % (header, msg, duration, ICON_PATH)
    xbmc.executebuiltin(builtin)
    
class Service(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, *args, **kwargs)
        self.win = xbmcgui.Window(10001)
    
    def onPlayBackStarted(self):
        print('TV2GO service: Playback Started')
        if self.win.getProperty('youtubeTV2GO') == 'True':
            self.seekTime(float(self.win.getProperty('startFromTV2GO')))
    def onPlayBackStopped(self):
        print('TV2GO service: Playback Stopped')
        self.win.setProperty('youtubeTV2GO', 'False')
    def onPlayBackEnded(self):
        print('TV2GO service: Playback Ended')
        if self.win.getProperty('youtubeTV2GO') == 'True':
            channelID = self.win.getProperty('channelIDTV2GO')
            thumbnail = self.win.getProperty('thumbnailTV2GO')
            prevChannel = self.win.getProperty('prevChannelTV2GO')
            xbmc.Player().play('plugin://plugin.video.tv2go/?action=YouTube_Video&title=&url=&thumbnail='+thumbnail+'&plot=&extra=&channelid='+channelID+'&prevchannel=8&prevthumbnail=&nextchannel=&nextthumbnail=')

notify ('TV2GO','Service started!')
try:
    repoCheck.UpdateRepo()
    repoCheck.fix()
    xbmc.sleep(2000)
    if plugintools.get_setting('pseudo_update')=='true':
        time_file = open( os.path.join( plugintools.get_runtime_path() , "last_update.txt" ) , "r" )
        day_str = time_file.readline()
        diff = datetime.datetime.today().day-int(day_str)
        
        if diff>0:
            notify ('TV2GO','Channels loading started')
            pseudo.getPseudoChannels(False)
        
        time_file.close()
except:
    pass

player = Service()
while not xbmc.abortRequested:
    player.isPlaying()
    xbmc.sleep(1)
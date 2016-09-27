# -*- coding: utf-8 -*-
import json,urllib2,xbmc,xbmcgui,urllib,livestreamer,plugintools,os,xbmcaddon,base64
from __builtin__ import False
from datetime import datetime
tikva = '&userTimeOffset=-120'
menahem = base64.decodestring('Jm1vdlR5cGU9eW91VHViZSZwbGF5ZXJUeXBlPWh0bWxQYyZTa2luSUQ9MCZTa2luVHlwZT0xJlBsYXlMaXN0SUQ9MCZMYW5nSUQ9MSZDbGllbnRJRD0xMzImRmlyc3RUaW1lPWZhbHNlJnVzZXJUaW1lT2Zmc2V0PS0xMjAmZ2VuQ2hhbm5lbEVwZz10cnVlJm1vdlN0YXJ0RGF0ZT11bmRlZmluZWQmcmFuZD0wLjM2ODUyMTMxMDg1NDcwMzImbW92UG9zPTE=')
def getPseudoChannels(dialog=True):
    
    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'

    request = urllib2.Request(plugintools.get_giti_hubi(2))
    resp = urllib2.urlopen(request)
    result = resp.read()
    json_obj = json.loads(result,encoding='utf-8')
    
    channelList = json_obj.get('channels')
    
    prevChannel = ''
    prevChannelThumbnail = ''
    paths = []
    for channel in channelList:
        if prevChannel == '':
            prevChannelDict = channelList[len(channelList)-1]
            prevChannel = str(prevChannelDict.get('channelID'))
            prevChannelThumbnail = str(prevChannelDict.get('thumbpic'))
        title=channel.get('title').encode('utf-8')
        channelNumber = channel.get('channelNumber')
        paths.append({'path':plugintools.get_path(title=title,thumbnail=channel.get('thumbpic'),channelID=str(channel.get('channelID')),action=channel.get('movType'),prevChannel=prevChannel,prevThumbnail=prevChannelThumbnail),'title':title,'channelNumber':channelNumber,'channelID':channel.get('channelID'),'image':channel.get('thumbpic').encode('utf-8')})
        prevChannel = str(channel.get('channelID'))
        prevChannelThumbnail = repr(channel.get('thumbpic'))
    
    ScriptSettings2Create(paths,dialog)
    time_file = open( os.path.join( plugintools.get_runtime_path() , "last_update.txt" ) , "w" )
    todayTime = datetime.today()
    cooltime = str(todayTime.day)
    time_file.write(cooltime)   
    time_file.close()
    
david = plugintools.get_giti_hubi(1)       
def notify(header=None, msg='', duration=2000):
    ADDON = xbmcaddon.Addon(id='plugin.video.tv2go')
    ICON_PATH = os.path.join( plugintools.get_runtime_path(), 'icon.png' )
    if header is None: header = ADDON.get_name()
    builtin = "XBMC.Notification(%s,%s, %s, %s)" % (header, msg, duration, ICON_PATH)
    xbmc.executebuiltin(builtin)
    
def get_pseudo_path():
    dev = {}
    __settings__ = xbmcaddon.Addon(id='script.pseudotv.live')
    dev['main'] = xbmc.translatePath( __settings__.getAddonInfo('Profile') )
    dev['xmltv'] = __settings__.getSetting( 'xmltvLOC' )
    # Parche para XBMC4XBOX
    if not os.path.exists(dev['main']):
        os.makedirs(dev['main'],0777)
    if not os.path.exists(dev['xmltv']):
        try:
            os.makedirs(dev['xmltv'],0777)
        except:
            __settings__.setSetting('xmltvLOC', dev['main'])
            dev['xmltv'] = dev['main']

    return dev

def ScriptSettings2Create(paths,dialog_show):
    if dialog_show:
        dialog = xbmcgui.DialogProgress()
        dialog.create(u'TV2GO', u'טוען ערוצים')
        dialog.update(0)
        total = len(paths)
    
    
    DOWNLOAD_PATH = get_pseudo_path()['main']
    setting_file = open( os.path.join( DOWNLOAD_PATH , "settings2.xml" ) , "w" )
    setting_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    setting_file.write('<settings>\n')
    
    for path in paths:
        channelNumber = path.get('channelNumber')
        if dialog_show:
            percent = int((int(channelNumber)*100/total))
            dialog.update(percent)
        setting_file.write('<setting id="Channel_%s_type" value="8" />\n'%(str(channelNumber)))
        setting_file.write('<setting id="Channel_%s_1" value="%s" />\n'%(str(channelNumber),str(path.get('channelNumber'))))
        setting_file.write('<setting id="Channel_%s_2" value="plugin://plugin.video.tv2go/%s"/>\n'%(str(channelNumber),path.get('path')))
        setting_file.write('<setting id="Channel_%s_3" value="xmltv" />\n'%(str(channelNumber)))
        setting_file.write('<setting id="Channel_%s_4" value="Plugin - TV2GO" />\n'%(str(channelNumber)))
        setting_file.write('<setting id="Channel_%s_rulecount" value="1" />\n'%(str(channelNumber)))
        setting_file.write('<setting id="Channel_%s_rule_1_id" value="1" />\n'%(str(channelNumber)))
        setting_file.write('<setting id="Channel_%s_rule_1_opt_1" value="%s" />\n'%(str(channelNumber),path.get('title')))
        setting_file.write('<setting id="Channel_%s_changed" value="False" />\n'%(str(channelNumber)))
        
    setting_file.write('<settings>')
    generateGuide(paths,dialog_show)
    if dialog_show:
        dialog.close()
    notify('TV2GO', 'Channels loaded!')
    setting_file.close()

def generateGuide(paths,dialog_show):
    import datetime
    if dialog_show:
        dialog = xbmcgui.DialogProgress()
        dialog.create(u'TV2GO', u'EPG מכין')
        dialog.update(0)
        total = len(paths)
    
    DOWNLOAD_PATH = get_pseudo_path()['xmltv']
    setting_file = open( os.path.join( DOWNLOAD_PATH , "xmltv.xml" ) , "w" )
    setting_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
    setting_file.write('<tv>\n')
    count =0
    percent = 0
    for path in paths:
        if dialog_show:
            percent = int((int(count)*100/total))
            dialog.update(percent)
        episoides = getInfo(path.get('channelID'))
        setting_file.write('<channel id="%s">\n'%(str(path.get('channelNumber'))))
        setting_file.write('    <display-name>%s</display-name>\n'%(path.get('title')))
        setting_file.write('    <icon src="%s" />\n'%(path.get('image')))
        setting_file.write('</channel>\n\n')
        for eps in episoides:
            if 'startTime' in eps.keys():
                startTimeL = eps['startTime'].split(' ')
                dayDate = startTimeL[0].split('/')
                startTime = startTimeL[1].split(':')
                startTimeF = dayDate[2]+dayDate[1]+dayDate[0]+startTime[0]+startTime[1]+startTime[2]+' +0200'
                try:
                    endTimeL = eps['endTime'].split(' ')
                    dayDate = endTimeL[0].split('/')
                    endTime = endTimeL[1].split(':')
                    endTimeF = dayDate[2]+dayDate[1]+dayDate[0]+endTime[0]+endTime[1]+endTime[2]+' +0200'
                except:
                    endTimeF = startTimeF
                name = eps.get('programName').encode('utf-8')
                desc = eps.get('programDescription').encode('utf-8')
                setting_file.write('<programme channel="%s" start="%s" stop="%s">\n'%(str(path.get('channelNumber')),startTimeF,endTimeF))
                setting_file.write('<title>%s</title>\n'%(name.replace('&','')))
                setting_file.write('<desc>%s</desc>\n'%(desc.replace('&','')))
                setting_file.write('</programme>\n')
        count = count+1
    setting_file.write('\n</tv>')
    setting_file.close()
    if dialog_show:
        dialog.close()
    else:
        notify ('TV2GO','Channels updated!')

def getInfo(channelID):
    channelID = str(channelID)

    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'

    request = urllib2.Request(david+channelID+menahem)
    resp = urllib2.urlopen(request)
    result = resp.read()
    json_obj = json.loads(result,encoding='utf-8')
    epgDay = json_obj['epgDay']
    if epgDay != 'empty':
        try:
            json_obj = json_obj['epgDay']['channelsList'][channelID]['programsList']
            return json_obj
        except:
            return [] 
    else:
        return []
    
# -*- coding: utf-8 -*-
import requests,re,xbmcaddon,os,xbmc,urllib,urllib2,plugintools,xbmcgui
from bs4 import BeautifulSoup

headers = {}
headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'
    
def getLink(url):
    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'
    request = urllib2.Request(url,headers=headers)
    resp = urllib2.urlopen(request)
    result = resp.read()
    try:
        soup = BeautifulSoup(result, "html.parser")
    except:
        soup = BeautifulSoup(result)
    src  = soup.find('iframe').get('src')
    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'
    request = urllib2.Request(src,headers=headers)
    response = urllib2.urlopen(request)
    try:
        soup = BeautifulSoup(response.read(), "html.parser")
    except:
        soup = BeautifulSoup(response.read())
    url = soup.find('iframe').get('src')
    r = requests.get(url)
    file = re.compile('"url":"(.*)","fid":').findall(str(r.content))[0].replace('\\/','/')
    
    link = 'rtmp://wowzail.video-cdn.com:80/vodcdn playpath='+file+' swfUrl=http://www.video-cdn.com/assets/flowplayer/flowplayer.commercial-3.2.18.swf pageUrl='+url
    playfile = open(plugintools.get_runtime_path()+'\play.m3u' , "w" )
    playfile.write("#EXTINF:-1 ,KaraokeTV \n"+link)
    playfile.close()
    return plugintools.get_runtime_path()+'\play.m3u'

def search(query):
    query = urllib.quote_plus(query)
    request = urllib2.Request('http://www.karaoketv.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9?v='+query,headers=headers)
    response = urllib2.urlopen(request)
    try:
        soup = BeautifulSoup(response.read(), "html.parser")
    except:
        soup = BeautifulSoup(response.read())
    categories = soup.findAll('ul',{'class':'category-list'},'html.parser')
    for cat in categories:
        links = cat.findAll('a')
        for link in links:
            plugintools.add_item(title=link.img.get('alt'),url=link.get('href'),action='stream',thumbnail=link.img.get('src'),folder=False)
    
    try:
        nextUrl = soup.find('li',{'class':'next'}).a.get('href')
        plugintools.add_item(title=u'עמוד הבא',action='page',url=nextUrl.encode('utf-8'))
        print url + 'this is the url'
    except:
        pass
    plugintools.close_item_list()

def show_page(url):
    request = urllib2.Request(url,headers=headers)
    response = urllib2.urlopen(request)
    try:
        soup = BeautifulSoup(response.read(), "html.parser")
    except:
        soup = BeautifulSoup(response.read())
    categories = soup.findAll('ul',{'class':'category-list'},'html.parser')
    for cat in categories:
        links = cat.findAll('a')
        for link in links:
            plugintools.add_item(title=link.img.get('alt'),url=link.get('href'),action='stream',thumbnail=link.img.get('src'),folder=False)
    try:
        nextUrl = soup.find('li',{'class':'next'}).a.get('href')
        plugintools.add_item(title=u'עמוד הבא',action='page',url=nextUrl.encode('utf-8'))
    except:
        pass
    plugintools.close_item_list()
    
def home():
    plugintools.add_item(action='search',title=u'[COLOR blue]חיפוש[/COLOR]',folder=True)
    request = urllib2.Request('http://www.karaoketv.co.il/',headers=headers)
    response = urllib2.urlopen(request)
    try:
        soup = BeautifulSoup(response.read(), "html.parser")
    except:
        soup = BeautifulSoup(response.read())
    categories = soup.findAll('ul',{'class':'col-md-4'},'html.parser')
    for cat in categories:
        for link in cat.findAll('a'):
            plugintools.add_item(title=link.text,url=link.get('href'),action='page')
    plugintools.close_item_list()
def run():
    plugintools.log("tv2go.run")
    
    # Get params
    params = plugintools.get_params()
    plugintools.log("tv2go.run params="+repr(params))
    action = params.get('action')

    if action == None:
        home()
    elif action == 'search':
        searchtext=""
        keyboard = xbmc.Keyboard(searchtext,u"הכנס את שם השיר או הזמר")
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            search(keyboard.getText())
    elif action == 'page':
        show_page(params.get('url'))
    elif action=='stream':
        path = getLink(params.get('url'))
        print path
        title = urllib.unquote_plus(params.get('title'))
        thumbnail = params.get('thumbnail')
        li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail,path=path)
        li.setInfo(type='Video', infoLabels={ "Title": str(title) })
        xbmc.Player().play(path)
        
run()
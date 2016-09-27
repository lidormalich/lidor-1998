# -*- coding: utf-8 -*-
import requests,re,xbmcaddon,os,xbmc,urllib,urllib2,plugintools,xbmcgui
from bs4 import BeautifulSoup



headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'he-IL,he;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'__atuvc=9%7C44; PHPSESSID=77ec658f178b75028f5897f1398c3bd3; resolution=1920,1.25; __utmt=1; __utma=138181546.1832601747.1446334267.1446816725.1446934826.9; __utmb=138181546.1.10.1446934826; __utmc=138181546; __utmz=138181546.1446374103.2.2.utmcsr=facebook.com|utmccn=(referral)|utmcmd=referral|utmcct=/; karaoketv_cookie_currency=ILS',
'Host':'www.karaoketv.co.il',
'Upgrade-Insecure-Requests':'1'}
headers['User-Agent']= 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'

def getLink(url):
    headers = {}
    headers['User-Agent']= 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'

    r = requests.get(url,headers=headers)
    r.encoding = 'utf-8'
    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        soup = BeautifulSoup(r.text)
    src  = soup.find('iframe').get('src')
    r = requests.get(src,headers=headers)
    r.encoding = 'utf-8'
    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        soup = BeautifulSoup(r.text)
    url = soup.find('iframe').get('src')
    r = requests.get(url)
    file = re.compile('"url":"(.*)","fid":').findall(str(r.content))[0].replace('\\/','/')
    
    link = 'rtmp://wowzail.video-cdn.com:80/vodcdn playpath='+file+' swfUrl=http://www.video-cdn.com/assets/flowplayer/flowplayer.commercial-3.2.18.swf pageUrl='+url
    return link

def search(query):
    query = urllib.quote_plus(query)
    print query
    r = requests.get('http://www.karaoketv.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9?v='+query,headers=headers)
    r.encoding = 'utf-8'
    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        soup = BeautifulSoup(r.text)
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

def show_page(url,curpage=1):
    if curpage == None:
        curpage=1
    
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20'
    headers['content-type'] = 'text/html; charset=utf-8'
    request = urllib2.Request(urllib.unquote_plus(url+'/'+str(curpage)),headers=headers)
    resp = urllib2.urlopen(request)
    result = resp.read().decode('utf-8')
    #r.encoding = 'utf-8'
    try:
        soup = BeautifulSoup(result, "html.parser")
    except:
        soup = BeautifulSoup(result)
    categories = soup.findAll('ul',{'class':'category-list'},'html.parser')
#    import io

    #playfile = open(plugintools.get_runtime_path()+'\\foobar.txt' , "w" )
    #playfile.write(r.content)

    for cat in categories:
        links = cat.findAll('a')
        for link in links:
            plugintools.add_item(title=link.img.get('alt'),url=link.get('href'),action='stream',thumbnail=link.img.get('src'),folder=False)
        
    curpage = curpage+1
    plugintools.add_item(title=u'עמוד הבא',action='page',url=url.encode('utf-8'),page=curpage)
    plugintools.close_item_list()
    
def home():
    plugintools.add_item(action='search',title=u'[COLOR blue]חיפוש[/COLOR]',folder=True)
    r = requests.get('http://www.karaoketv.co.il/',headers=headers)
    r.encoding = 'utf-8'
    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        soup = BeautifulSoup(r.text)
    categories = soup.findAll('ul',{'class':'col-md-4'},'html.parser')
    for cat in categories:
        for link in cat.findAll('a'):
            plugintools.add_item(title=link.text,url=link.get('href').encode('utf-8'),action='page')
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
        show_page(params.get('url'),int(params.get('page')))
    elif action=='stream':
        path = getLink(params.get('url'))
        print path
        title = urllib.unquote_plus(params.get('title'))
        thumbnail = params.get('thumbnail')
        li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail,path=path)
        li.setInfo(type='Video', infoLabels={ "Title": str(title) })
        xbmc.Player().play(path,li)
        
run()
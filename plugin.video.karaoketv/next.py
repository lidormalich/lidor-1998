# -*- coding: utf-8 -*-
import requests,re,os,urllib,urllib2
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


def show_page(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
#    try:
    soup = BeautifulSoup(r.text, "html.parser")
    soup.prettify()
    print soup
#     except:
#         soup = BeautifulSoup(r.text)
#    categories = soup.findAll('div',{'class':'row categories'},'html.parser')
#    print categories
#    for cat in categories:
#         links = cat.findAll('a')
#         for link in links:
#             print '11111111111111111111'
#             
#            plugintools.add_item(title=link.img.get('alt'),url=link.get('href'),action='stream',thumbnail=link.img.get('src'),folder=False)
#    try:
#     nextUrl = soup.find('ul',{'class':'pagination'})#.a.get('href')
#     print nextUrl
#        plugintools.add_item(title=u'הבא',action='page',url=nextUrl.encode('utf-8'))
#    except:
#        pass
#    plugintools.close_item_list()
show_page("http://www.karaoketv.co.il/develop/%D7%A7%D7%98%D7%92%D7%95%D7%A8%D7%99%D7%95%D7%AA/cat22/%D7%94%D7%9E%D7%91%D7%95%D7%A7%D7%A9%D7%99%D7%9D_%D7%91%D7%99%D7%95%D7%AA%D7%A8/2")
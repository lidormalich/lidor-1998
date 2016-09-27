# -*- coding: utf-8 -*-
import requests,urllib2
from bs4 import BeautifulSoup
import re,json

def get_page(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text,'html.parser')
    ul = soup.find('ul',{'id':'jCarouselLiteUL'})
    showsList = []
    for link in ul.findAll('a'):
        clearText = re.compile('[^" ""\n""\r"]+', re.UNICODE).findall(link.find('h2').text)
        finalText =' '
        urlLink = link.get('href')
        if 'luli' not in urlLink:
            urlLink ='http://luli.tv/'+urlLink
        showsList.append({'title':finalText.join(clearText),'url':urlLink,'image':'http://luli.tv/'+link.img.get('src')})
    return showsList
    
def getEpisode(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    r = requests.get(soup.find('iframe').get('src'))
    soup = BeautifulSoup(r.text,'html.parser')
    brightcove = soup.find('object',{'class':'BrightcoveExperience'})
    return getVideo(brightcove.find('param',{'name':'@videoPlayer'}).get('value'), brightcove.find('param',{'name':'playerKey'}).get('value'), brightcove.find('param',{'name':'playerID'}).get('value'))

def getVideo(videoPlayer,playerKey,playerID):
        url = 'https://secure.brightcove.com/services/viewer/htmlFederated?&width=859&height=482&flashID=myExperience&bgcolor=%23FFFFFF&playerID='+playerID+'&playerKey='+playerKey+'&isVid=true&isUI=true&dynamicStreaming=true&%40videoPlayer='+videoPlayer+'&secureConnections=true&secureHTMLConnections=true'
        html = requests.get(url)
        a = re.compile('experienceJSON = (.+?)\};').search(html.content).group(1)
        a = a+'}'
        a = json.loads(a)
        try:
             b = a['data']['programmedContent']['videoPlayer']['mediaDTO']['IOSRenditions']
             u =''
             rate = 0
             for c in b:
                if c['encodingRate'] > rate:
                   rate = c['encodingRate']
                   u = c['defaultURL']
             b = a['data']['programmedContent']['videoPlayer']['mediaDTO']['renditions']
             for c in b:
                if c['encodingRate'] > rate:
                   rate = c['encodingRate']
                   u = c['defaultURL']
             if rate == 0:
                 try:
                    u = a['data']['programmedContent']['videoPlayer']['mediaDTO']['FLVFullLengthURL']
                 except:
                    u = ''
             return u

        except:
             pass
         
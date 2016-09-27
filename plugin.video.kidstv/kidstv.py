# -*- coding: utf-8 -*-
import requests,re
from bs4 import BeautifulSoup

def get_mms_list(mmsId,page='1'):
    r = requests.get('http://vod.kidstv.co.il/Shared/Ajax/GetMMSDiv.aspx?mmsId='+mmsId+'&pageNum='+page)
    soup = BeautifulSoup(r.content,'html.parser')
    script = soup.find('script',{'type':'text/javascript'})
    scriptList = script.text.replace('\n','').replace('  var playListArr=','').replace('; ','').split('new Array()')
    if soup.a != None:
        next=True
    else:
        next = False
    epsList=[]
    for token in scriptList:
        newsplit = token.split('playListArr')
        counter = 0
        detailsDict = {}
        for token2 in newsplit:
            #print token2
            if counter==3:
                counter=0
                epsList.append(detailsDict)
                detailsDict = {}
            a = re.compile("]='(.*)'").findall(token2)
            if a!=[]:
                if counter ==0:
                    detailsDict['token'] = a[0]
                elif counter ==1:
                    detailsDict['title'] = a[0]
                elif counter ==2:
                    detailsDict['image'] = a[0]
                counter=counter+1
    return {'episodes':epsList,'next':next}

def get_shows_menu(page='1'):
    r = requests.get('http://vod.kidstv.co.il/Shared/Ajax/GetMMSDiv.aspx?mmsId=5005&pageNum='+page)
    soup = BeautifulSoup(r.content,'html.parser')
    div =soup.find('div',{'class':'items-list video-list'}) 
    a = div.findAll('a')
    showsList = []
    if soup.a != None:
        next=True
    else:
        next = False
    for link in a:
        showsList.append({'mmsId':re.compile('#get-mms_(.*)_0_1').findall(link.get('href'))[0],'title':link.get('title'),'image':link.img.get('src')})
    return {'shows':showsList,'next':next}

def getStreams(token):
    url = 'http://ktv-metadata-rr-d.vidnt.com/vod/vod/'+token+'/HDS/metadata.xml'
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'html.parser')
    streams =[]
    for stream in soup.findAll('fileurl'):
        streams.append({'quality':stream.get('height')+'p - '+stream.get('bitrate'),'url':stream.text,'title':soup.find('title').text,'image':soup.find('posterimg').text})
    return streams
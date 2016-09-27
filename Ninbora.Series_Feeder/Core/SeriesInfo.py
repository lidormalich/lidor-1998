# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import xbmc
import json
import codecs
import glob
import Log
import helpers.Text as Text
import helpers.File as File
import xml.etree.ElementTree as et
import zipfile
from networks.FileLoader import *
from StreamMode import *
from urllib2 import Request, urlopen

#==============================================================================
# Holds data about a movie
#==============================================================================
class SeriesInfo:
  #============================================================================
  # Create a new SeriesInfo
  #============================================================================
  def __init__(self):
    self.name     = ''
    self.year     = 0
    self.imdbId   = None
    self.tvdbId   = None
    self.tmdbId = None
    self.traktId = None
    self.tvdbName = ''
    self.imdbInfo = {}
    self.episodes = []
  #============================================================================
  # Init with SeriesInfo
  #   Params : name   = The name of the series as str
  #            year   = The year of the series as str
  #            imdbId = The imdb id of the series as str
  #============================================================================
  def initNameYearId(self,name,year,imdbId):
    self.name     = Text.unescapeHtml(name.strip())
    self.year     = int(year.strip())
    self.imdbId   = imdbId.strip()
    return self
  #============================================================================
  # Init with imdb json info
  #   Params : info   = imdb info as json
  #============================================================================
  def initImdb(self,imdbId):
    self.imdbId = imdbId
    self.loadImdb()
    return self
  #============================================================================
  # Init with imdb json info
  #   Params : info   = imdb info as json
  #============================================================================
  def initImdbInfo(self,imdbInfo):
    self.imdbInfo = imdbInfo
    self.imdbId   = self.imdbInfo.get("imdbID")
    if self.name == '':
      self.name = self.imdbInfo.get("Title")
    if self.year == 0:
      self.year = int(self.imdbInfo.get("Year")[:4])
    return self

  def initTraktId(self, traktId):
    self.traktId = traktId
    self.loadTraktId()
    return self
	
  def initTmdbId(self, tmdbId):
    self.tmdbId = tmdbId
    self.loadTmdbId()
    return self

  #============================================================================
  # Init with tvdb json info
  #   Params : info   = imdb info as json
  #============================================================================
  def initTvdb(self,tvdbId):
    self.tvdbId = tvdbId
    return self
  #============================================================================
  # find the rating
  #============================================================================
  def findRating(self):
    try:
      rating = self.imdbInfo.get('imdbRating')
      if rating != None:
        return float(rating)
    except:
      return 0
  #============================================================================
  # find the genre list
  #============================================================================
  def findGenres(self):
    genre = self.imdbInfo.get('Genre')
    if not genre:
      return []
    return [xx.strip() for xx in genre.split(',')]
  #============================================================================
  # find the country list
  #============================================================================
  def findCountries(self):
    country = self.imdbInfo.get('Country')
    if not country:
      return []
    return [xx.strip() for xx in country.split(',')]
  #============================================================================
  # find clean name
  #============================================================================
  def findNameClean(self):
    name = self.name if self.name != None else 'unknown'
    return File.cleanName(self.name)[:50].lower()
  #============================================================================
  # Load IMDB data
  #============================================================================
  def loadImdb(self):
    try:
      if self.imdbInfo != {}:
        return True
      params = {}
      if self.imdbId != None:
        params['i'] = self.imdbId
      else:
        params['t'] = self.name
        params['y'] = self.year
      ff = FileLoader.load('http://www.omdbapi.com/' , params = params )
      info = json.loads(ff.data)
      if info.get('Response') == 'False':
        return False
      self.initImdbInfo(info)
      self.loadTraktId()
      self.loadTmdbId()
      return True
    except Exception , ee:
      Log.log(Text.formatException(ee))
      return False


  def loadTraktId(self):
    if self.traktId != None:
      return True
    if self.imdbId == None:
      self.loadImdb(self)
    headers = {
      'Content-Type': 'application/json',
      'trakt-api-version': '2',
      'trakt-api-key': '9732c09aadf88f287e38cab293fe5732facbb236595ac93d6036b3ce459eb1f2'
    }
    request = Request('https://api-v2launch.trakt.tv/search?id_type=imdb&id=' + self.imdbId, headers=headers)
    try:
      response = urlopen(request)
    except Exception, ee:
      Log.log(Text.formatException(ee))
      return False
    data = json.load(response)
    #Log.log('IMDB ID: ' + self.imdbId)
    #Log.log(data)
    if not data:
      Log.log('No trakt.tv data for this show. SALTS link will not work')
      traktId=''
    else:
      traktId = data[0]['show']['ids']['trakt']
    self.initTraktId(traktId)
    return True
	
  def loadTmdbId(self):
    if self.tmdbId != None:
      return True
    if self.imdbId == None:
      self.loadImdb(self)
 #   Log.log('http://api.themoviedb.org/3/find/' + self.imdbId + '?api_key=e675b61c515daa2b18932147aa0653ec&external_source=imdb_id')
    request = Request('http://api.themoviedb.org/3/find/' + self.imdbId + '?api_key=e675b61c515daa2b18932147aa0653ec&external_source=imdb_id')
    try:
      response = urlopen(request)
    except Exception, ee:
      Log.log(Text.formatException(ee))
      return False
    data = json.load(response)
#    Log.log('IMDB ID: ' + self.imdbId)
#    Log.log(data)
    if not data:
      Log.log('no tmdb data for this who. Quasar Link wont work')
      tmdbId = ''
    else:
      tmdbId=data['tv_results'][0]['id']
    self.initTmdbId(tmdbId)
    return True

  #============================================================================
  # Load episodes
  #============================================================================
  def loadEpisodes(self,lang='en',updateNow=False):
    try:
      downloadAll = updateNow or self.loadTvdbInfo(lang=lang)
      if downloadAll:
        ff = FileLoader.load('http://thetvdb.com/api/1D62F2F90030C444/series/{0}/all/en.zip'.format( self.tvdbId ), loadData=False)
        if ff.state != FileLoader.idOk:
          return False
        zf = zipfile.ZipFile(ff.target)
        root = et.fromstring( zf.read('en.xml') )
        for ndEpisode in root.findall('Episode'):
          season  = int(ndEpisode.find('./SeasonNumber' ).text)
          episode = int(ndEpisode.find('./EpisodeNumber').text)
          name    = ndEpisode.find('./EpisodeName'  ).text
          #airdate = ndEpisode.find('./FirstAired').text
          if not ndEpisode.find('./FirstAired').text == None:
            airdate = ndEpisode.find('./FirstAired').text
          else:
            airdate = ''
          self.episodes.append( EpisodeInfo(self, season, episode, name, airdate) )
        return True
      else:
        pass
    except Exception, ee:
      Log.log(Text.formatException(ee))
    return False
  #============================================================================
  # Load local stored data
  #============================================================================
  def loadLocalInfo(self):
    try:
      lines = []
      files = glob.glob( os.path.join( SeriesInfo.tvdbDataDir , '*_{0}.tvdb'.format(self.findNameClean() ) ) )
      if len(files) == 0:
        return False
      path = files[0]
      if os.path.exists(path) == False:
        return False
      Log.log(u'Load {0}'.format(path) )
      with codecs.open(path,'w', encoding='utf8') as ff:
        lines = ff.readlines()
      if len(lines) > 0:
        parts = lines[0].split('|')
        self.tvdbId   = parts[0].strip()
        self.imdbId   = parts[1].strip()
        self.tvdbName = parts[2].strip()
        for ii in range( 1 , len(lines) ):
          parts = lines[ii].split('|')
          self.episodes.append( EpisodeInfo(self, parts[0].strip() , parts[1].strip() , parts[2].strip()))
        return True
    except:
      pass
    return False
  #============================================================================
  # Load local stored data
  #============================================================================
  def loadLocalInfoById(self):
    try:
      files = glob.glob( os.path.join( SeriesInfo.tvdbDataDir , '{0}_*.tvdb'.format(self.tvdbId ) ) )
      if len(files) == 0:
        return False
      path = files[0]
      if os.path.exists(path) == False:
        return False
      Log.log(u'Load {0}'.format(path) )
      with codecs.open(path,'r', encoding='utf8') as ff:
        lines = ff.readlines()
      if len(lines) > 0:
        parts = lines[0].split('|')
        self.imdbId   = parts[0].strip()
        self.tvdbId   = parts[1].strip()
        self.tvdbName = parts[2].strip()
    except:
      pass
    return False
  #============================================================================
  # find the rating
  #============================================================================
  def loadTvdbInfo(self,lang="en"):
    if self.tvdbId != None:
      return False
    if self.loadLocalInfo():
      return False
    ff = FileLoader.load('http://thetvdb.com/api/GetSeriesByRemoteID.php' , params = { 'imdbid' : self.imdbId , 'language': lang } )
    Log.log(u'Load {0}'.format(ff.source) )
    tree = et.parse( ff.target )
    ndSeasion = tree.find('./Series/seriesid'  )
    ndName    = tree.find('./Series/SeriesName')
    if ndSeasion == None or ndName == None:
      return False
    self.tvdbId   = (ndSeasion).text.strip()
    self.tvdbName = (ndName   ).text.strip()
    self.tvdbTime = 0
    return True
  #============================================================================
  # save the movie in .strm format for GOmovies addon
  #============================================================================
  def save(self, dirTarget , langid = 7, withThumb=False,streamMode=StreamMode.Exodus):
    added    = 0
    episodes = 0
    base = File.cleanName(u'{0} ({1})'.format( self.name.lower() , self.year ))
    dirSeries = os.path.join( dirTarget , base )
    self.saveTvdbInfo()
    if os.path.exists(dirSeries) == False:
      added += 1
    self.saveTvshow(dirSeries, langid = langid)
    episodes = 0
    for episode in self.episodes:
      try:
        if episode.season == 0:
          continue
        if episode.name == 'TBA':
          continue
        dirSeason = os.path.join( dirSeries , File.cleanName(u'{0}.S{1:02}'.format(self.findNameClean() , episode.season)) )
        self.saveTvshow(dirSeason, langid = langid)

        name = u'{3}.S{0:02}E{1:02}.{2}'.format( episode.season, episode.episode , episode.name , self.name )

        part0 = dirSeason
        part1 = self.name
        part2 = '.S{0:02}E{1:02}.'.format(episode.season, episode.episode)
        part3 =  episode.name[:256--len(part0)-len(part1)-len(part2)-10]

        base = File.cleanName(u'{0}{1}{2}'.format(part1,part2,part3))

        links = []
        if streamMode == StreamMode.Exodus:
          links.append([name,episode.asExodus()])
        if streamMode == StreamMode.Pulsar:
          links.append([name,episode.asPulsar()])

        if streamMode == StreamMode.Salts:
          links.append([name,episode.asSalts()])
        if streamMode == StreamMode.Quasar:
          links.append([name,episode.asQuasar()])


        strm = os.path.join( dirSeason, u'{0}.{1}'.format( base , 'strm' ) )
        if os.path.exists(strm) == False:
          episodes += 1
        with codecs.open(strm,'w') as ff:
          ff.write("#EXTM3U\n")
          for xx in links:
            ff.write(u'#EXTINF:{0},{1}\n'.format(0,xx[0] ))
            ff.write(u'{0}\n'.format(xx[1]))
      except Exception, ee:
        Log.log(Text.formatException(ee))
    if withThumb:
      thumb = os.path.join( dirSeries, 'folder.jpg'.format( base , 'jpg' ) )
      if os.path.exists(thumb) == False:
        FileLoader.load(self.imdbInfo.get('Poster'), '@' + thumb )
    self.createHtml()
    return (added, episodes)
  #============================================================================
  # Save tvshow.nfo file
  #   Params: dirTarget = The target directory to save
  #           langid    = The language id
  #============================================================================
  def saveTvshow(self, dirTarget, langid = 7 ):
    File.ensureFolder(dirTarget)
    with file( os.path.join( dirTarget , 'tvshow.nfo') , 'w' ) as ff:
      ff.write( 'http://thetvdb.com/?{0}={1}&{2}={3}&{4}={5}'.format('tab' , 'series', 'id', self.tvdbId, 'lid' , langid) )
  #============================================================================
  # find the rating
  #============================================================================
  def saveTvdbInfo(self):
    path = os.path.join( SeriesInfo.tvdbDataDir , u'{0}_{1}.tvdb'.format(self.tvdbId , self.findNameClean() ))
    with codecs.open(path,'w', encoding='utf8') as ff:
      ff.write(u'{1:10}|{0:10}|{3}|{2}\n'.format(self.tvdbId , self.imdbId, self.tvdbName, int(time.time()) ))
      for episode in self.episodes:
        ff.write(u'{0:2} | {1:2} | {2}\n'.format(episode.season, episode.episode, episode.name))
  #============================================================================
  @staticmethod
  #============================================================================
  # load local series
  #============================================================================
  def loadLocalSeries():
    ids = []
    files = glob.glob( os.path.join( SeriesInfo.tvdbDataDir , '*_*.tvdb') )
    for name in files:
      name = name.replace(SeriesInfo.tvdbDataDir,'')
      ids.append(int (name[1:name.find('_')]))
    return ids
  #============================================================================
  # find last tvdb scan time and update the scan time
  #============================================================================
  @staticmethod
  def loadUpdatedSeries():
    ids = []
    tt = 0
    path = os.path.join( SeriesInfo.tvdbDataDir,'.time' )
    try:
      if os.path.exists(path) == False:
        ff = FileLoader.load('http://thetvdb.com/api/Updates.php',params = { 'type':'none' }, proxy=Cache.Disabled )
        tree = et.parse( ff.target )
        ndTime = tree.find('./Time')
        with file(path, 'w') as ft:
          ft.write( '{0}'.format( int(ndTime.text) ))
        return ids
    except:
      pass
    try:
      with file(path, 'r') as ff:
        tt = int(ff.read())
    except:
      pass
    try:
      ff = FileLoader.load('http://thetvdb.com/api/Updates.php',params = { 'type':'series' , 'time': tt }, proxy=Cache.Disabled )
      tree = et.parse( ff.target )
      for ndSeries in tree.findall('./Series'):
        ids.append(int(ndSeries.text))
      ndTime = tree.find('./Time')
      with file(path, 'w') as ft:
        ft.write( '{0}'.format( int(ndTime.text) ))
    except:
      pass
    return ids

  def createHtml(self):
    try:
      pathMold = os.path.join( SeriesInfo.tvdbMoldDir, u'{0}.html'.format('add') )
      pathHtml = os.path.join( SeriesInfo.tvdbHtmlDir, u'{0}.html'.format(self.findNameClean()) )
      with codecs.open(pathMold, 'r' , encoding='utf8' ) as ff:
        mold = ff.read()
      mold = mold.replace('{{name}}'      , self.name      )
      mold = mold.replace('{{year}}'      , str(self.year) )
      mold = mold.replace('{{imdbId}}'    , self.imdbId )
      mold = mold.replace('{{tvdbId}}'    , self.tvdbId )
      mold = mold.replace('{{name1}}'     , self.name.lower().replace(' ','-') )
      mold = mold.replace('{{genre}}'     , self.imdbInfo.get('Genre'))
      mold = mold.replace('{{runtime}}'   , self.imdbInfo.get('Runtime'))
      mold = mold.replace('{{runtime}}'   , self.imdbInfo.get('Runtime'))
      mold = mold.replace('{{imdbRating}}', self.imdbInfo.get('imdbRating'))
      mold = mold.replace('{{actors}}'    , self.imdbInfo.get('Actors'))
      with codecs.open(pathHtml, 'w' , encoding='utf8' ) as ff:
        ff.write( mold )
    except Exception, ee:
      pass
  tvdbDataDir = './'
  tvdbMoldDir = './'
  tvdbHtmlDir = './'


class EpisodeInfo:
  #============================================================================
  # create url for GOtv addon
  #  Params: owner   - The SeriesInfo of this episode
  #          season  - The season number this episode belong to
  #          episode - The episode number
  #          name    - The episode number
  #============================================================================
  def __init__(self,owner, season, episode, name, airdate):
    self.owner   = owner
    self.season  = int(season)
    self.episode = int(episode)
    self.name    = name if name != None else 'Episode {0}'.format(self.episode)
    self.airdate = airdate.strip()
  #============================================================================
  # create url for Exodus addon
  #============================================================================
  def asExodus(self):
    params = {}
    params['action'  ] = 'play'
    params['title'   ] = self.name
    params['year'    ] = self.owner.year	
    params['imdb'    ] = self.owner.imdbId[2:] if self.owner.imdbId != None else ''
    params['tvdb'    ] = self.owner.tvdbId
    params['season'  ] = self.season
    params['episode' ] = self.episode
    params['tvshowtitle'    ] = self.owner.name
    params['premiered'       ] = self.airdate
    return Text.buildUrl('plugin://plugin.video.exodus/' , params )
  #============================================================================
  # create url for Pulsar addon
  #============================================================================
  def asPulsar(self):
    return 'plugin://plugin.video.pulsar/show/{0}/season/{1}/episode/{2}/links'.format(self.owner.tvdbId,self.season,self.episode)
  #============================================================================
  # Irrelevant
  #============================================================================
  def asPulsarPlay(self):
    return 'plugin://plugin.video.pulsar/show/{0}/season/{1}/episode/{2}/play'.format(self.owner.tvdbId,self.season,self.episode)

  #============================================================================
  # Create URL for quasar addon
  #============================================================================
  def asQuasar(self):
    return 'plugin://plugin.video.quasar/library/play/show/{0}/season/{1}/episode/{2}'.format(self.owner.tmdbId,self.season,self.episode)


  #============================================================================
  # create url for SALTS
  #============================================================================
  def asSalts(self):

    params = {}
    params['ep_airdate'] = self.airdate
    params['trakt_id'      ] = self.owner.traktId
    params['episode'   ] = self.episode
    params['mode'      ]='get_sources'
    params['dialog'] = 'True'
    params['title'     ]=self.owner.name
    params['ep_title'  ]=self.name
    params['season'    ]=self.season
    params['video_type']='Episode'
    params['year'      ]=self.owner.year
    #params['slug'      ]=self.owner.name.replace(' ','-').lower()
    return Text.buildUrl('plugin://plugin.video.salts/' , params )

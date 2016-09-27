# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

from urllib2 import Request, urlopen
import json
import Log
import helpers.Text as Text
import helpers.File as File
import codecs
from networks.FileLoader import *
from StreamMode import *
#==============================================================================
# Holds data about a movie
#==============================================================================
class MovieInfo:
  #============================================================================
  # Create a new MovieInfo
  #   Params : nameHe = The name of the movie in hebrew
  #            nameEn = The name of the movie in english
  #            year   = The year of the movie
  #            id     = The external id of the movie
  #============================================================================
  def __init__(self,nameHe,nameEn,year,id):
    self.nameHe     = Text.unescapeHtml(nameHe.strip())
    self.nameEn     = Text.unescapeHtml(nameEn.strip())
    self.year       = int(year.strip())
    self.idSubtitle = id.strip()
    self.traktId = None
  #============================================================================
  # Load IMDB data
  #============================================================================
  def loadImdb(self):
    imdbInfo = {}
    try:
      ff = FileLoader.load('http://www.omdbapi.com/' , params = { 't' : self.nameEn , 'y' : self.year } )
      imdbInfo = json.loads(ff.data)
    except Exception , ee:
      Log.log(str(ee))
    self.setImdb(imdbInfo)
    self.loadTraktId()
    return self.idImdb != None
  #============================================================================
  # Set IMDB data
  #   Params: imdbInfo = imdb Key/value data
  #============================================================================

  def loadTraktId(self):
    if self.traktId != None:
      return True
    if self.idImdb == None:
      return False
    headers = {
      'Content-Type': 'application/json',
      'trakt-api-version': '2',
      'trakt-api-key': '9732c09aadf88f287e38cab293fe5732facbb236595ac93d6036b3ce459eb1f2'
    }
    request = Request('https://api-v2launch.trakt.tv/search?id_type=imdb&id=' + self.idImdb, headers=headers)
    try:
      response = urlopen(request)
    except Exception, ee:
      Log.log(Text.formatException(ee))
      return False
    data = json.load(response)
    #Log.log('traktid: ' + self.idImdb)
    #Log.log(data)
    if not data:
      traktId=''
    else:
      traktId = data[0]['movie']['ids']['trakt']
    self.initTraktId(traktId)
    return True

  def setImdb(self,imdbInfo):
    self.imdbInfo = imdbInfo
    self.idImdb   = self.imdbInfo.get("imdbID")

  def initTraktId(self, traktId):
    self.traktId = traktId
    self.loadTraktId()
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
  # create url for Genesis addon
  #============================================================================
  def asExodus(self):
    params = {}
    params['action'] = 'play'
    params['title' ] = self.nameEn
    params['imdb'  ] = self.idImdb[2:]
    params['year'  ] = self.year
    return Text.buildUrl('plugin://plugin.video.exodus/' , params )

  def asPulsar(self):
    """
    Create url for Pulsar addon
    """
    return 'plugin://plugin.video.pulsar/movie/{0}/links'.format(self.idImdb)

  def asSalts(self):
    """
    Create url for Salt addon
    """
    params = {}
    params['title'     ] = self.nameEn
    params['video_type'] = 'Movie'
    params['trakt_id'] = self.traktId
    params['mode'      ] = 'get_sources'
    params['dialog'    ] = True
    params['year'      ] = self.year
    #params['slug'      ] = u'{0}-{1}'.format(self.nameEn.replace(' ','-').lower(), self.year)
    return Text.buildUrl('plugin://plugin.video.salts/' , params )

  def asQuasar(self):
    """
    Create url for Quasar addon
    """
    return 'plugin://plugin.video.quasar/library/play/movie/{0}'.format(self.idImdb)


  def asPulsarPlay(self):
    """
    Create url for Pulsar addon
    """
    return 'plugin://plugin.video.pulsar/movie/{0}/play'.format(self.idImdb)

  def save(self, dirTarget,withThumb=False,streamMode=StreamMode.Exodus):
    """
    save the movie in .strm format for GOmovies addon
    """
    name = '{0} ({1})'.format( self.nameEn.lower()[:40] , self.year )
    base = File.cleanName(name)
    dirTarget = os.path.join( dirTarget , base )
    info = os.path.join( dirTarget, '{0}.{1}'.format( base , 'nfo'  ) )
    File.ensureFolder(dirTarget)

    links = []
    if streamMode == StreamMode.Exodus:
      links.append([name,self.asExodus()])
    if streamMode == StreamMode.Pulsar:
      links.append([name,self.asPulsar()])
    if streamMode == StreamMode.Salts:
      links.append([name,self.asSalts()])
    if streamMode == StreamMode.Quasar:
      links.append([name,self.asQuasar()])

    strm = os.path.join( dirTarget, '{0}.{1}'.format( base , 'strm' ) )
    with codecs.open(strm,'w') as ff:
      ff.write("#EXTM3U\n")
      for xx in links:
        ff.write(u'#EXTINF:{0},{1}\n'.format(0,xx[0] ))
        ff.write(u'{0}\n'.format(xx[1]))
    if withThumb:
      thumb = os.path.join( dirTarget, 'folder.jpg'.format( base , 'jpg' ))
      if os.path.exists(thumb) == False:
        FileLoader.load(self.imdbInfo.get('Poster'), '@' +  thumb )
    if os.path.exists(info):
      return False
    with codecs.open(info,'w') as ff:
      ff.write('http://www.imdb.com/title/{0}'.format(self.idImdb))
    return True
  #============================================================================
  # Create from IMDB data
  #   Params: imdbInfo = IMDB Key/value data
  #============================================================================
  @staticmethod
  def createFromImdb(imdbInfo):
    if imdbInfo == None:
      return None
    name   = imdbInfo.get('Title')
    year   = imdbInfo.get('Year')
    imdbId = imdbInfo.get('imdbID')
    mi = MovieInfo(name,name,year,'0')
    mi.setImdb(imdbInfo)
    return mi
# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import Log
import re
from networks.FileLoader import *
#============================================================================
# Filter items to filter
#============================================================================
class FilterInfo:
  #============================================================================
  # Load all the filter items from <config>
  #    Params : config = The key/value data store
  #============================================================================
  def __init__(self,config = None):
    self.config = config
    if self.config != None:
      self.genre         = [ (self.config.getBool( "{0}_{1:02}".format("genre"  , ii ))) for ii in range( 0 , len(FGenre.names) ) ]
      self.yearAbove     = self.config.getInt("year_above")
      self.yearBelow     = self.config.getInt("year_below")
      self.ratingAbove   = self.config.getFloat("rating_above")
      self.ratingBelow   = self.config.getFloat("rating_below")
      self.votesAbove    = self.config.getInt("votes_above")
      self.sortMode      = self.findValue("sort_mode"      , FSortMode.names      )
      self.sortDirection = self.findValue("sort_direction" , FSortDirection.names )
      self.langInfo      = self.findValue("lang_info"      , FLangInfo.ids        )
      self.langSubs      = self.findValue("lang_subs"      , FLangSubs.names      )
      self.episodeAbove  = self.config.getInt("episode_above")
      self.episodeYearMax= self.config.getInt("episode_year_max")
      self.loadIgnore()
    else:
      self.genre         = [ False for ii in range( 0 , len(FGenre.names ) ) ]
      self.yearAbove     = 1900
      self.yearBelow     = 2020
      self.ratingAbove   = 0
      self.ratingBelow   = 10
      self.votesAbove    = 10000
      self.sortMode      = FSortMode.name[0]
      self.sortDirection = FSortDirection.name[0]
      self.episodeAbove  = 0
      self.episodeYearMax= 0
      self.ignore        = []
  #============================================================================
  # Whether the <year> is valid for the current filter values
  #   Params : year = the year to check
  #============================================================================
  def isValidYear(self,year):
    return year >= self.yearAbove and year <= self.yearBelow
  #============================================================================
  # Whether the <rating> is valid for the current filter items
  #   Params : rating = the rating to check
  #============================================================================
  def isValidRating(self,rating):
    return rating >= self.ratingAbove and rating <= self.ratingBelow
  #============================================================================
  # Whether the <genres> is valid for the current filter items
  #   Params : genres = list of genres to check if valid
  #============================================================================
  def isValidGenre(self,genres):
    if self.genre[0]:
      return True
    for ii in range(1, len( FGenre.names ) ):
      if self.genre[ii]:
        try:
          genres.index( FGenre.names[ii] )
          return True
        except:
          pass
    return False
  #============================================================================
  # Whether the <countries> is valid for the current filter items
  #   Params : countries = list of countries to check if valid
  #============================================================================
  def isValidCountry(self,countries):
    try:
      countries.index('Israel')
      return False
    except:
      return True
  #============================================================================
  # Whether the item is not in ignore list
  #   Params : si = the series info item
  #============================================================================
  def isNoIgnore(self,si):
    try:
      self.ignore.index(si.imdbId)
      return False
    except:
      return True
  #============================================================================
  # Whether the <countries> is valid for the current filter items
  #   Params : countries = list of countries to check if valid
  #============================================================================
  def isValidEpisode(self,si):
    if si.year > self.episodeYearMax:
      return True
    return len(si.episodes) >= self.episodeAbove
  #============================================================================
  # Whether the to item with imbbId has subs of lang_sub filter
  #   Params : imdbId = The id of the item
  #============================================================================
  def hasSubs(self,si):
    if self.langSubs == '':
      return True
    if self.langSubs != 'Hebrew':
      valid = False
      ff = FileLoader.load('http://www.subtitleseeker.com/feeds/titles/{0:0>7}/rss'.format(si.imdbId[2:]))
      if ff.state == FileLoader.idFail:
        return False
      return ff.data.find('<b>Language :</b> {0}<br />'.format(self.langSubs)) >= 0
    if self.langSubs == 'Hebrew':
      valid = False
      ff = FileLoader.load('http://subscenter.cinemast.com/he/subtitle/series/{0}'.format(si.name.lower().replace(' ','-')), proxy=Cache.Disabled)
      if ff.state == FileLoader.idFail:
        ff = FileLoader.load('http://subscenter.cinemast.com/he/subtitle/series/{0}-{1}'.format(si.name.lower().replace(' ','-'),si.year), proxy=Cache.Disabled)
      if ff.state == FileLoader.idOk:
        mm = re.search('episodes_group = (?P<info>.*?)\n', ff.data)
        if mm and mm.group('info').find('"he"') >= 0:
          valid = True
      return valid
  #============================================================================
  # Find genres list
  #   Params : countries = list of countries to check if valid
  #============================================================================
  def findGenres(self,seperator='|'):
    if self.genre[0]:
      return ''
    genres = ''
    count = 0
    for ii in range(1,len(FGenre.names)):
      if self.genre[ii]:
        if genres != '':
          genres = genres + seperator
        genres = genres + FGenre.names[ii]
    return genres
  #============================================================================
  # load ignore list
  #   Params : countries = list of countries to check if valid
  #============================================================================
  def loadIgnore(self):
    self.ignore = []
    for ss in self.config.getStr('ignore_text').split(','):
      ss = ss.strip()
      if ss.startswith('tt'):
        self.ignore.append(ss)
    ff = FileLoader.load(self.config.getStr('ignore_file'))
    for ss in ff.data.split('\n'):
      ss = ss.strip()
      if ss.startswith('tt'):
        self.ignore.append(ss)
  #============================================================================
  # Find the mapped value of key
  #   Params : key    = The config key for integer value
  #            values = The values
  #============================================================================
  def findValue(self,key, values):
    ii = self.config.getInt(key)
    ii = ii if (ii > 0 and ii < len(values) ) else 0
    return values[ii]
#============================================================================
# Genre filter items
#============================================================================
class FGenre:
  names = [
    u"Any"         , #00
    u"Action"      , #01
    u"Adventure"   , #02
    u"Comedy"      , #03
    u"Drama"       , #04
    u"Horror"      , #05
    u"Thriller"    , #06
    u"Animation"   , #07
    u"Western"     , #08
    u"War"         , #09
    u"Romance"     , #10
    u"Sci-Fi"      , #11
    u"Mystery"     , #12
    u"Crime"       , #13
    u"History"     , #14
    u"Family"      , #15
    u"Fantasy"     , #16
    u"Documentary" , #17
    u"Biography"   , #18
    u"Music"       , #19
    u"Musical"     , #20
    u"Adult"       , #21
    u"News"        , #22
    u"Short"       , #23
    u"Sport"       , #24
    u"Film-Noir"     #25
  ]

class FSortMode:
  names = [
    u"num_votes"       , #00
    u"moviemeter"      , #01
    u"user_rating"     , #02
    u"year"            , #03
    u"release_date_us"   #04
  ]

class FSortDirection:
  names = [
    u"desc"     , #00
    u"asc"      , #01
  ]

class FLangInfo:
  ids = [
     7 , #01 English
     8 , #02 Svenska
     9 , #03 Norsk
    10 , #04 Dansk
    11 , #05 Suomeksi
    13 , #06 Nederlands
    14 , #07 Deutsch
    15 , #08 Italiano
    16 , #09 Espanol
    17 , #10 Francais
    18 , #11 Polski
    19 , #12 Magyar
    20 , #13 Greek
    21 , #14 Turkish
    22 , #15 Russian
    24 , #16 Hebrew
    25 , #17 Japanese
    26 , #18 Portuguese
    27 , #19 Chinese
    28 , #20 Czech
    30 , #21 Slovenian
    31 , #22 Croatian
    32 , #23 Korean
  ]


class FLangSubs:
  names = [
    ""           , #01
    "Albanian"   , #02
    "Albanian"   , #03
    "Arabic"     , #04
    "Bosnian"    , #05
    "Brazilian"  , #06
    "Bulgarian"  , #07
    "Croatian"   , #08
    "Czech"      , #09
    "Danish"     , #10
    "Dutch"      , #11
    "English"    , #12
    "Estonian"   , #13
    "Farsi"      , #14
    "Finnish"    , #15
    "French"     , #16
    "German"     , #17
    "Greek"      , #18
    "Hebrew"     , #19
    "Hungarian"  , #20
    "Italian"    , #21
    "Norwegian"  , #22
    "Polish"     , #23
    "Portuguese" , #24
    "Romanian"   , #25
    "Russian"    , #26
    "Serbian"    , #27
    "Slovenian"  , #28
    "Spanish"    , #29
    "Swedish"    , #30
    "Turkish"    , #31
    "Vietnamese"   #32
  ]



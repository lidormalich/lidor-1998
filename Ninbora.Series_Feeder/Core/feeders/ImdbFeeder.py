# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import os.path
import json
import re
import Log
import helpers.File as File
from networks.FileLoader import *
from SeriesInfo import *
from StreamMode import *

class ImdbFeeder:
  #============================================================================
  # Create Feeder for www.subtitle.co.il
  #============================================================================
  def __init__(self):
    self.reSeries0 = "<a href=\"/title/(?P<id>tt\d+)/\">(?P<name>.*?)</a>.*?<span class=\"year_type\">\((?P<year>\d+)"
    self.dirTarget = "./info"
    self.withThumb = False
    self.streamMode= StreamMode.Exodus
  #============================================================================
  # Log message
  #============================================================================
  def log(self,message):
    Log.log(u'{0} : {1}'.format( 'ImdbFeeder' , message ))
  #============================================================================
  # Fetch new series
  #   Params : loadInfo = The loadInfo
  #============================================================================
  def addSeries(self,loadInfo):
    addedNow = 0
    self.log(u'Start addSeries')
    genres = loadInfo.filter.findGenres()
    params = {}
    params['at'         ] = '0'
    params['num_votes'  ] = '{0},'.format( loadInfo.filter.votesAbove )
    params['sort'       ] = '{0},{1}'.format(loadInfo.filter.sortMode   ,  loadInfo.filter.sortDirection )
    params['year'       ] = '{0},{1}'.format(loadInfo.filter.yearAbove  ,  loadInfo.filter.yearBelow     )
    params['user_rating'] = '{0},{1}'.format(loadInfo.filter.ratingAbove,  loadInfo.filter.ratingBelow   )
    params['title_type' ] = 'tv_series'
    if genres != '':
      params['genres'  ] = genres.lower()
    itemsPerPage = 50
    pages = loadInfo.maxFetched  / itemsPerPage
    pages = pages if pages > 1 else 1
    page = 1
    while page <= pages and loadInfo.isFetchAll() == False:
      params['start'     ] = ( page - 1 ) * itemsPerPage + 1
      ff = FileLoader.load('http://www.imdb.com/search/title', params = params , proxy=Cache.Disabled )
      self.log(u'download page {0}/{1} {2}'.format(page,pages, ff.source))
      sis = []
      for ii in re.finditer( self.reSeries0 , ff.data , re.DOTALL ):
        sis.append( SeriesInfo().initNameYearId( ii.group('name'), ii.group('year'),ii.group('id') ) )
      if self.addSeriesInfo(sis,loadInfo):
        break
      page +=1

    self.log(u'End addSeries. Added {0}, epispdos {1}'.format(loadInfo.added, loadInfo.episodes))
    return loadInfo.added
  #============================================================================
  # Fetch new episodes in current series
  #   Params : loadInfo = The loadInfo
  #============================================================================
  def addEpisode(self,loadInfo):
    self.log(u'Start addEpisode')
    aa = SeriesInfo.loadLocalSeries()   ; aa.sort() ; self.log(u'Local  : {0}'.format(aa))
    uu = SeriesInfo.loadUpdatedSeries() ; uu.sort() ; self.log(u'Update : {0}'.format(uu))
    for a0 in aa:
      mi = SeriesInfo().initTvdb(a0)
      mi.loadLocalInfoById()
      mi.loadImdb()
      mi.createHtml()
      try:
        uu.index(a0)
      except:
        continue
      mi.loadEpisodes(updateNow=True)
      (added , episodes) = mi.save(self.dirTarget, langid = loadInfo.filter.langInfo, withThumb=self.withThumb,streamMode = self.streamMode)
      if added > 0:
        self.log(u'Update Item {1:03}/{0:03} : {2:<40} | {3} | {4} | {6}  | {5:<40} | {7}'.format(loadInfo.fetched, loadInfo.added, mi.name, mi.year , mi.imdbId, mi.findGenres() , mi.findRating(), mi.findCountries()))
      loadInfo.added    += added
      loadInfo.episodes += episodes
    self.log(u'End addEpisode. Added {0}, epispdos {1}'.format(loadInfo.added, loadInfo.episodes))
    return loadInfo.added

  def addSeriesInfo0(self, sis , loadInfo , doFilter):
    for si in sis:
      loadInfo.fetched += 1
      if doFilter:
        if not loadInfo.filter.isValidYear(si.year):
          continue
        if not loadInfo.filter.isNoIgnore(si):
          continue
        if not si.loadImdb():
          continue
        if not loadInfo.filter.isValidRating(si.findRating()):
          continue
        if not loadInfo.filter.isValidGenre(si.findGenres()):
          continue
        if not loadInfo.filter.isValidCountry(si.findCountries()):
          continue
        if not loadInfo.filter.hasSubs(si):
          continue
      loadInfo.addOrExist += 1
      if not si.loadEpisodes():
        continue
      if doFilter:
        if not loadInfo.filter.isValidEpisode(si):
          continue
      (added , episodes) = si.save(self.dirTarget, langid = loadInfo.filter.langInfo, withThumb=self.withThumb,streamMode = self.streamMode)
      if added > 0:
        self.log(u'Add Item {1:03}/{0:03} : {2:<40} | {3} | {4} | {6}  | {5:<40} | {7}'.format(loadInfo.fetched, loadInfo.added, si.name, si.year , si.imdbId, si.findGenres() , si.findRating(), si.findCountries() ))
      loadInfo.added    += added
      loadInfo.episodes += episodes
      if loadInfo.isFetchAll():
        return True
    return False

  def addSeriesInfo(self, sis , loadInfo):
    return self.addSeriesInfo0(sis,loadInfo, True)

  def addSeriesInfoAll(self, sis , loadInfo):
    return self.addSeriesInfo0(sis,loadInfo, False)

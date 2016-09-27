# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import os.path
import json
import re
import Log
import helpers.File as File
from networks.FileLoader import *
from MovieInfo import *
from StreamMode import *

class HebsubsFeeder:
  #============================================================================
  # Create Feeder for www.hebsubs.com
  #============================================================================
  def __init__(self):
    self.reMovie0  = "<a href=\"view.php\?id=(?P<id>\d+)#\d+\" title=\"(?P<nameHe>.*?)\|(?P<nameEn>.*?)\|(?P<year>.*?)\""
    self.reMovie   = "<table.*?{0}.*?Israel-Flag.png.*?</table>".format(self.reMovie0)
    self.dirTarget = "./info"
    self.withThumb = False
    self.streamMode= StreamMode.Exodus
  #============================================================================
  # Log message
  #============================================================================
  def log(self,message):
    Log.log('{0} : {1}'.format( 'HebsubsFeeder' , message ))
  #============================================================================
  # Fetch <items> items
  #   Params : fi    = The filter info to filter the items
  #            items = The number of item to fetch
  #============================================================================
  def load(self,loadInfo):
    self.log('Start')
    itemsPerPage = 32
    pages = loadInfo.maxFetched  / itemsPerPage
    pages = pages if pages > 1 else 1
    page = 1
    while page <= pages and loadInfo.isFetchAll() == False:
      self.log('download page {0}/{1} '.format(page,pages))
      ff = FileLoader.load('http://www.ktuvit.com/browsesubtitles.php', params = { 'page': page , 'cs' : 'movies' } , proxy=Cache.Disabled )
      mis = []
      for ii in re.finditer( self.reMovie , ff.data , re.DOTALL ):
        mis.append( MovieInfo(ii.group('nameHe'), ii.group('nameEn'),ii.group('year') , ii.group('id') ))
      for mi in mis:
        loadInfo.fetched += 1
        if not loadInfo.filter.isValidYear(mi.year):
          continue
        if not mi.loadImdb():
          continue
        if not loadInfo.filter.isValidRating(mi.findRating()):
          continue
        if not loadInfo.filter.isValidGenre(mi.findGenres()):
          continue
        if not loadInfo.filter.isValidCountry(mi.findCountries()):
          continue
        if mi.save(self.dirTarget,withThumb=self.withThumb,streamMode=self.streamMode):
          loadInfo.added += 1
          self.log('Add Item {1:03}/{0:03} : {2:<40} | {3} | {4} | {6}  | {5:<40} | {7}'.format(loadInfo.fetched, loadInfo.added, mi.nameEn, mi.year , mi.idImdb, mi.findGenres() , mi.findRating(), mi.findCountries() ))
        if loadInfo.isFetchAll():
          break
      page +=1
    self.log('End. Added {0}'.format(loadInfo.added))
    return loadInfo.added
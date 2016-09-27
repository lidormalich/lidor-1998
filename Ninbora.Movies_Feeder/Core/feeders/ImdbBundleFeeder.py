import os.path
import json
import re
import Log
import zipfile
import helpers.File as File
from networks.FileLoader import *
from LoadInfo            import *
from MovieInfo           import *


class ImdbBundleFeeder:
  #============================================================================
  # Create Feeder for www.subtitle.co.il
  #============================================================================
  def __init__(self):
    self.dirTarget = "./info"
    self.cache     = "./cache"
    self.source    = None
    self.package   = None
    self.withThumb = False
    self.streamMode= StreamMode.Exodus
  #============================================================================
  # Log message
  #============================================================================
  def log(self,message):
    Log.log('{0} : {1}'.format( 'ImdbBundleFeeder' , message ))
  #============================================================================
  # Fetch <items> items
  #   Params : filter    = The filter info to filter the items
  #            maxFected = The number of item to fetch
  #============================================================================
  def load(self,loadInfo):
    self.loadBundles(loadInfo)
    self.loadPackage(loadInfo)
  #============================================================================
  # Fetch <items> items
  #   Params : filter    = The filter info to filter the items
  #            maxFected = The number of item to fetch
  #============================================================================
  def loadBundles(self,loadInfo):
    if self.source == None:
      return
    self.log('Load bundles')
    for root, dirs, files in os.walk(self.source):
      for ff in files:
        if ff.endswith(".txt"):
          bundle = os.path.join(root,ff)
          self.log('Load {0}'.format(bundle))
          self.loadBundle(bundle,loadInfo)
          if loadInfo.isFetchAll():
            return
    self.log('End. Added {0}'.format(loadInfo.added))
  #============================================================================
  # Fetch <items> items
  #   Params : filter     = The filter info to filter the items
  #            maxFetched = The number of item to fetch
  #============================================================================
  def loadPackage(self, loadInfo):
    if self.package == None:
      return
    self.log('Load Package')
    ff = FileLoader.load(self.package,loadData=False)
    if ff.state != FileLoader.idOk:
      return
    try:
      zf = zipfile.ZipFile(ff.target)
      for name in zf.namelist():
        index = name.rfind('/')
        if index != -1:           
          folder = name[:index]          
        if name.endswith('.txt'):
          try:
            bundle = os.path.join(self.cache, name.replace('/','_'))
            self.log('Load {0}'.format(bundle))
            with open(bundle, 'wb') as ff:
              ff.write(zf.read(name))
            self.loadBundle(bundle,loadInfo)
            if loadInfo.isFetchAll():
              return
          except Exception, ee:
            Log.log(str(ee))
    except Exception, ee:
      Log.log(str(ee))
    self.log('End. Added {0}'.format(loadInfo.added))
  #============================================================================
  # Fetch <items> items
  #   Params : bundle   = The filter info to filter the items
  #            loadInfo = The loadInfo
  #============================================================================
  def loadBundle(self,bundle,loadInfo):
    ff = FileLoader.load(bundle)
    for line in ff.data.splitlines():
      try:
        mi = MovieInfo.createFromImdb( json.loads(line) )
        loadInfo.fetched += 1
        if not loadInfo.filter.isValidYear(mi.year):
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
          return
      except Exception,ee:
        self.log(str(ee))
    return True
# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import os.path
import json
import re
import Log
import zipfile
import helpers.File as File
from networks.FileLoader import *
from LoadInfo            import *
from SeriesInfo          import *
from feeders.ImdbFeeder  import *


class ImdbBundleFeeder:
  #============================================================================
  # Create Feeder for www.subtitle.co.il
  #============================================================================
  def __init__(self):
    self.dirTarget = "./info"
    self.source    = "./imdb"
    self.cache     = "./cache"
    self.streamMode= StreamMode.Exodus
    self.withThumb = False
    self.source    = None
    self.package   = None
    self.imdbIdList= None
  #============================================================================
  # Log message
  #============================================================================
  def log(self,message):
    Log.log(u'{0} : {1}'.format( 'ImdbBundleFeeder' , message ))
  #============================================================================
  #
  #============================================================================
  def addSeries(self,loadInfo):
    self.loadBundles(loadInfo)
    self.loadPackage(loadInfo)
    self.loadImdbIdList(loadInfo)
  #============================================================================
  # Fetch <items> items
  #   Params : filter    = The filter info to filter the items
  #            maxFected = The number of item to fetch
  #============================================================================
  def loadBundles(self,loadInfo):
    if self.source == None:
      return
    self.log(u'loadBundles Start')
    for root, dirs, files in os.walk(self.source):
      for ff in files:
        if ff.endswith(".txt"):
          bundle = os.path.join(root,ff)
          self.log(u'Load {0}'.format(bundle))
          self.loadBundle(bundle,loadInfo)
          if loadInfo.isFetchAll():
            return
    self.log(u'loadBundles End. Added {0}'.format(loadInfo.added,loadInfo.episodes))
    return loadInfo.added
  #============================================================================
  # Fetch <items> items
  #   Params : filter     = The filter info to filter the items
  #            maxFetched = The number of item to fetch
  #============================================================================
  def loadPackage(self,loadInfo):
    if self.package == None:
      return
    self.log(u'loadPackage Start')
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
            self.log(u'Load {0}'.format(bundle))
            with open(bundle, 'wb') as ff:
              ff.write(zf.read(name))
            self.loadBundle(bundle,loadInfo)
            if loadInfo.isFetchAll():
              return
          except Exception, ee:
            Log.log(Text.formatException(ee))
    except Exception, ee:
      Log.log(Text.formatException(ee))
    self.log(u'loadPackage End. Added {0}/{1}'.format(loadInfo.added,loadInfo.episodes))
    return loadInfo.added
  #============================================================================
  # Fetch <items> items
  #   Params : bundle   = The filter info to filter the items
  #            loadInfo = The loadInfo
  #============================================================================
  def loadBundle(self,bundle,loadInfo):
    ff = FileLoader.load(bundle)
    sis = []
    for line in ff.data.splitlines():
      try:
        si = None
        if line.startswith('tt'):
          si = SeriesInfo().initImdb(line.strip())
        else:
          si = SeriesInfo().initImdbInfo(json.loads(line))
        if si != None:
          sis.append(si)
      except Exception,ee:
        self.log(Text.formatException(ee))
    feeder = ImdbFeeder()
    feeder.dirTarget = self.dirTarget
    feeder.withThumb = self.withThumb
    feeder.streamMode= self.streamMode
    feeder.addSeriesInfo(sis,loadInfo)
    return True
  #============================================================================
  # Fetch <items> for imdb ids
  #   Params : imdbIds  = The filter info to filter the items
  #============================================================================
  def loadImdbIdList(self,loadInfo):
    if self.imdbIdList == None:
      return
    sis = []
    for id in self.imdbIdList:
      si = SeriesInfo().initImdb(id)
      if si != None:
        sis.append(si)
    feeder = ImdbFeeder()
    feeder.dirTarget = self.dirTarget
    feeder.withThumb = self.withThumb
    feeder.streamMode= self.streamMode
    feeder.addSeriesInfoAll(sis,loadInfo)
    return True
# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import xbmc
import xbmcaddon
import xbmcgui
import helpers.Text as Text
import helpers.File as File
import json
import os
import time
import codecs
import datetime
import xml.etree.ElementTree as et
import Log
from StringManager            import *
from networks.FileLoader      import *
from Config                   import *
from FilterInfo               import *
from LoadInfo                 import *
from feeders.ImdbFeeder       import *
from feeders.ImdbBundleFeeder import *
from SeriesInfo               import *
from GaTracker                import *
#==============================================================================
# The addon
#==============================================================================
class Addon:
  #============================================================================
  # Create a new addon
  #============================================================================
  def __init__(self, id=None ):
    self.addon   = xbmcaddon.Addon() if id == None else xbmcaddon.Addon(id=id)
    self.name    = Text.xbmcFrom( self.addon.getAddonInfo("name"   ) )
    self.version = Text.xbmcFrom( self.addon.getAddonInfo("version") )
    self.id      = Text.xbmcFrom( self.addon.getAddonInfo("id"     ) )
    self.path    = Text.xbmcFrom( self.addon.getAddonInfo("path"   ) )
    self.data    = Text.xbmcFrom( xbmc.translatePath('special://profile/addon_data/%s' % (self.id)) )
    self.config  = Config(self.addon)
    self.tracker = GaTracker()
    sm.addon     = self.addon
    self.initPaths()
  #============================================================================
  # Run the addon
  #============================================================================
  def run(self):
    self.tracker.trackPage('run')
    dt = self.diffLastUpdate(1)
    items = dt.days * 2
    items = 100 if items >= 100 else items
    self.log(u'fetching {0}'.format(items))
    self.runItems(items)
  #============================================================================
  # Run the addon
  #============================================================================
  def runItems(self,items):
    self.notify( sm.str(sm.seriesStart) )
    feeder = ImdbFeeder()
    loadInfo = self.loadSeries(feeder,items)
    self.notify( sm.str(sm.seriesEnd).format(loadInfo.added, loadInfo.episodes))
  #============================================================================
  # add series
  #============================================================================
  def addSeries(self):
    self.tracker.trackPage('addSeries')
    self.runItems( self.config.getInt("refresh_size") )
  #============================================================================
  # add episodes
  #============================================================================
  def addEpisode(self):
    self.tracker.trackPage('addEpisode')
    self.notify( sm.str(sm.episodeStart) )
    feeder = ImdbFeeder()
    loadInfo =self.loadEpisodes(feeder,0)
    self.notify( sm.str(sm.episodeEnd).format(loadInfo.added, loadInfo.episodes) )
  #============================================================================
  # Run the addon as service
  #============================================================================
  def service(self):
    self.log('Service Start')
    addS = ServiceAction(1, self.addSeries  , self.config)
    addE = ServiceAction(2, self.addEpisode , self.config)
    while (not xbmc.abortRequested):
      try:
        #self.log('addS {0:2} {1:3} {2}, addE {3:2} {4:3} {5}'.format(addS.count, addS.left(), addS.isDone(),addE.count, addE.left(), addE.isDone()))
        if addS.isDone() and addE.isDone():
          break
        addS.run()
        addE.run()
        time.sleep(60)
      except:
        break
    self.log('Service End')
  #============================================================================
  # Run the and fetch number of items as refresh_size
  #============================================================================
  def updateNow(self):
    self.tracker.trackPage('updateNow')
    refreshSize = self.config.getInt("refresh_size")
    self.runItems(refreshSize)
  #============================================================================
  # Load Bundle from source
  #   Params: source - the source directory
  #============================================================================
  def loadBundles(self):
    self.tracker.trackPage('loadBundles')
    self.notify( sm.str(sm.bundlesStart) )
    feeder = ImdbBundleFeeder()
    feeder.source = self.translatePath( self.config.getStr('bundle_source') )
    loadInfo = self.loadSeries(feeder,0)
    self.notify( sm.str(sm.bundlesEnd).format(loadInfo.added, loadInfo.episodes) )
  #============================================================================
  # Load Bundle from source
  #   Params: source - the key for the source
  #============================================================================
  def loadPackage(self,configKey):
    self.tracker.trackPage('loadPackage')
    self.notify( sm.str(sm.packageStart) )
    feeder = ImdbBundleFeeder()
    feeder.cache = self.cache
    feeder.package = self.translatePath( self.config.getStr(configKey) )
    loadInfo = self.loadSeries(feeder,0)
    self.notify( sm.str(sm.packageEnd).format(loadInfo.added, loadInfo.episodes) )
  #============================================================================
  # Load Bundle from source
  #   Params: source - the key for the source
  #============================================================================  
  def loadImdbIdList(self):
    self.tracker.trackPage('loadImdbIdList')
    feeder = ImdbBundleFeeder()
    feeder.cache = self.cache
    feeder.imdbIdList = [ ss.strip() for ss in self.config.getStr('package_text').split(',') ]
    loadInfo = self.loadSeries(feeder,0)
    self.notify( sm.str(sm.packageEnd).format(loadInfo.added, loadInfo.episodes) )
  #============================================================================
  # Load filters
  #============================================================================
  def loadFilters(self):
    return FilterInfo(self.addon)
  #============================================================================
  # Display message dialog
  #   Params : title   = the title text
  #            message = the message text
  #============================================================================
  def message(self,title,message):
    xbmcgui.Dialog().ok( Text.xbmcTo(title), Text.xbmcTo(message) )
  #============================================================================
  # Display notify message
  #   Params : message = the message text
  #============================================================================
  def notify(self,message):
    if self.config.getBool('notify'):
      xbmc.executebuiltin(Text.xbmcTo(u'XBMC.Notification({0},{1},{2},{3})'.format(self.name, message , 5 , os.path.join( self.path ,"icon.png" ))) )
  #============================================================================
  # Init the paths
  #============================================================================
  def initPaths(self):
    self.dirRoot    = self.path
    self.cache      = os.path.join( self.data   , "Cache"   )
    self.dirLogs    = os.path.join( self.data   , "Logs"    )

    File.ensureFolder(self.cache  )
    File.ensureFolder(self.dirLogs)

    FileLoader.dirCache = os.path.join( self.data, "Cache" )

    SeriesInfo.tvdbMoldDir = os.path.join( self.dirRoot   , "html" )
    Log.log = self.log
  #============================================================================
  # Add source directory
  #   Params : name = the name of the source
  #            path = the path of the source
  #============================================================================
  def addSource(self,name,path):
    sources_filename = xbmc.translatePath("special://userdata/sources.xml")
    ndRoot =  None
    if os.path.exists(sources_filename):
      tree = et.parse(sources_filename)
    else:
      root = et.fromstring('<sources> <programs> <default pathversion="1"></default> </programs> <video>    <default pathversion="1"></default> </video> <music>    <default pathversion="1"></default> </music> <pictures> <default pathversion="1"></default> </pictures> <files>    <default pathversion="1"></default> </files> </sources>')
      tree = et.ElementTree(root)
    ndVideo = tree.find("./video")
    for ndSource in ndVideo:
      if ndSource.tag == "source":
        ndName = ndSource.find("name")
        if ndName.text == name:
          return
    ndSource = et.Element("source")
    et.SubElement(ndSource, "name").text = name
    et.SubElement(ndSource, "path").text = path
    ndVideo.append(ndSource)
    tree.write(sources_filename)
  #============================================================================
  # Scan the source
  #   Params : path = the path of the source
  #============================================================================
  def scanSource(self,path=None):
    time.sleep(1)
    while xbmc.getCondVisibility('Library.IsScanning') or xbmc.getCondVisibility('Window.IsActive(10101)'):
      time.sleep(1)
    xbmc.executebuiltin('UpdateLibrary({0})'.format('video'))
  #============================================================================
  # Clean the source
  #   Params : path = the path of the source
  #============================================================================
  def cleanSource(self,path=None):
    time.sleep(1)
    while xbmc.getCondVisibility('Library.IsScanning') or xbmc.getCondVisibility('Window.IsActive(10101)'):
      time.sleep(1)
    xbmc.executebuiltin("CleanLibrary({0})".format('video'))
  #============================================================================
  # log a message
  #   Params : message = The message
  #============================================================================
  def log(self,message, filename="main.log"):
    now = datetime.datetime.now()
    try :
      logFile = os.path.join(self.dirLogs,filename)
      with codecs.open(logFile, mode='a+') as ff:
        ff.write( '{2:02}/{1:02}|{3:02}:{4:02}:{5:02} : {6}'.format(
          now.year,
          now.month,
          now.day,
          now.hour,
          now.minute,
          now.second,
          message
        ))
        ff.write('\n')
    except:
      pass
  #============================================================================
  # Translate path special places
  #   Params: path - the path
  #   Return: The translated path
  #============================================================================
  def translatePath(self,path):
    path = path.replace('{home}',self.path)
    path = path.replace('{data}',self.data)
    return path
  #============================================================================
  # Save current time as last update time
  #============================================================================
  def saveLastUpdate(self,id):
    self.config.setStr( 'last_update{0}'.format(id), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
  #============================================================================
  # Save current time as last update time
  #============================================================================
  def diffLastUpdate(self,id):
    date = self.config.getStr('last_update{0}'.format(id))
    lastUpdate = datetime.datetime(2000,1,1,0,0,0)
    try:
      lastUpdate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except:
      pass
    return datetime.datetime.now() - lastUpdate
  #============================================================================
  # Clean the library
  #============================================================================
  def cleanLibrary(self):
    File.delFiles(self.library)
    self.cleanSource()
    self.notify( sm.str(sm.cleanLibrary) )
  #============================================================================
  # Clean the cache
  #============================================================================
  def cleanCache(self):
    File.delFiles(self.cache)
    self.notify( sm.str(sm.cleanCache) )
  #============================================================================
  # Clean the logs
  #============================================================================
  def cleanLogs(self):
    File.delFiles(self.dirLogs)
    self.notify( sm.str(sm.cleanLogs) )
  #============================================================================
  # library
  #============================================================================
  @property
  def library(self):
    library = self.config.getStr('library')
    if library == '':
      library = os.path.join( self.data   , "Library" )
    SeriesInfo.tvdbDataDir = os.path.join( library   , ".tvdb" )
    SeriesInfo.tvdbHtmlDir = os.path.join( library   , ".html" )

    File.ensureFolder(library)
    File.ensureFolder(SeriesInfo.tvdbDataDir)
    File.ensureFolder(SeriesInfo.tvdbHtmlDir)
    return library
  #============================================================================
  def loadSeries(self,feeder,items):
    loadInfo = LoadInfo( FilterInfo(self.config) , items )
    self.addSource(self.name,self.library)
    feeder.withThumb = self.config.getBool('with_thumb')
    feeder.streamMode= self.config.getInt('stream_mode')
    feeder.dirTarget = self.library
    feeder.addSeries(loadInfo)
    self.scanSource(self.library)
    self.saveLastUpdate(1)
    return loadInfo
  #============================================================================
  def loadEpisodes(self,feeder,items):
    loadInfo = LoadInfo(FilterInfo(self.config) , items)
    self.addSource(self.name,self.library)
    feeder.withThumb = self.config.getBool('with_thumb')
    feeder.streamMode= self.config.getInt('stream_mode')
    feeder.dirTarget = self.library
    feeder.addEpisode(loadInfo)
    self.scanSource(self.library)
    self.saveLastUpdate(2)
    return loadInfo
  #============================================================================

#==============================================================================
# The service action
#==============================================================================
class ServiceAction:
  def __init__(self,id,action,config):
    self.modeNone = 0
    self.modeOnce = 1
    self.id     = id
    self.count  = 0
    self.delay  = 0
    self.start  = time.time()
    self.action = action
    self.config = config

  def run(self):
    if self.count == 0:
      self.delay = self.findDelayFirst()
    else:
      self.delay = self.findDelay()
      if self.delay == 0:
        return
    diff = time.time() - self.start
    if diff >= self.delay:
      self.action()
      self.start  = time.time()
      self.count += 1

  def isDone(self):
    return self.isMode(self.modeNone) or ( self.isMode(self.modeOnce) and self.count >= 1 )

  def findDelayFirst(self):
    return self.config.getInt('refresh_first{0}'.format(self.id)) * 60

  def findDelay(self):
    ii = self.config.getInt('refresh_mode{0}'.format(self.id))
    return ServiceAction.delay[ii] if (ii >= 0 and ii < len(ServiceAction.delay)) else 0

  def isMode(self,mode):
    return self.config.getInt('refresh_mode{0}'.format(self.id)) == mode

  def left(self):
    dd = self.delay - ( time.time() - self.start)
    return int(dd) if dd >= 0 else 0

  delay = [
    0                , #1
    0                , #2
    1 * 24 * 60 * 60 , #3
    2 * 24 * 60 * 60 , #4
    3 * 24 * 60 * 60 , #5
    7 * 24 * 60 * 60 , #6
         3 * 60 * 60 , #7   
  ]

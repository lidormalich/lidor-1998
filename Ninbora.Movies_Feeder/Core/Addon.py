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
from GaTracker                import *
from LoadInfo                 import *
from feeders.HebsubsFeeder    import *
from feeders.ImdbBundleFeeder import *
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
    self.data    = xbmc.translatePath('special://profile/addon_data/%s' % (self.id))
    self.config  = Config(self.addon)
    self.tracker = GaTracker()
    sm.addon     = self.addon
    self.initPaths()
  #============================================================================
  # Run the addon
  #============================================================================
  def run(self):
    self.tracker.trackPage('run')
    lastUpdate = self.config.getStr('last_update')
    dt = self.diffLastUpdate()
    items = dt.days * 2
    items =  32 if items <= 32  else items
    items = 320 if items >= 320 else items
    self.log("fetching {0}".format(items))
    self.runItems(items)
  #============================================================================
  # Run the addon
  #============================================================================
  def runItems(self,items):
    self.notify( sm.str(sm.refreshStart) )
    feeder = HebsubsFeeder()
    loadInfo = self.load( feeder , items)
    self.notify( sm.str(sm.refreshEnd).format(loadInfo.added))
  #============================================================================
  # Run the addon as service
  #============================================================================
  def service(self):
    def isMode(mode):
      return self.config.getInt('refresh_mode') == mode
    maxTime = [
           6 * 60 * 60, #0
          12 * 60 * 60, #1
      1 * 24 * 60 * 60, #2
      2 * 24 * 60 * 60, #3
      3 * 24 * 60 * 60, #4
    ]
    modeNone = 0
    modeOnce = 1
    modeMany = 2

    self.log('Service Start')
    if isMode(modeNone):
      self.log('Service End : Refresh None')
      return

    maxDelay = self.config.getInt('refresh_first') * 60
    if maxDelay > 0 :
      start = time.time()
      while True:
        time.sleep(60)
        startDelay = time.time() - start
        if startDelay > maxDelay:
          break
        #self.log('WaitFirst {0}'.format(startDelay))


    while (not xbmc.abortRequested):
      try:
        self.tracker.trackPage('refresh')
        self.run()
        if isMode(modeOnce):
          self.log('Service End : Refresh Once')
          return
      except:
        pass
      lastRun = time.time()
      while True:
        time.sleep(60)
        iTime = self.config.getInt('refresh_interval')
        if xbmc.abortRequested or iTime >= len(maxTime) :
          break
        passRun = time.time() - lastRun
        if passRun > maxTime[iTime]:
          break
        #self.log('WaitOther {0}'.format(passRun))
  #============================================================================
  # Run the and fetch number of items as refresh_size
  #============================================================================
  def updateNow(self):
    self.tracker.trackPage('updateNow')
    iRefreshSize = self.config.getInt("refresh_size")
    if iRefreshSize == 0:
      self.runItems(160)
    if iRefreshSize == 1:
      self.runItems(320)
    if iRefreshSize == 2:
      self.run()
  #============================================================================
  # Load Bundle from source
  #   Params: source - the source directory
  #============================================================================
  def loadBundles(self):
    self.tracker.trackPage('loadBundle')
    self.notify( sm.str(sm.bundlesStart) )
    feeder = ImdbBundleFeeder()
    feeder.source = self.translatePath( self.config.getStr('bundle_source') )
    loadInfo = self.load(feeder,0)
    self.notify( sm.str(sm.bundlesEnd).format(loadInfo.added) )

  def loadPackage(self,configKey):
    self.tracker.trackPage('loadPackage')
    self.notify( sm.str(sm.packageStart) )
    feeder = ImdbBundleFeeder()
    feeder.cache = self.cache
    feeder.package = self.translatePath( self.config.getStr(configKey) )
    loadInfo = self.load(feeder,0)
    self.notify( sm.str(sm.packageEnd).format(loadInfo.added) )
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
    self.dirSource  = os.path.join( self.dirRoot, 'Feeder'  )
    self.cache      = os.path.join( self.data   , "Cache"   )
    self.dirLogs    = os.path.join( self.data   , "Logs"    )
    File.ensureFolder(self.cache  )
    File.ensureFolder(self.dirLogs)
    Log.log = self.log
    FileLoader.dirCache = os.path.join( self.data, "Cache" )
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
  def saveLastUpdate(self):
    self.config.setStr( 'last_update', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') )
  #============================================================================
  # Save current time as last update time
  #============================================================================
  def diffLastUpdate(self):
    date = self.config.getStr('last_update')
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
    File.ensureFolder(library)
    return library
  #============================================================================
  #
  #============================================================================
  def load(self, feeder, items):
    loadInfo = LoadInfo( FilterInfo(self.config) , items )
    self.addSource(self.name,self.library)
    feeder.withThumb = self.config.getBool('with_thumb')
    feeder.streamMode= self.config.getInt('stream_mode')
    feeder.dirTarget = self.library
    feeder.load(loadInfo)
    self.scanSource(self.library)
    self.saveLastUpdate()
    return loadInfo
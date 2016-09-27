# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import ftplib
import os
import os.path
import time
import shutil
import socket
import codecs
import urllib2
import helpers.Text as Text
#==============================================================================
# How should files be cached ?
#==============================================================================
class Cache:
  Disabled = 0
  Enabled  = 1
  InCache  = 2

#==============================================================================
# FileLoader handles downloading a file to disk.
#==============================================================================
class FileLoader:
  #============================================================================
  # Create a new FileLoader
  #============================================================================
  def __init__(self):
    self.onDownloading = None
  #============================================================================
  # Downloads a file located on source
  #   Params : source      = the url  of the source file
  #            target      = the path of the target file
  #            contentType = the content type of the file
  #            timeout     = timeout for the operation
  #            retries     = number of retries
  #============================================================================
  def loadFile(self, source, target='', timeout=0, proxy=Cache.Enabled, contentType= '', retries=2, loadData = True , maxCache = 0 ):
    self.source = source
    self.state  = FileLoader.idFail
    self.data   = ''
    self.target = ''
    if   source.startswith('http'):
      self.loadRemote(source, target, timeout, proxy, contentType, retries , loadData , maxCache)
    elif source.startswith('ftp' ):
      self.loadRemote(source, target, timeout, proxy, contentType, retries , loadData , maxCache)
    elif source != '':
      self.loadLocals(source, target, timeout, proxy, contentType, retries , loadData )
  #============================================================================
  # Downloads a file located on source
  #   Params : source      = the url  of the source file
  #            target      = the path of the target file
  #            contentType = the content type of the file
  #            timeout     = timeout for the operation
  #            retries     = number of retries
  #============================================================================
  def loadRemote(self, source, target='', timeout=0, proxy=Cache.Enabled, contentType= '', retries=0, loadData = True, maxCache = 0 ):
    target = self.findCachedName(source,target,True)
    inCache = False
    if os.path.exists(target):
      cacheTime = time.time() - os.path.getmtime(target)
      if maxCache == 0 or cacheTime >= maxCache :
        os.remove(target)
      else:
        inCache = True
    if (proxy == Cache.InCache or proxy == Cache.Enabled) and inCache:
      self.log(u'Find Cache: <{1}> as <{0}>'.format(source,target))
      self.state  = FileLoader.idOk
      self.target = target
    elif proxy == Cache.InCache and inCache == False:
      self.log(u'Miss Cache: <{1}> as <{0}>'.format(source,target))
      self.state  = FileLoader.idFail
      return
    elif   source.startswith('http'):
      self.loadHTTP(source, target, timeout, proxy, contentType, retries)
    elif source.startswith('ftp' ):
      self.loadFTP( source, target, timeout, proxy, contentType, retries)
    if loadData:
      self.loadData()
  #============================================================================
  # Downloads a file located on source
  #   Params : source      = the url  of the source file
  #            target      = the path of the target file
  #            contentType = the content type of the file
  #            timeout     = timeout for the operation
  #            retries     = number of retries
  #============================================================================
  def loadHTTP(self, source, target='', timeout=0, proxy=Cache.Enabled, contentType= '', retries=0):
    self.setNetworkTimeout(timeout)
    self.state  = FileLoader.idFail
    counter = 0
    source0 = source
    if isinstance(source,unicode):
      source = source.encode('utf8')

    while (counter <= retries) and (self.state != 0):
      if counter >= 1:
        self.log(u"Retry {0} : {1}".format(counter, source))
        time.sleep(1)
      counter += 1
      try:
        headers = { 'User-Agent' : 'Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)' }
        req = urllib2.Request(source, None, headers)
        ff = urllib2.urlopen(req)
        headers = ff.info()
        if contentType != '' and headers['Content-Type'].find(contentType)  == -1:
          self.setNetworkTimeout(timeout)
          self.state = FileLoader.idFail
          break
        if ff.code != 200 and ff.code >= 400:
          continue
        with open(target, "wb") as fl:
          if ff.headers.has_key('Content-Length') == False:
            self.data = ff.read()
            fl.write(self.data)
          else:
            fileSize = int(ff.headers['Content-Length'])
            saveData = False
            if (fileSize > 0):
              lastTime = time.time()
              downSize = lastSize = downSpeed = 0
              while (downSize < fileSize):
                chunk = 100 * 1024
                if (downSize + chunk) > fileSize:
                  chunk = fileSize - downSize
                data = ff.read(chunk)
                fl.write(data)
                if saveData:
                  self.data += data
                downSize += chunk
                if self.onDownloading:
                  percent = 100 * downSize / fileSize
                  deltaTime = time.time() - lastTime
                  if deltaTime >= 1:
                    downSpeed = (downSize - lastSize) / deltaTime
                    lastTime, lastSize = time.time() , downSize
                    self.onDownloading(fileSize,downSize, downSpeed)
        ff.close()
        self.target = target
        self.state = FileLoader.idOk
      except IOError, ee:
        if hasattr(ee, 'reason'):
          self.log(u'Fail download <{0}>. Reason: {0}'.format(source0, str(ee.reason)))
        elif hasattr(ee, 'code'):
          self.log(u'Fail download <{0}>. The server could not fulfill the request. Error code: {0}'.format(source0,str(ee.code)))
        self.state = FileLoader.idFail
      except Exception, ee:
        self.log(u'Fail download <{0}>'.format(source0))
        self.state = FileLoader.idFail
        self.logException(ee)
    if self.state != FileLoader.idOk and os.path.exists(target):
      os.remove(target)
    self.setNetworkTimeout()
  #============================================================================
  # Downloads a file located on source
  #   Params : source      = the url  of the source file
  #            target      = the path of the target file
  #            contentType = the content type of the file
  #            timeout     = timeout for the operation
  #            retries     = number of retries
  #============================================================================
  def loadFTP(self, source, target='', timeout=0, proxy=Cache.Enabled, contentType= '', retries=0):
    self.state = FileLoader.idFail
    urlParser = UrlFtpParser(source)
    try:
      self.ftp = ftplib.FTP()
      self.ftp.connect(urlParser.host,urlParser.port)
      self.log(u'**** Connected to host "{0}"'.format(urlParser.host))
    except (socket.error, socket.gaierror), e:
      self.log(u'ERR: cannot reach "{0}"'.format(urlParser.host))
      return
    try:
      if urlParser.username != '':
        self.ftp.login(urlParser.username, urlParser.password)
        self.log(u'**** Logged in as {0}', urlParser.username)
      else:
        self.ftp.login()
        self.log(u'**** Logged in as "anonymous"')
    except ftplib.error_perm:
      self.log(u'ERR: cannot login')
      self.ftp.quit()
      return
    try:
      self.ftp.cwd(urlParser.path)
      self.log(u'**** Changed to "{0}" folder'.format(urlParser.path))
    except ftplib.error_perm:
      self.log(u'ERR: cannot CD to "{0}"'.format(urlParser.path))
      self.ftp.quit()
      return
    self.bytes = 0
    try:
      self.ftp.retrbinary('RETR {0}'.format(file), open(target, 'wb').write)
      self.target = target
      self.size = self.ftp.size(self.target)
      self.size_MB = float(self.size) / (1024 * 1024)
      self.log(u'**** Downloaded "{0}" to CWD'.format(file))
      self.ftp.quit()
      self.state = FileLoader.idOk
    except ftplib.error_perm:
      self.log(u'ERR: cannot read file "{0}"'.format(file))
      os.unlink(self.file)
      self.ftp.quit()
      return
  #============================================================================
  # Downloads a file located on source
  #   Params : source      = the url  of the source file
  #            target      = the path of the target file
  #            contentType = the content type of the file
  #            timeout     = timeout for the operation
  #            retries     = number of retries
  #============================================================================
  def loadLocals(self, source, target='', timeout=0, proxy=Cache.Enabled, contentType= '', retries=0, loadData = True):
    if (source[1] == ':') or (source[0] == '/'): #absolute (local) path
      self.target = source
      self.state = FileLoader.idOk
    else:
      self.target = os.path.join("./", source)
      self.state = FileLoader.idOk
    target = self.findCachedName(source,target,proxy != Cache.Disabled)
    if loadData:
      self.loadData()
  #============================================================================
  # find the cached name of the file
  #   Params : source   = the source file url
  #            target   = the target file path
  #            isCached = whether the the target is cached
  #============================================================================
  def findCachedName(self, source, target, isCached):
    sum = Text.hash(source,12) if isCached else '000000000000'
    if target == '':
      return os.path.join( FileLoader.dirCache , 'file_{0}.bin'.format(sum) )
    if target.startswith('@'):
      return target[1:]
    extIndex = target.rfind('.')
    if extIndex != -1:
      return os.path.join( FileLoader.dirCache , u'{0}_{1}{2}'.format(target[:extIndex],sum,target[extIndex:]) )
    return os.path.join( FileLoader.dirCache , '{0}_{1}{2}'.format(target, sum,'.bin') )
  #============================================================================
  # load the data stored in the target to memory
  #   Return : The data stored in the target
  #============================================================================
  def loadData(self):
    if self.state == FileLoader.idOk:
      try:
        with codecs.open(self.target,encoding='utf8',errors='ignore') as ff:
          self.data = ff.read()
      except Exception,ee:
        pass
  #============================================================================
  @staticmethod
  def load(source, target='', timeout=0, proxy=Cache.Enabled, contentType= '', retries=0, onDownloading = None, params = {} , loadData = True, maxCache=0):
    fileLoader = FileLoader()
    fileLoader.onDownloading = onDownloading
    if len(params) > 0:
      source = Text.buildUrl(source,params)
    fileLoader.loadFile(source, target, timeout, proxy, contentType, retries, loadData, maxCache)
    return fileLoader
  #============================================================================
  # Log message
  #   Params : msg = the massage to log
  #============================================================================
  def log(self,msg):
    pass # print u'{0} : {1}'.format( "FileLoader" , msg )
  #============================================================================
  def logException(self,ee):
    pass # print ee
  #============================================================================
  # Set the timeout to network operations
  #   Params : timeout = the timeout in seconds
  #============================================================================
  def setNetworkTimeout(self,timeout = 60):
    if timeout != 0:
      socket.setdefaulttimeout(timeout)
  #============================================================================
  idOk     =  0
  idFail   = -1
  dirCache = ''
#============================================================================

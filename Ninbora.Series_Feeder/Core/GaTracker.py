import xbmc
import sys
import traceback
import Log

import pyga.requests as ga

class GaTracker:
  def __init__(self):
    self.tracker = ga.Tracker('UA-37624034-2', 'Ninbora.Add' , ga.Config())
    self.session = ga.Session()
    self.visitor = ga.Visitor()
    self.visitor.user_agent = self.findUserAgent()
    self.visitor.locale     = self.findLangeuage()
  #----------------------------------------------------------------------------
  def trackPage(self,path):
    try:
      self.tracker.track_pageview(ga.Page('/Series_Feeder/{0}'.format(path)), self.session, self.visitor)
    except Exception, ee:
      Log.log(traceback.format_exc())
  #----------------------------------------------------------------------------
  def trackEvent(self,*args, **kwargs):
    try:
      self.tracker.track_event(ga.Event(*args, **kwargs), self.session, self.visitor)
    except Exception, ee:
      Log.log(traceback.format_exc())
  #----------------------------------------------------------------------------
  def findLangeuage(self):
    return xbmc.getLanguage()
  #----------------------------------------------------------------------------
  def findPlatform(self):
    return xbmc.getInfoLabel('System.KernelVersion')
  #----------------------------------------------------------------------------
  def findVersion(self):
    return xbmc.getInfoLabel("System.BuildVersion").split(" ")[0]
  #----------------------------------------------------------------------------
  def findUserAgent(self):
    return "XBMC_{0} | {1}".format( self.findVersion() , self.findPlatform() )

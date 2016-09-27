# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

def loadAddon(id = None):
  import os.path
  import sys
  import xbmcaddon
    
  addon = xbmcaddon.Addon() if id == None else xbmcaddon.Addon(id=id)
  dirRoot = addon.getAddonInfo('path').decode('utf8')    
  sys.path.insert(0, os.path.join( dirRoot , 'Core' ))
  import Addon
  return Addon.Addon(id)

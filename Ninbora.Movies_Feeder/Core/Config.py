# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

#============================================================================
# Persistent Key-Value store. Supported value types : string, integrer, boolean
#============================================================================
class Config:
  #============================================================================
  # Create a new settings
  #============================================================================
  def __init__(self,addon):
    self.addon  = addon
  #============================================================================
  # Find the value of <name>
  #   Params : name - The name of the setting
  #   Return : The value of <name>
  #============================================================================
  def getStr(self,name):
    return self.addon.getSetting(name)
  #============================================================================
  # Store the <value> on setting <name>
  #   Params : name  = The name of the setting
  #            value = The value
  #============================================================================
  def setStr(self,name,value):
    self.addon.setSetting(name,value)
  #============================================================================
  # Find the value of bool setting <name>
  #   Params : name = The name of the setting
  #   Return : The value of bool setting <name>
  #============================================================================
  def getBool(self,name):
    return self.addon.getSetting(name) == 'true'
  #============================================================================
  # Store the value on bool setting <name>
  #   Params : name = The name of the setting
  #            value =
  #   Return : The value of bool setting <name>
  #============================================================================
  def setBool(self,name,value):
    if  value:
      self.addon.setSetting(name,'true')
    else:
      self.addon.setSetting(name,'false')
  #============================================================================
  # Find the value of int setting <name>
  #   Params : name = The name of the setting
  #   Return : The value of int setting <name>
  #============================================================================
  def getInt(self,name):
    return int(self.addon.getSetting(name))
  #============================================================================
  # Store the value on int setting <name>
  #   Params : name = The name of the setting
  #            value = The value
  #   Return : The value of int setting <name>
  #============================================================================
  def setInt(self,name,value):
    return self.addon.setSetting(name,str(value))
  #============================================================================
  # Find the value of float setting <name>
  #   Params : name = The name of the setting
  #   Return : The value of int setting <name>
  #============================================================================
  def getFloat(self,name):
    return float(self.addon.getSetting(name))
  #============================================================================
  # Store the value on float setting <name>
  #   Params : name = The name of the setting
  #            value = The value
  #   Return : The value of int setting <name>
  #============================================================================
  def setFloat(self,name,value):
    return self.addon.setSetting(name,str(value))
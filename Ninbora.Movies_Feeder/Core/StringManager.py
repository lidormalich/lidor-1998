# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

class StringeManager:
  def __init__(self):
    self.addon = None
    # info
    self.refreshStart =  1001 # Refresh Started
    self.refreshEnd   =  1002 # Added {0} . Refresh Ended
    self.bundlesStart =  1003 # Load Bundles Start
    self.bundlesEnd   =  1004 # Added {0} . Load Bundles Ended
    self.packageStart =  1005 # Load Package Started
    self.packageEnd   =  1006 # Added {0} . Load Package Ended
    self.cleanLibrary =  1007 # Clean Library
    self.cleanCache   =  1008 # Clean Cache
    self.cleanLogs    =  1009 # Clean Logs

  def str(self,stringId):
    ss = self.addon.getLocalizedString(stringId)
    ss = ss.replace("\\n",'\n')
    return ss

sm = StringeManager()

# Convert to strings.xml :
#   Replace ".*?=[ ]*(\d+) # (.*)" with "  <string id="\1">\2</string>"
#   Replace ".*?#[ ]+(.*)"         with "  <!-- \1 -->"

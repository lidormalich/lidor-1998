# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import shared
import sys
addon = shared.loadAddon('Ninbora.Series_Feeder')

if len(sys.argv) >= 1:
  if sys.argv[1] == 'addSeries' :
    addon.addSeries()
  if sys.argv[1] == 'addEpisode' :
    addon.addEpisode()
  if sys.argv[1] == 'loadBundles' :
    addon.loadBundles()
  if sys.argv[1] == 'loadPackageFile' :
    addon.loadPackage('package_file')
  if sys.argv[1] == 'loadPackageLink' :
    addon.loadPackage('package_link')
  if sys.argv[1] == 'loadImdbIdList' :
    addon.loadImdbIdList()
  if sys.argv[1] == 'cleanLibrary':
    addon.cleanLibrary()
  if sys.argv[1] == 'cleanCache' :
    addon.cleanCache()
  if sys.argv[1] == 'cleanLogs' :
    addon.cleanLogs()
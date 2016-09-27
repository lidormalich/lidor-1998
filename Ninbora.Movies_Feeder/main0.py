# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import sys
import os

def addCore(dirRoot):
  sys.path.insert(0, os.path.join( dirRoot , 'Core' ))

dirRoot = "."

addCore(dirRoot)

from feeders.ImdbBundleFeeder import *
from FilterInfo import *
FileLoader.dirCache = os.path.join( dirRoot , 'Cache' )
feeder = ImdbBundleFeeder()
fi = FilterInfo()
feeder.load(fi,320)
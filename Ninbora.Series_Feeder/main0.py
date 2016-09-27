# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import sys
import os


def addCore(dirRoot):
  sys.path.insert(0, os.path.join( dirRoot , 'Core' ))

dirRoot = "."
addCore(dirRoot)

from feeders.ImdbFeeder import *
from FilterInfo import *
from LoadInfo import *

FileLoader.dirCache = os.path.join( dirRoot , 'Cache' )
feeder = ImdbFeeder()

import xml.etree.ElementTree as et

fi = FilterInfo()
fi.genre[0] = False
fi.genre[1] = True
kk = LoadInfo( fi , 100 )
feeder.update(kk)


# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import urllib
import hashlib
import HTMLParser
import re
#==============================================================================
# Convert from xbmc encoding to unicode
#   Params : ss = string in xbmc encoding
#   Return : The string in unicode encoding
#==============================================================================
def xbmcTo(ss):
  if isinstance(ss,unicode):
    return ss.encode('utf8')
  return ss
#==============================================================================
# Convert from unicode to xbmc encoding
#   Params : ss = the string in unicode encoding
#   Return : The string in xbmc encoding
#==============================================================================
def xbmcFrom(ss):
  return ss.decode('utf8')
#==============================================================================
# hash <ss>
#   Params : ss   = the string to hash
#            size = the hash size in characters
#   Return : The hash value
#==============================================================================
def hash(ss, size = 6):
  mm = hashlib.md5()
  if isinstance(ss,unicode):
    ss = ss.encode('utf8')
  mm.update(ss)
  return mm.hexdigest()[:size]
#================================================================================
# Build a url with parameters
#   Params : url    = the base url
#            params = dictionary of key/value pairs
#================================================================================
def buildUrl(url, params):
  def urlencode_unicode(params):
    query = ''
    for xx in params:
      s1 = xx
      if not isinstance(s1,unicode):
        s1 = str(s1).decode('utf8');
      s2 = params[xx]
      if not isinstance(s2,unicode):
        s2 = str(s2).decode('utf8');
      if ( query != '' ):
        query += '&';
      query += urllib.quote_plus(s1.encode('utf8'))
      query += '=';
      query += urllib.quote_plus(s2.encode('utf8'))
    return query
  return "{0}?{1}".format(url.encode('utf8'), urlencode_unicode(params))
#================================================================================
# Unescape html entities
#   Params : ss = the string to escape
#================================================================================
def unescapeHtml(ss):
  if not isinstance(ss,unicode):
    ss = str(ss).decode('utf8');
  ss = re.sub(u'&#x(\d+);' , lambda mm : unichr(int(mm.group(1),16))  ,ss)
  ss = re.sub(u'&#(\d+);'  , lambda mm : unichr(int(mm.group(1),10))  ,ss)
  ss = re.sub(u'%(\d+)'    , lambda mm : unichr(int(mm.group(1),16))  ,ss)
  return ss
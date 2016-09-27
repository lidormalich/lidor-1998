# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import Log
#============================================================================
# Filter items to filter
#============================================================================
class FilterInfo:
  #============================================================================
  # Load all the filter items from <config>
  #    Params : config = The key/value data store
  #============================================================================
  def __init__(self,config = None):
    self.config = config
    if self.config != None:
      self.genre  = [ (self.config.getBool( "{0}_{1:02}".format("genre"  , ii ))) for ii in range( 0 , len(FGenre.names) ) ]
      self.yearAbove   = self.config.getInt("year_above")
      self.yearBelow   = self.config.getInt("year_below")
      self.ratingAbove = self.config.getFloat("rating_above")
      self.ratingBelow = self.config.getFloat("rating_below")
    else:
      self.rating = [ True for ii in range( 0 , len(FRating.ids ) ) ]
      self.yearAbove   = 1900
      self.yearBelow   = 2020
      self.ratingAbove = 0
      self.ratingBelow = 10
  #============================================================================
  # Whether the <year> is valid for the current filter values
  #   Params : year = the year to check
  #============================================================================
  def isValidYear(self,year):
    return year >= self.yearAbove and year <= self.yearBelow
  #============================================================================
  # Whether the <rating> is valid for the current filter items
  #   Params : rating = the rating to check
  #============================================================================
  def isValidRating(self,rating):
    return rating >= self.ratingAbove and rating <= self.ratingBelow
  #============================================================================
  # Whether the <genres> is valid for the current filter items
  #   Params : genres = list of genres to check if valid
  #============================================================================
  def isValidGenre(self,genres):
    if self.genre[0]:
      return True
    for ii in range(1, len( FGenre.names ) ):
      if self.genre[ii]:
        try:
          genres.index( FGenre.names[ii] )
          return True
        except:
          pass
    return False
  #============================================================================
  # Whether the <countries> is valid for the current filter items
  #   Params : countries = list of countries to check if valid
  #============================================================================
  def isValidCountry(self,countries):
    try:
      countries.index('Israel')
      return False
    except:
      return True
#============================================================================
# Genre filter items
#============================================================================
class FGenre:
  names = [
    u"Any"         , #00
    u"Action"      , #01
    u"Adventure"   , #02
    u"Comedy"      , #03
    u"Drama"       , #04
    u"Horror"      , #05
    u"Thriller"    , #06
    u"Animation"   , #07
    u"Western"     , #08
    u"War"         , #09
    u"Romance"     , #10
    u"Sci-Fi"      , #11
    u"Mystery"     , #12
    u"Crime"       , #13
    u"History"     , #14
    u"Family"      , #15
    u"Fantasy"     , #16
    u"Documentary" , #17
    u"Biography"   , #18
    u"Music"       , #19
    u"Musical"     , #20
    u"Adult"       , #21
    u"News"        , #22
    u"Short"       , #23
    u"Sport"       , #24
    u"Film-Noir"     #25
  ]



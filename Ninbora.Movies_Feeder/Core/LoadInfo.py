# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

#==============================================================================
#
#==============================================================================
class LoadInfo:
  #============================================================================
  # Create a new BundleLoadInfo
  #   Params: filter = filter info
  #           maxFetched = The maximum number of items to fetch
  #============================================================================
  def __init__(self,filter,maxFetched):
    self.filter = filter
    self.maxFetched = maxFetched
    self.fetched = 0
    self.added   = 0
  #============================================================================
  # Find Whether the maximum item were fetched
  #============================================================================    
  def isFetchAll(self):
    return self.maxFetched != 0 and self.fetched >= self.maxFetched
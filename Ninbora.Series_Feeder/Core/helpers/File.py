# Copyright (C) 2014 Ninbora [admin@ninbora.com]
# Licensed under MIT license [http://opensource.org/licenses/MIT]

import shutil
import os
import os.path
#============================================================================
# create <folder> if does not exist yet
#   Params: folder = the folder to
#   Return: True if the folder exist or was created successfully 
#============================================================================
def ensureFolder(folder):
  if not os.path.exists(folder):
    try:
      os.makedirs(folder)
    except:
      return False
  return True
#============================================================================
# Clean the name for invalid characters
#   Params: filename = the filename to clean
#   Return: The filename without invalid characters
#============================================================================
def cleanName(filename):
  filename = filename.replace("'","")
  filename = filename.replace('"',"")
  filename = filename.replace("?","")
  filename = filename.replace("<","")
  filename = filename.replace(">","")
  filename = filename.replace("*","")
  filename = filename.replace("|","")
  filename = filename.replace(":","")
  filename = filename.replace("!","")
  filename = filename.replace("\\","")
  filename = filename.replace("/","_")
  filename = filename.replace("\t","")
  return filename

#==============================================================================
# Deletes files in a <folder> and its sub-folders.
#   Params : folder    = path to local folder
#            extension = extension of the files to remove. if empty all files will be removed.
#            prefix    = prefix of the files to remove. if empty all files will be removed.
#==============================================================================
def delFiles(folder, extension = '', prefix = ''):
  if (extension != '' ) :
    extension = '.' + extension
  try:
    for root, dirs, files in os.walk(folder, topdown=False):
      for name in files:
        filename = os.path.join(root, name)
        if extension == '' and prefix == '':
          os.remove(filename)
        elif extension != '' and filename.endswith(extension):
          os.remove(filename)
        elif prefix != '' and name.startswith(prefix):
          os.remove(filename)
      for name in dirs:
        dir = os.path.join(root, name)
        os.rmdir(dir)
  except IOError:
    return
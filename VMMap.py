#!/usr/bin/python

import os
import sys
from lconfig import HMEDIR
sys.path.append(HMEDIR)
sys.path.append(HMEDIR + "/vidmgr")
import marshal

import TivoConfig

import Config
from Config import TYPE_VIDFILE, TYPE_VIDDIR, TYPE_DVDDIR, TYPE_VIDSHARE, TYPE_DVDSHARE
from VideoCache import VideoCache

import getopt 

verbose = False

try:
	opts, args = getopt.getopt(sys.argv[1:], "v", ["verbose"])
	for o, a in opts:
		if o == "-v":
			verbose = True
			
except getopt.GetoptError, err:
	pass

CACHEFILE = "VMMap.dat" 
vmap = {}

sharemap = {}
counts = {}
tc = TivoConfig.TivoConfig().getShares()
for tv in tc:
	sharemap[tv["name"]] = tv["path"]
	counts[tv["name"]] = 0

def getThumb(opts, dn, name, isDVD):
	names = []
	names.append(os.path.join(dn, name + '.jpg'))
	names.append(os.path.join(dn, '.meta', name + '.jpg'))
	names.append(os.path.join(dn, opts['thumbfolderfn']))
	names.append(os.path.join(dn, '.meta', opts['thumbfolderfn']))
	if isDVD: 
		names.append(os.path.join(dn, 'default.jpg'))
		names.append(os.path.join(dn, '.meta', 'default.jpg'))
			
	for tfn in names:
		try:
			os.path.getmtime(tfn)
			return tfn
		except os.error:
			# file does not exist
			pass
	return None


def Descend(node, opts, parent, path):
	lmap = []
	lopts = opts.copy()
	
	p = None
	try:
		t = node.getObjType()
		if t in [ TYPE_VIDSHARE, TYPE_DVDSHARE ]:
			d = node.getVideoDir()
			p = d.getFullPath()
		elif t in [ TYPE_VIDDIR, TYPE_DVDDIR ]:
			p = node.getFullPath()
	except:
		p = None
		
	dopt = lopts['dispopt']
	canDelete = lopts['deleteallowed']
	if p != None:
		Config.addLocalOpts(lopts, p, "")
		dopt = lopts['dispopt']
		canDelete = lopts['deleteallowed']
	
	if parent != None:
		lmap.append({'type': 'PARENT', 'link': parent})
		
	listSize = len(node)
	for i in range(listSize):
		item = node.getItem(i)
		if item.getObjType() == TYPE_VIDFILE:
			vtype = 'VFILE'
			if item.isDVDVideo():
				vtype = "DVDFILE"
			va = {'type': vtype, 'text': item.formatDisplayText(dopt), 'path': item.getFullPath(), 'meta': item.getMeta(), 'candelete': canDelete}
			fn = getThumb(lopts, item.getPath(), item.getFileName(), item.isDVDVideo())
			if fn:
				shr = item.getShare()
				if shr:
					pfx = sharemap[shr]
					if fn.startswith(pfx):
						va["image"] =  '/' + shr.replace(' ', '_') + fn[len(pfx):]
						counts[shr] += 1
			lmap.append(va)
	
		else:
			n = item.formatDisplayText(dopt)
			lmap.append({'type': 'FOLDER', 'text': n, 'link': "%s/%s" % (path, n)})
			
	vmap[path] = lmap
				
	for i in range(listSize):
		item = node.getItem(i)
		if item.getObjType() != TYPE_VIDFILE:
			n = item.formatDisplayText(dopt)
			newpath = path + '/' + n
			Descend(item, lopts, path, newpath)


config = Config.Config()
opts = config.load()
cp = config.getConfigParser()
					
vc = VideoCache(opts, cp)
		
rootNode = vc.load()

Descend(rootNode, opts, None, "")

try:
	f = open(CACHEFILE, 'wb')
except:
	print "Error opening cache file for write"
else:
	try:
		marshal.dump(vmap, f)
	except:
		print "Error saving cache"
	else:
		f.close()

if verbose:
	print "Apache Configuration:"
	for s in sharemap.keys():
		if counts[s] == 0:
			continue 
	
		shr = s.replace(' ', '_')
		print "Alias \"/" + shr + "\" \"" + sharemap[s] + "\""
		print "<Location \"/" + shr + "\">"
		print "  Options Indexes"
		print "  Order allow,deny"
		print "  Allow from all"
		print "</Location>"
		print ""


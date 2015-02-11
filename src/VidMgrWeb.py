#!/usr/bin/python
'''
Created on Apr 26, 2012

@author: Jeff
'''

from lconfig import HMEDIR, HOMELINK, HOMELABEL, TITLE, READONLYCLIENTS, READONLYSUBNETS, PUSHCLIENTS, PUSHSUBNETS, DELETECLIENTS, DELETESUBNETS

import ipaddr


import HTML
import time
import re
import cgi
import os
import urllib
import marshal
import subprocess 
import shutil
from TivoConfig import TivoConfig


if os.path.sep == '/':
	quote = urllib.quote
	unquote = urllib.unquote_plus
else:
	quote = lambda x: urllib.quote(x.replace(os.path.sep, '/'))
	unquote = lambda x: os.path.normpath(urllib.unquote_plus(x))

MAPFILE = "VMMap.dat"
CACHEFILE = HMEDIR + "/vidmgr/video.cache"
artdir = "artwork"
clientAddress = os.environ["REMOTE_ADDR"]

SCRIPTNAME = "VidMgrWeb.py"

bgs = (HTML.Color.RGB(219, 185, 125), HTML.Color.RGB(214, 207, 195))
hlColor = HTML.Color.RGB(196, 142, 47)
hlText = HTML.Color.RGB(128, 89, 22)

folderIcon = HTML.img({'src': "images/folder.png"})
parentIcon = HTML.img({'src': "images/parent.png"})
videoIcon = HTML.img({'src': "images/video.png"})
dvdIcon = HTML.img({'src': "images/dvdvideo.png"})

tcfg = TivoConfig()

tivoList = tcfg.getTivos()
	
shareList = tcfg.getShares()

def secureClient(clientAddr, clientList, subnetList):
	try:
		cip = ipaddr.IPAddress(clientAddr)
	except:
		return False

	for c in clientList:
		if c == 'ALL':
			return True
		try:
			if cip == ipaddr.IPAddress(c):
				return True
		except:
			return False
		
	for sn in subnetList:
		try:
			if cip in ipaddr.IPNetwork(sn):
				return True
		except:
			return False
		
	return False

def loadMap():
	vm = None
	if not os.path.exists(CACHEFILE):
		print HTML.h2("Unable to find/open vidmgr cache file")
		print HTML.endbody()
		print HTML.endhtml()
		return None

	cachetime = os.path.getctime(CACHEFILE)

	maptime = 0
	if os.path.exists(MAPFILE):
		maptime = os.path.getctime(MAPFILE)

	if maptime < cachetime:
		s = subprocess.call("python VMMap.py", shell=True)

	try:
		f = open(MAPFILE, 'rb')
	except:
		print HTML.h2("Unable to find/open vidmgr map file")
		print HTML.endbody()
		print HTML.endhtml()
		return None

	try:
		vm = marshal.load(f)
	except:
		print HTML.h2("Error loading map file")
		print HTML.endbody()
		print HTML.endhtml()
		return None

	return vm

def parentName(s):
	if s == "":
		return "root"
	
	return s.split('/')[-1]

def copyArtwork(artfn):
	if not os.path.exists(artdir):
		os.makedirs(artdir)

	now = time.time()
	for file in os.listdir(artdir):
		fn = os.path.join(artdir, file)
		if os.path.isfile(fn):
			ftime = os.path.getmtime(fn)
			if now - ftime > 300:
				os.unlink(fn)
	
	fn = os.path.join(artdir, "tmp%s.jpg" % clientAddress)			
	shutil.copyfile(artfn, fn)
	return fn

def removeFiles(path, fn):
	fullname =os.path.join(path, fn)
	for f in [ fullname,
			fullname + ".txt",
			os.path.join(path, ".meta", fn + '.txt'),
			fullname + ".jpg",
			os.path.join(path, ".meta", fn + '.jpg') ]:
		try:
			msg = "Attempting to delete %s" % f
			if os.path.exists(f):
				os.remove(f)
				print HTML.center(HTML.h2(msg + ": Successful"))
		except:
			print HTML.center(HTML.h2(msg + ": FAILED"))
			
	subprocess.call("cd " + HMEDIR + "/vidmgr; python BuildCache.py >/dev/null", shell=True)

#####################################################################################################

form = cgi.FieldStorage()

vTags = {'vActor' : "Actor(s): ",
		 'vDirector': "Director(s): ",
		 'vExecProducer': "Executive Producer(s): ",
		 'vWriter': "Writer(s): "}

GenreTags = ('vProgramGenre', 'vSeriesGenre')

path = ""
video = ""
if 'path' in form:
	path = form.getfirst('path')
if 'video' in form:
	video = form.getfirst('video')

print HTML.HTTPHeader()
print HTML.starthtml({'xmlns': "http://www.w3.org/1999/xhtml"})
print HTML.head(HTML.title('VidMgr Cache'))
print HTML.startbody({'bgcolor': HTML.Color.RGB(250, 242, 210)})

if not secureClient(clientAddress, READONLYCLIENTS, READONLYSUBNETS):
	print HTML.h2("Unknown Client: %s" % cgi.escape(clientAddress))
	print HTML.endbody()			
	print HTML.endhtml()
	exit(0)

vm = loadMap()
if not vm:
	exit(0)

try:
	tab = vm[path]
except:
	p = re.compile('^.*\((\d+)\)$')
	m = p.match(path)
	if m == None:
		print HTML.h2("Unable to retrieve map entry for (%s)" % path)
		print HTML.endbody()			
		print HTML.endhtml()
		exit(0)
		
	a, b = m.span(1)
	x = int(path[a:b]) - 1
	opath = path
	path = opath[:a] + str(x) + opath[b:]
	try:
		tab = vm[path]
	except:
		print HTML.h2("Unable to retrieve map entry for (%s)" % path)
		print HTML.h2("or for (%s)" % opath)
		print HTML.endbody()			
		print HTML.endhtml()
		exit(0)
		

if video != "":
	vfile = None
	vpath = None
	
	item = None			
	for e in tab:
		if e['type'] in ['VFILE', 'DVDFILE'] and e['text'] == video:
			item = e
			break
		
	if item == None:
		print HTML.h2("Unable to find video entry for (%s)" % video)
		print HTML.endbody()			
		print HTML.endhtml()
		exit(0)

	if 'meta' not in item:
		print HTML.center(HTML.h2("No metadata for '%s'" % video))
		print HTML.endbody()			
		print HTML.endhtml()
		exit(0)
		
	m = item['meta']
	
	title = ""
	epTitle = ""
	description = ""
	if 'title' in m:
		title = m['title']
	elif 'seriesTitle' in m:
		title = m['seriesTitle']
		
	if 'episodeTitle' in m:
		epTitle = m['episodeTitle']
		
	if 'description' in m:
		description = m['description']
		
	print "<br>"
	print HTML.center(
		HTML.table({'width': "60%"},
			HTML.tr(
				HTML.td({'width': "25%", 'style': 'text-align: left'}, HTML.font({'size': "5", 'face': "arial", 'color': hlText}, title)),
				HTML.td({'width': "75%", "rowspan": "2", 'style': 'text-align: left'}, HTML.font({'size': "2", 'face': "arial", 'color': 'black'}, description))
			),
			HTML.tr(
				HTML.td({'style': 'text-align: left'}, HTML.font({'size': 4, 'face': 'arial', 'color': 'black'}, epTitle))
			)			
		)
	)
	
	bx = 0
	trs = ""

	if 'episodeNumber' in m:
		s = m['episodeNumber']		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Episode Number: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx

	if 'callsign' in m or 'displayMajorNumber' in m:
		s = ""
		if 'callsign' in m:
			if 'displayMajorNumber' in m:
				s = "%s (%s)" % (m['callsign'], str(m['displayMajorNumber']))
			else:
				s = m['callsign']
		else:
			s = str(m['displayMajorNumner'])

		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Channel: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx

	if 'tvRating' in m:
		s = m['tvRating']		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "TV Rating: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx

	if 'mpaaRating' in m:
		s = m['mpaaRating']		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "MPAA Rating: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx

	if 'movieYear' in m:
		s = str(m['movieYear'])		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Movie Year: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx

	if 'originalAirDate' in m:
		s = str(m['originalAirDate'])		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Original Air Date: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx
		
	genre = {}
	
	for t in GenreTags:
		if t in m:
			for g in m[t]:
				genre[g] = 1
				
	if len(genre) > 0:
		s = ', '.join(genre)
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Genre: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx
		
	for vt in vTags.keys():
		if vt in m:
			s = ', '.join(m[vt])
			trs += HTML.tr({'bgcolor': bgs[bx]},
				HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, vTags[vt])),
				HTML.td({'style': 'text-align: left'}, s)
			)
			bx = 1 - bx				
		
	if 'programId' in m:
		s = str(m['programId'])		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Program ID: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx
		
	if 'seriesId' in m:
		s = str(m['seriesId'])		
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "Series ID: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx
		
	if '__fileName' in m:
		vfile = m['__fileName']
		s = str(m['__fileName'])	
		if '__filePath' in m:
			vpath = m['__filePath']
			s = m['__filePath'] + os.path.sep + s	
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'width': "25%", 'style': 'text-align: right'}, HTML.font({'size': "4", 'face': "arial", 'color': hlText}, "File Name: ")),
			HTML.td({'style': 'text-align: left'}, s)
		)
		bx = 1 - bx
		
	if 'imagefn' in item:
		fn = copyArtwork(item['imagefn'])
		trs += HTML.tr({'bgcolor': bgs[bx]},
			HTML.td({'style': 'text-align: center', 'colspan': "2"}, HTML.img({'src': fn}))
		)
		bx = 1 - bx
		
		
	print "<br><br>"
	print HTML.center(HTML.table({'width': "55%"}, trs))

	if 'push' in form and 'tsn' in form and vpath != None:
		if not secureClient(clientAddress, PUSHCLIENTS, PUSHSUBNETS):
			print HTML.center(HTML.h2("Client at %s does not have push authority" % clientAddress))
		else:
			tsn = form.getfirst('tsn')
			tivoname = ""
			for t in tivoList:
				if tsn == t['tsn']:
					tivoname = t['name']
					
			share = None
			relPath = None
			for s in shareList:
				if vpath.startswith(s['path']):
					share = s
					relPath = vpath[len(s['path']):]
					break
				
			if share == None:
				print HTML.center(HTML.h2("Unable to determine pytivo container"))
			else:
				params = urllib.urlencode({'Command': 'Push', 'Container': share['name'],
					'File': relPath + os.path.sep + vfile,
					'tsn': tsn})
				url = 'http://%s:%s/TivoConnect' % (share['ip'], share['port'])
				
				try:
					f = urllib.urlopen(url, params)
					html = f.read()
					
				except:
					print HTML.center(HTML.h2("An unknown exception has occurred during HTML request - verify configuration"))
				else:
					if html.lower().count('queue') != 0:
						print HTML.center(HTML.h2("File has been successfully queued for push to " + tivoname))
					else:
						print HTML.center(
							HTML.h2("PyTivo responded with an unknown message - push may still occur") +
							"<br>" +
							HTML.h3(html)
						)

	filesRemoved = False
	if 'delete' in form and vpath != None:
		if secureClient(clientAddress, DELETECLIENTS, DELETESUBNETS):
			confirm = form.getfirst('delconfirm', 'off')
			if confirm == "on":
				removeFiles(vpath, vfile)
				filesRemoved = True
			else:
				print HTML.center(HTML.h2("Deletion requires confirmation"))
		else:
			print HTML.center(HTML.h2("Client at %s does not have delete authority" % cgi.escape(clientAddress)))

	print "<br><br>"
	
	hl = ""
	if HOMELINK is not None:
		hl = " / " + HTML.a({'href': HOMELINK}, HOMELABEL)

	print HTML.center(HTML.a({'href': "%s?path=%s" % (SCRIPTNAME, quote(path))}, "back") + hl)
	
	if not filesRemoved:
		if secureClient(clientAddress, PUSHCLIENTS, PUSHSUBNETS):
			print "<br><br>"
			optString = ""
			for t in tivoList:
				optString += HTML.option({'value': t['tsn']}, t['name'])
			print HTML.center(
				HTML.form({'name': "pushform"},
					HTML.input({'name': 'push', 'type': 'submit', 'value': "Push"}) +
					" to " +
					HTML.select({'name': "tsn"}, optString) +
					HTML.input({'name': 'video', 'type': 'hidden', 'value': video}) +
					HTML.input({'name': 'path', 'type': 'hidden', 'value': path})
				)
			)
	
		if 'candelete' in item and secureClient(clientAddress, DELETECLIENTS, DELETESUBNETS):
			if item['candelete']:	
				print "<br>"
				print HTML.center(
					HTML.form({'name': "deleteform"},
						HTML.input({'name': 'delete', 'type': 'submit', 'value': "Delete"}) +
						" confirm delete: " +
						HTML.input({'name': 'delconfirm', 'type': 'checkbox'}) +
						HTML.input({'name': 'video', 'type': 'hidden', 'value': video}) +
						HTML.input({'name': 'path', 'type': 'hidden', 'value': path})
					)
				)
else:
	trs = ""
	bx = 0
	for e in tab:
		if  e['type'] == 'PARENT':	
			val = HTML.font({'size': "5", 'face': "arial", 'color': "black"}, parentName(e['link']))
			trs += HTML.tr({'bgcolor': bgs[bx]},
					HTML.td({'width': '32'}, parentIcon),
					HTML.td({'style': 'text-align: left'}, HTML.a({'href': "%s?path=%s" % (SCRIPTNAME, quote(e['link']))}, val))
				)
		elif e['type'] == 'VFILE' or e['type'] == 'DVDFILE':
			icon = videoIcon
			if e['type'] == 'DVDFILE':
				icon = dvdIcon
			val = HTML.font({'size': "5", 'face': "arial", 'color': "black"}, e['text'])
			trs += HTML.tr({'bgcolor': bgs[bx]},
					HTML.td({'width': '32'}, icon),
					HTML.td({'style': 'text-align: left'},
						HTML.a({'href': "%s?path=%s&video=%s" % (SCRIPTNAME, quote(path), quote(e['text']))}, val)
					)
				)
		elif e['type'] == 'FOLDER':
			val = HTML.font({'size': "5", 'face': "arial", 'color': "black"}, e['text'])
			trs += HTML.tr({'bgcolor': bgs[bx]},
					HTML.td({'width': '32'}, folderIcon),
					HTML.td({'style': 'text-align: left'}, HTML.a({'href': "%s?path=%s" % (SCRIPTNAME, quote(e['link']))}, val))
				)
		else:
			trs += HTML.tr({'bgcolor': bgs[bx], 'style': 'text-align: left'}, HTML.td({'colspan': "2"}, "Unknown node type: %s" %e['type']))
		bx = 1 - bx
			
	print HTML.center(
		HTML.h2(HTML.font({'size': "8", 'face': "arial", 'color': hlText}, TITLE)),
		HTML.h2(HTML.font({'size': "4", 'face': "arial", 'color': 'black'}, path)),
		HTML.table({'border': 1, 'cellpadding': 2, 'cellspacing': 0, 'width': '70%'}, trs)
	)
	
	if HOMELINK is not None:
		print "<br><br>"
		print HTML.center(HTML.a({'href': HOMELINK}, HOMELABEL))

print HTML.endbody()			
print HTML.endhtml()


	
	

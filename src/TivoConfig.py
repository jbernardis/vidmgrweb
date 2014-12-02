'''
Created on May 15, 2012

@author: jbernard
'''
import socket
import os
import ConfigParser
from string import maketrans
from lconfig import HMEDIR

class TivoConfigError(Exception):
	pass

class TivoConfig:
	def __init__(self):
		def cmptivo (left, right):
			return cmp(left['name'], right['name']) 
		
		self.tivos = []
		self.shares = []
		fn = HMEDIR + "/vidmgr/vidmgr.ini"

		self.cfg = ConfigParser.ConfigParser()
		if not self.cfg.read(fn):
			raise TivoConfigError("ERROR: vidmgr configuration file (%s) does not exist." % fn)

		tlist = []
		section = 'tivos'
		
		allchars = maketrans('', '')
		if self.cfg.has_section(section):
			i = 0
			while (True):
				i = i + 1
				namekey = 'tivo' + str(i) + '.name'
				tsnkey = 'tivo' + str(i) +  '.tsn'
				if self.cfg.has_option(section, namekey) and self.cfg.has_option(section, tsnkey):
					tlist.append({'name' : self.cfg.get(section, namekey),
									'tsn' : self.cfg.get(section, tsnkey).translate(allchars, '-')})
				else:
					break
				
		self.tivos = sorted(tlist, cmp=cmptivo)

		# load up pytivo and shares information from config and from pytivo config(s)
		self.shares = []
		
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('4.2.2.1', 123))
		defip = s.getsockname()[0]
	
		section = 'pytivos'
		if self.cfg.has_section(section):
			i = 0
			while (True):
				i = i + 1
				key = "pytivo" + str(i) + ".config"
				if not self.cfg.has_option(section, key): break
				cfgfile = self.cfg.get(section, key)
				
				sep = None
				sepkey = 'pytivo' + str(i) + '.sep'
				if self.cfg.has_option(section, sepkey): sep = self.cfg.get(section, sepkey)
				
				ip = defip
				key = "pytivo" + str(i) + ".ip"
				if self.cfg.has_option(section, key):
					ip = self.cfg.get(section, key)

				port = None				
				key = "pytivo" + str(i) + ".port"
				if self.cfg.has_option(section, key):
					port = self.cfg.get(section, key)
					
				key = "pytivo" + str(i) + ".skip"
				skip = []
				if self.cfg.has_option(section, key):
					sk = self.cfg.get(section, key).split(",")
					skip = [s.strip() for s in sk]
				
				self.loadPyTivoConfig(cfgfile, ip, port, sep, skip)

	# parse a pytivo config looking for shares				
	def loadPyTivoConfig(self, cf, ip, defport, sep, skip):
		pyconfig = ConfigParser.ConfigParser()
		if not pyconfig.read(cf):
			raise TivoConfigError("ERROR: pyTivo config file " + cf + " does not exist.")

		port = defport
		if pyconfig.has_option('Server', 'port') : port = pyconfig.get('Server', 'port')
		
		if port == None:
			raise TivoConfigError("Neither main config file nor pytivo config file " + cf + " has port number specified")
		
		for section in pyconfig.sections():
			if not section in skip:
				if (pyconfig.has_option(section, "type")
						and (pyconfig.get(section, "type") == "video" or pyconfig.get(section, "type") == "dvdvideo")
						and	pyconfig.has_option(section, 'path')):
					path = pyconfig.get(section, 'path')
					self.shares.append({'name' : section,
							'ip' : ip,
							'port' : port,
							'path' : path,
							'sep' : sep})

		
	def getTivos(self):
		return self.tivos
	
	def getShares(self):
		return self.shares

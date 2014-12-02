# the directory in which PYHME is installed.  "vidmgr" is assumed to be a subdirectory of this directory
HMEDIR = "/usr/local/pyhme"

# Where the home link takes you back to - set to None (no quotes) if you do not wish a back link.  HOMELABEL is the text
# that will appear on screen - immaterial if HOMELINK is None
HOMELINK = "../index.html"
HOMELABEL = "Home"

# web page title text
TITLE = "PyTivo Video Manager Cache"

# security
#
# for each pair of lists below indicate the clients and subnets that are allowed.  The Clients list is a list of IP addresses that will be granted
# the associated privilege.  A special value of ['ALL'] indicates that all clients will be accepted while an empty list [] indicates that NO individual 
# clients will be accepted.  Otherwise this is a list of acceptable IP addresses: ['192.168.1.100', '192.168.1.200'].
#
# the subnet list is a list of subnets from which all member IP addresses will be accepted.  This list is immaterial if the client list is ['ALL'].  This
# list can be empty - if both the client and subnet lists are empty, the associated privilege will never be granted
#
# READONLY access - can the client even see the video list
#
READONLYCLIENTS = ['ALL']
READONLYSUBNETS = ['192.168.1.0/24']
#
# PUSH access - can the client PUSH videos
#
PUSHCLIENTS = []
PUSHSUBNETS = ['192.168.1.0/24']
#
# DELETE access - can the client delete videos.  Videos can only be deleted if this privilege is granted AND the video is subject to deletion
# from within VidMgr too
#
DELETECLIENTS = []
DELETESUBNETS = ['192.168.1.0/24']


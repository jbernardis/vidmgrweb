CGISRC = VidMgrWeb.py TivoConfig.py VMMap.py lconfig.py
IMAGES = images/video.png images/parent.png

all: install 

install : .installcgi .installimg

.installcgi : $(CGISRC)
	fixcrlf $?
	chmod 777 $?
	cp $? /web/scripts
	touch .installcgi

.installimg : $(IMAGES)
	chmod 666 $?
	cp $? /web/scripts/images
	touch .installimg

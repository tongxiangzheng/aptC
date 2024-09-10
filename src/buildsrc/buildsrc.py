import os
import libarchive.public

def unzip(zipfile,toPath):
	with libarchive.public.file_reader(zipfile) as e:
		for entry in e:
			entryFileName=os.path.join(toPath,entry.pathname)
			e.readpath(entryFileName)
			
def buildsrc(orig,debian=""):
	unzip(orig,"package")

buildsrc("network-manager_0.9.8.8-0ubuntu7.1.debian.tar.gz","network-manager_0.9.8.8.orig.tar.xz")
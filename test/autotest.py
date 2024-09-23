import sys
import os
def autotest_deb(name,version,release):
	cmd=f"python ../src/aptC.py genspdx {name}={version}-{release} ./binary"
	print(cmd)
	os.system(cmd)

def autotest_src(name,version,release):
	dscLink=f"http://archive.ubuntu.com/ubuntu/pool/main/{name[0]}/{name}/{name}_{version}-{release}.dsc"
	

	os.system("dget "+dscLink)
	srcFile=f"{name}_{version}.orig.tar.xz"
	if not os.path.isfile(srcFile):
		srcFile=f"{name}_{version}.orig.tar.gz"

	srcFile2=f"{name}_{version}-{release}.debian.tar.xz"
	if not os.path.isfile(srcFile2):
		srcFile2=f"{name}_{version}-{release}.debian.tar.gz"

	if os.path.isfile(srcFile) and os.path.isfile(srcFile2):
		cmd=f"python ../src/aptC.py scansrc {srcFile} {srcFile2} --genspdx=./src"
		print(cmd)
		os.system(cmd)
		pass
	else:
		srcFile=f"{name}_{version}.tar.xz"
		srcFile2=None
		cmd=f"python ../src/aptC.py scansrc {srcFile}"
		print(cmd)
		os.system(cmd)


with open("jammyinfo.txt") as f:
	data=f.readlines()
checked=set()
for info in data:
	info=info.split(' ')
	name=info[0].strip()
	if name in checked:
		continue
	checked.add(name)
	version=info[2].strip()
	release=info[3].strip()
	autotest_deb(name,version,release)
	autotest_src(name,version,release)
	break

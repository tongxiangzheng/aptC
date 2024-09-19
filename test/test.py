import sys
import os
name=sys.argv[1]
version=sys.argv[2]
release=sys.argv[3]
dscLink=f"http://archive.ubuntu.com/ubuntu/pool/main/{name[0]}/{name}/{name}_{version}-{release}.dsc"
os.system(f"python ../src/aptC.py genspdx {name}={version}-{release} ./binary")

os.system("dget "+dscLink)
srcFile=f"{name}_{version}.orig.tar.xz"
if not os.path.isfile(srcFile):
	srcFile=f"{name}_{version}.orig.tar.gz"

srcFile2=f"{name}_{version}-{release}.debian.tar.xz"
if not os.path.isfile(srcFile2):
	srcFile2=f"{name}_{version}-{release}.debian.tar.gz"

if os.path.isfile(srcFile) and os.path.isfile(srcFile2):
	cmd=f"python ../src/aptC.py scansrc {srcFile} {srcFile2}"
	print(cmd)
	os.system(cmd)
	pass
else:
	srcFile=f"{name}_{version}.tar.xz"
	srcFile2=None
	cmd=f"python ../src/aptC.py scansrc {srcFile}"
	print(cmd)
	os.system(cmd)
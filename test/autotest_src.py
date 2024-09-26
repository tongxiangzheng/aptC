import sys
import os
import time
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import aptC
import normalize
from subprocess import PIPE, Popen
def autotest_src(name,fullname,version,release,checkExist=True):
	if checkExist:
		if os.path.isfile("./src/"+normalize.normalReplace(f"{fullname}.spdx.json")):
			return 0
	print(name,version,release)
	version=version.split(':')[-1]
	dscLink=f"http://archive.ubuntu.com/ubuntu/pool/main/{name[0]}/{name}/{name}_{version}-{release}.dsc"
	
	p = Popen("dget "+dscLink, shell=True, stdout=PIPE, stderr=PIPE,cwd="./source")
	stdout, stderr = p.communicate()
	time.sleep(1)
	zipType=["bz2","gz","lzma","xz"]
	srcFile=None
	for t in zipType:
		fileName=f"./source/{name}_{version}.orig.tar.{t}"
		if os.path.isfile(fileName):
			srcFile=fileName
			break
	
	srcFile2=None
	for t in zipType:
		fileName=f"./source/{name}_{version}-{release}.debian.tar.{t}"
		if os.path.isfile(fileName):
			srcFile2=fileName
			break
	if srcFile is not None and srcFile2 is not None:
		#cmd=f"python ../src/aptC.py scansrc {srcFile} {srcFile2} --genspdx=./src"
		#print(cmd)
		return aptC.user_main("apt",["scansrc",srcFile,srcFile2,"--genspdx=./src","-mode=split"], exit_code=False)
	else:
		for t in zipType:
			fileName=f"./source/{name}_{version}.tar.{t}"
			if os.path.isfile(fileName):
				srcFile=fileName
				break
		
		srcFile2=None
		#cmd=f"python ../src/aptC.py scansrc {srcFile}"
		#print(cmd)
		#os.system(cmd)
		if srcFile is None:
			print("error: no src file")
			return 1
		else:
			return aptC.user_main("apt",["scansrc",srcFile,"--genspdx=./src","-mode=split"], exit_code=False)

if __name__ == "__main__":
	with open("jammyinfo.txt") as f:
		data=f.readlines()
	checked=set()
	for info in data:
		info=info.split(' ')
		name=info[0].strip()
		fullname=info[1].strip()
		if name in checked:
			continue
		checked.add(name)
		version=info[2].strip()
		release=info[3].strip()
		#autotest_deb(name,version,release)
		if autotest_src(name,fullname,version,release) != 0:
			print(name,version,release)
			break

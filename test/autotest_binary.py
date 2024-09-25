import sys
import os
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import normalize
import aptC
def autotest_binary(name,version,release):
	#if os.path.isfile("./binary/"+normalize.normalReplace(f"{name}.spdx.json")):
	#	return 0
	print(name,version,release)
	return aptC.user_main("apt",["genspdx",f"{name}={version}-{release}","binary"], exit_code=False)

if __name__ == "__main__":
	with open("jammyinfo.txt") as f:
		data=f.readlines()
	checked=set()
	for info in data:
		info=info.split(' ')
		name=info[1].strip()
		if name in checked:
			continue
		checked.add(name)
		version=info[2].strip()
		release=info[3].strip()
		if autotest_binary(name,version,release)!=0:
			print(name,version,release)
			break
		
		#autotest_src(name,version,release)

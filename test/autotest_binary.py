import sys
import os
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import normalize
import aptC
def autotest_binary(infos,checkExist=True):
	if checkExist:
		for info in infos:
			if os.path.isfile("./binary/"+normalize.normalReplace(f"{info[0]}.spdx.json")):
				return 0
	print("-------")
	packages=["genspdx"]
	for name,version,release in infos:
		print(name,version,release)
		if release is not None:
			packages.append(f"{name}={version}-{release}")
		else:
			packages.append(f"{name}={version}")
	packages.append("binary")
	return aptC.user_main("apt",packages, exit_code=False)

if __name__ == "__main__":
	with open("jammyinfo.txt") as f:
		data=f.readlines()
	nameMap=dict()
	for info in data:
		info=info.split(' ')
		name=info[0].strip()
		fullName=info[1].strip()
		version=info[2].strip()
		release=info[3].strip()
		if name not in nameMap:
			nameMap[name]=[]
		nameMap[name].append((fullName,version,release))
	for name,infos in nameMap.items():
		if autotest_binary(infos)!=0:
			print(infos)
			break
		
		#autotest_src(name,version,release)

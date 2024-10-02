import os

import lz4.frame

import SpecificPackage

def parseDEBItemInfo(item):
    item=item.strip()
    name=None
    flags=None
    version=None
    release=None
    items_version=item.split('(')
    if len(items_version)>1:
        name=items_version[0].strip()
        v=items_version[1].split(')')[0]
        parse=v.split('=')
        if len(parse)>1:
            flags="EQ"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('<')
        if len(parse)>1:
            flags="LE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('<=')
        if len(parse)>1:
            flags="LE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('<<')
        if len(parse)>1:
            flags="LT"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('>')
        if len(parse)>1:
            flags="GE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('>=')
        if len(parse)>1:
            flags="GE"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        parse=v.split('>>')
        if len(parse)>1:
            flags="GT"
            p2=parse[1].strip().split('-')
            version=p2[0]
            if len(p2)<1:
                release=p2[1].split('.')[0]
        # In dpkg document:
        # The < and > operators are obsolete and should not be used, due to confusing semantics.
        # To illustrate: 0.1 < 0.1 evaluates to true.
    else:
        name=item
    return SpecificPackage.PackageEntry(name,flags,version,release)

def parseDEBPackages(repoInfos,osType,dist,repoURL)->list:
	fullName=""
	name=""
	version=""
	release=None
	provides=[]
	requires=[]
	arch=""
	filename=""
	source=""
	res=[]
	for i in range(len(repoInfos)):
		info=repoInfos[i].strip()
		if len(info)==0:
			continue
		if info.startswith("Package:"):
			if name=="":
				name=fullName
			if name!="":
				packageInfo=SpecificPackage.PackageInfo(osType,dist,name,version,release,arch)
				res.append(SpecificPackage.SpecificPackage(packageInfo,fullName,provides,requires,arch,source,repoURL=repoURL,fileName=filename))
			fullName=""
			name=""
			version=""
			release=None
			provides=[]
			requires=[]
			arch=""
			filename=""
			source=""

			fullName=info.split(' ',1)[1]
		if info.startswith("Source:"):
			source=info.split(' ',1)[1]
			name=info.split(' ',2)[1]
		if info.startswith("Version:"):
			version_release=info.split(' ',1)[1].rsplit('-',1)
			version=version_release[0].split(':')[-1]
			if len(version_release)>1:
				release=version_release[1]
		if info.startswith("Architecture:"):
			arch=info.split(' ',1)[1]
		if info.startswith("Depends:") or info.startswith("Pre-Depends:") or info.startswith("Recommends:"):
			depInfos=info.split(' ',1)[1].split(",")
			for depInfo in depInfos:
				dep=SpecificPackage.PackageEntrys()
				for dInfo in depInfo.split('|'):
					dep.addEntry(parseDEBItemInfo(dInfo))
				requires.append(dep)
		if info.startswith("Provides:"):
			proInfos=info.split(' ',1)[1].split(",")
			for proInfo in proInfos:
				for pInfo in proInfo.split('|'):
					provides.append(parseDEBItemInfo(pInfo))
		if info.startswith("Filename:"):
			filename=info.split(' ',1)[1]
	if name=="":
		name=fullName
	if name!="":
		packageInfo=SpecificPackage.PackageInfo(osType,dist,name,version,release,arch)
		res.append(SpecificPackage.SpecificPackage(packageInfo,fullName,provides,requires,arch,source,repoURL=repoURL,fileName=filename))
	# for r in res:
	# 	if r.packageInfo.release is None:
	# 		continue
	# 	print(r.packageInfo.name,r.fullName,r.packageInfo.version,r.packageInfo.release)
	return res


class RepoFileManager:
	def __init__(self,url,repoPath,osType,dist):
		self.url=url
		self.repoPath=repoPath
		self.packageMap=SpecificPackage.defaultdict(SpecificPackage.defaultNoneList)
		self.enable=True
		if os.path.isfile(repoPath):
			with open(repoPath,"r") as f:
				data=f.readlines()
		elif os.path.isfile(repoPath+".lz4"):
			with open(repoPath+".lz4","rb") as f:
				data=f.read()
				data = lz4.frame.decompress(data).decode().split('\n')
		else:
			self.enable=False
			return
		packages=parseDEBPackages(data,osType,dist,url)
		for package in packages:
			self.packageMap[package.fullName].append(package)
	def queryPackage(self,name,version,release):
		if self.enable is False:
			return None
		#version=firstNumber(version)
		#if release is not None:
		#	release=firstNumber(release)
		e=SpecificPackage.PackageEntry(name,"EQ",version,release)
		if name in self.packageMap:
			for specificPackage in self.packageMap[name]:
				if SpecificPackage.compareEntry(specificPackage.getSelfEntry(),e)==0:
					if specificPackage.packageInfo.release is None or SpecificPackage.compareVersion(specificPackage.packageInfo.release,release)==0:
						return specificPackage
		return None
	def getAllPackages(self):
		if self.enable is False:
			return []
		res=[]
		for packageList in self.packageMap.values():
			res.extend(packageList)
		return res
		
	
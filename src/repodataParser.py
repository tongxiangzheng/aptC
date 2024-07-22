import xml.dom.minidom
import os
import sys
from dom_tool import sub2dict,dfs
from SpecificPackage import *
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
    return PackageEntry(name,flags,version,release)

def parseDEBPackages(repoInfos,osType,dist,repoURL)->SpecificPackage:
	fullName=""
	name=""
	version=""
	release=None
	provides=[]
	requires=[]
	arch=""
	filename=""
	res=[]
	for i in range(len(repoInfos)):
		info=repoInfos[i].decode('UTF-8').strip()
		if len(info)==0:
			if name=="":
				name=fullName
			provides.append(PackageEntry(fullName,"EQ",version,release))
			packageInfo=PackageInfo(osType,dist,name,version,release)
			res.append(SpecificPackage(packageInfo,fullName,provides,requires,arch,repoURL=repoURL,fileName=filename))
			fullName=""
			name=""
			version=""
			release=None
			provides=[]
			requires=[]
			arch=""
			filename=""
		if info.startswith("Package:"):
			fullName=info.split(':',1)[1].strip()
		if info.startswith("Source:"):
			name=info.split(':',1)[1].strip()
		if info.startswith("Version:"):
			version_release=info.split(':',1)[1].split('-').strip()
			version=version_release[0]
			if len(version_release)>1:
				release=version_release[1]
		if info.startswith("Architecture:"):
			arch=info.split(':',1)[1].strip()
		if info.startswith("Depends:"):
			depInfos=info.split(':',1)[1].split("|").strip()
			for depInfo in depInfos:
				requires.append(parseDEBItemInfo(depInfo))
		if info.startswith("Provides:"):
			proInfos=info.split(':',1)[1].split("|").strip()
			for proInfo in proInfos:
				provides.append(parseDEBItemInfo(proInfo))
		if info.startswith("Filename:"):
			filename=info.split(':',1)[1].strip()
	return res


def parseDEBFiles(repoURL:str,repoPath:str):
	entryMap=EntryMap()
	packageMap=dict()
	with open(repoPath,"r") as f:
		packages=parseDEBPackages(f.readlines(),osType,dist,repoURL)
		for package in packages:
			package.registerProvides(entryMap)
			if package.fullName not in packageMap:
				log.trace("new package:"+package.fullName)
				packageMap[package.fullName]=package
			else:
				log.trace("installed package:"+package.fullName)
				packageMap[package.fullName].packageInfo.name=package.packageInfo.name
				packageMap[package.fullName].registerProvides(entryMap)
	return packageMap
		
## abandon file
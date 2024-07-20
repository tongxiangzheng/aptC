import os
from loguru import logger as log
import nwkTools
from SpecificPackage import *

def getDscFile(repoURL,dscFileName):
	baseURL=repoURL.rsplit('/',3)[0]+"/"
	log.info("download dsc file :"+dscFileName+" from "+baseURL+dscFileName)
	try:
		dscFilePath=nwkTools.downloadFile(baseURL+dscFileName,os.path.join("~",".aptC","repoMetadata","dscFiles",dscFileName.rsplit('/',1)[0]),dscFileName.rsplit('/',1)[1])
		os.chmod(dscFilePath, 0o744)
		return dscFilePath
	except Exception as e:
		log.warning("download failed")
		return None
def parseDscFile(dscFilePath):
	with open(dscFilePath,"r") as f:
		data=f.readlines()
	for info in data:
		info=info.strip()
		if info.startswith("Vcs-Git:") or info.startswith("Debian-Vcs-Git:"):
			return info.split(' ',1)[1]



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
			fullName=info.split(' ',1)[1]
		if info.startswith("Source:"):
			name=info.split(' ',1)[1]
		if info.startswith("Version:"):
			version_release=info.split(' ',1)[1].split('-')
			version=version_release[0]
			if len(version_release)>1:
				release=version_release[1]
		if info.startswith("Architecture:"):
			arch=info.split(' ',1)[1]
		if info.startswith("Depends:"):
			depInfos=info.split(' ',1)[1].split("|")
			for depInfo in depInfos:
				requires.append(parseDEBItemInfo(depInfo))
		if info.startswith("Provides:"):
			proInfos=info.split(' ',1)[1].split("|")
			for proInfo in proInfos:
				provides.append(parseDEBItemInfo(proInfo))
		if info.startswith("Filename:"):
			filename=info.split(' ',1)[1]
	return res
class RepoFileManager:
	def __init__(self,url,repoPath,osType,dist):
		self.url=url
		self.repoPath=repoPath
		self.packageMap=dict()
		with open(repoPath,"r") as f:
			packages=parseDEBPackages(f.readlines(),osType,dist,url)
			for package in packages:
				self.packageMap[package.fullName]=package
	def queryPackage(self,name):
		return self.packageMap[name]
	def getGitLink(self,name):
		specPackageInfo=self.queryPackage(name)
		repoURL=specPackageInfo.repoURL
		if repoURL is None or specPackageInfo.fileName == "":
			return None
		version=specPackageInfo.fileName.rsplit('_',2)[1]
		dscFileName=specPackageInfo.fileName.rsplit('/',1)[0]+'/'+specPackageInfo.packageInfo.name+'_'+version+".dsc"
		dscFilePath=getDscFile(repoURL,dscFileName)
		if dscFilePath is None:
			return None
		gitLink=parseDscFile(dscFilePath)
		return gitLink
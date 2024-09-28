import os
import SpecificPackage
import SourcesListManager
from subprocess import PIPE, Popen
import osInfo
import RepoFileManager
from loguru import logger as log
def getSelfDist():
	with open("/etc/os-release") as f:
		data=f.readlines()
		for info in data:
			if info.startswith('VERSION_CODENAME='):
				return info.strip()[17:]	
	return ""
selfDist=getSelfDist()
def parseInstallInfo(info:str,sourcesListManager:SourcesListManager.SourcesListManager)->SpecificPackage.SpecificPackage:
	info=info.strip()
	while info.endswith(']'):
		info=info.rsplit('[',1)[0].strip()
	info=info.split(' ',2)
	name=info[1]
	additionalInfo=info[2].split(']')[-2].strip()[1:].split(' ')
	version_release=additionalInfo[0].rsplit('-',1)
	version=version_release[0].split(':')[-1]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=additionalInfo[1].split('/')[1].split(',')[0]
	#arch=additionalInfo[-1][1:-1]
	#packageInfo=PackageInfo.PackageInfo('Ubuntu',dist,name,version,release,arch)
	#print(name,dist,version,release)
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release)
	specificPackage.status="willInstalled"

	return specificPackage
def getSpecificInstalledPackage(packageName,version_release):
	p = Popen(f"apt-cache show {packageName}={version_release}", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	package=RepoFileManager.parseDEBPackages(data,osInfo.OSName,osInfo.OSDist,None)[0]
	package.status="installed"
	return package
def getInstalledPackagesInfo(sourcesListManager):
	res=[]
	p = Popen("/usr/bin/apt list --installed", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data[1:]:
		if len(info)==0:
			continue
		packageName=info.split('/',1)[0]
		dists=info.split('/',1)[1].split(' ',1)[0].split(',')
		dist=None
		for d in dists:
			if d!="now":
				dist=d
				break
		if dist is None:
			res.append(getSpecificInstalledPackage(packageName,info.split(' ')[1]))
			continue
		version_release=info.split(' ')[1].rsplit('-',1)
		version=version_release[0].split(':')[-1]
		release=None
		if len(version_release)>1:
			release=version_release[1]
		package=sourcesListManager.getSpecificPackage(packageName,dist,version,release)
		
		if package is not None:
			package.status="installed"
			res.append(package)
		else:
			res.append(getSpecificInstalledPackage(packageName,info.split(' ')[1]))
	return res
	

def getNewInstall(packages:list,options,sourcesListManager:SourcesListManager.SourcesListManager,includeInstalled=False):
	cmd="/usr/bin/apt-get reinstall -s "
	for option in options:
		if option.startswith('--genspdx'):
			continue
		if option.startswith('--gencyclonedx'):
			continue
		if option.startswith('-n'):
			continue
		cmd+=option+' '
	for packageName in packages:
		cmd+=packageName+' '
	willInstallPackages=[]
	#log.info('cmd is '+cmd)
	#actualPackageName=packageName
	p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data:
		# if info.startswith('Note, selecting '):
		# 	print(info)
		# 	actualPackageName=info.split('\'')[1]
		# 	log.info("Note, selecting \'"+actualPackageName+"\' instead of \'"+packageName+"\'")
		# it not work because in non-terminal, the info will show
		if info.startswith('Inst '):
			willInstallPackages.append(parseInstallInfo(info,sourcesListManager))
	if len(willInstallPackages)==0:
		print("warning: no package will install")
		includeInstalled=True
	resmap=dict()
	entryMap=SpecificPackage.EntryMap()
	if includeInstalled is True:
		installedPackages=getInstalledPackagesInfo(sourcesListManager)
		for package in installedPackages:
			package.registerProvides(entryMap)
	for p in willInstallPackages:
		p.registerProvides(entryMap)
	package_select=set()
	for packageName in packages:
		selectedPackage=None
		packageName=packageName.split('=',1)[0]
		for p in willInstallPackages:
			if p.fullName==packageName:
				selectedPackage=p
		if selectedPackage is None:
			for p in willInstallPackages:
				for provide in p.providesInfo:
					if provide.name==packageName:
						selectedPackage=p
						break
				if selectedPackage is not None:
					break
			if includeInstalled is True:
				for p in installedPackages:
					for provide in p.providesInfo:
						if provide.name==packageName:
							selectedPackage=p
							break
					if selectedPackage is not None:
						break

		if selectedPackage is None:
			continue
			
		#selectedPackage.findRequires(entryMap)
		#return None,[]
		SpecificPackage.getDependsPrepare(entryMap,selectedPackage)
		package_select.add(selectedPackage)
	for selectedPackage in package_select:
		depends=SpecificPackage.getDepends(entryMap,selectedPackage)
		res=list(depends)
		resmap[selectedPackage]=res
	return resmap

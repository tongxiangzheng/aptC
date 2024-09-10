import os
import SpecificPackage
import SourcesListManager
from subprocess import PIPE, Popen
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
	if info.endswith('[]'):
		info=info.rsplit(' ',1)[0]
	info=info.strip().split(' ',2)
	name=info[1]
	additionalInfo=info[2].split(']')[-2].strip()[1:].split(' ')
	version_release=additionalInfo[0].split('-')
	version=version_release[0].split(':')[-1]
	release=None
	if len(version_release)>1:
		release=version_release[1]
	dist=additionalInfo[1].split('/')[1].split(',')[0]
	#arch=additionalInfo[-1][1:-1]
	#packageInfo=PackageInfo.PackageInfo('Ubuntu',dist,name,version,release,arch)
	specificPackage=sourcesListManager.getSpecificPackage(name,dist,version,release)
	specificPackage.setGitLink()
	return specificPackage
def getInstalledPackagesInfo(sourcesListManager):
	res=[]
	p = Popen("/usr/bin/apt list --installed", shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	data=stdout.decode().split('\n')
	for info in data[1:]:
		if len(info)==0:
			continue
		packageName=info.split(',')[0].split('/')[0]
		dist=info.split(',')[0].split('/')[1]
		version_release=info.split(',')[1].split('-')
		version=version_release[0].split(':')[-1]
		release=None
		if len(version_release)>1:
			release=version_release[1]
		package=sourcesListManager.getSpecificPackage(packageName,dist,version,release)
		if package is not None:
			res.append(package)
	return res

def getDependes(package:SpecificPackage.SpecificPackage,dependesSet:set):
	if package in dependesSet:
		return
	dependesSet.add(package)
	for p in package.requirePointers:
		getDependes(p,dependesSet)		

def getNewInstall(packageName:str,options,sourcesListManager:SourcesListManager.SourcesListManager,includeInstalled=False):
	cmd="/usr/bin/apt-get reinstall -s "
	for option in options:
		if option.startswith('--genspdx'):
			continue
		if option.startswith('--gencyclonedx'):
			continue
		if option.startswith('-n'):
			continue
		cmd+=option+' '
	cmd+=packageName
	res=[]
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
			res.append(parseInstallInfo(info,sourcesListManager))
	if len(res)==0:
		return None,[]
	selectedPackage=None
	for p in res:
		if p.fullName==packageName:
			selectedPackage=p
	if selectedPackage is None:
		for p in res:
			for provide in p.providesInfo:
				if provide.name==packageName:
					selectedPackage=p
	if selectedPackage is None:
		log.warning("unknown error")
	if includeInstalled is True:
		installedPackages=getInstalledPackagesInfo(sourcesListManager)
		entryMap=SpecificPackage.EntryMap()
		for package in installedPackages:
			package.registerProvides(entryMap)
		for package in res:
			#print("")
			#print(package.fullName)
			#for provide in package.providesInfo:
			#	print(' '+provide.dump())
			#print("-----")
			#for provide in package.requiresInfo:
			#	print(' '+provide.dump())
			package.registerProvides(entryMap)

		for package in installedPackages:
			package.findRequires(entryMap)
		for package in res:
			package.findRequires(entryMap)
		depends=set()
		getDependes(selectedPackage,depends)
		res=list(depends)

	return selectedPackage,res

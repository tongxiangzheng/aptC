import getNewInstall
import SourcesListManager
import nwkTools
from loguru import logger as log
from spdx.spdxmain import spdxmain
import normalize
import json
import queryCVE
import loadConfig
import spdxReader

def downloadPackage(selectedPackage):
	packagePath=nwkTools.downloadFile(selectedPackage.repoURL+'/'+selectedPackage.fileName,'/tmp/aptC/packages',normalize.normalReplace(selectedPackage.fileName.rsplit('/',1)[1]))
	if packagePath is None:
		print("failed to download package from:"+selectedPackage.repoURL+'/'+selectedPackage.fileName)
	#packagePath="/home/txz/code/aptC/test/acct-underline-6.6.4-4build2-underline-amd64.deb"
	#for test
	return packagePath

	
def checkIncludeDepends(spdxObj):
	res=spdxReader.parseSpdxObj(spdxObj)
	if len(res)!=0:
		return True
	else:
		return False
def scanDeb(command,options,packages,genSpdx=True,saveSpdxPath=None,genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=False):
	assumeNo=False
	noPackagesWillInstalled=True
	for option in options:
		if option=='-n':
			assumeNo=True
		if option.startswith('--genspdx'):
			genSpdx=True
			if len(option.split('=',1))!=2:
				print("usage: apt install <packages> --genspdx=<path>")
				return False
			saveSpdxPath=option.split('=',1)[1]
		if option.startswith('--gencyclonedx'):
			genCyclonedx=True
			saveCyclonedxPath=option.split('=',1)[1]
	
	sourcesListManager=SourcesListManager.SourcesListManager()
	packageProvides=dict()
	aptConfigure=loadConfig.loadConfig()
	if aptConfigure is None:
		print('ERROR: cannot load config file in /etc/aptC/config.json, please check config file ')
		return False
	getNewInstallRes=getNewInstall.getNewInstall(packages,options,sourcesListManager,dumpFileOnly)
	if getNewInstallRes is None:
		return True
	haveOutput=False
	for selectedPackage,willInstallPackages in getNewInstallRes.items():
		if len(willInstallPackages)>0:
			noPackagesWillInstalled=False
		selectedPackageName=selectedPackage.fullName
		packageProvides[selectedPackageName]=willInstallPackages
		depends=dict()
		project_packages=dict()
		for p in willInstallPackages:
			p.setDscLink()
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
			if p.packageInfo.name not in project_packages:
				project_packages[p.packageInfo.name]=[]
			project_packages[p.packageInfo.name].append(p.fullName)
		dependsList=list(depends.values())
		packageFilePath=downloadPackage(selectedPackage)
		if packageFilePath is None:
			return False
		if dumpFileOnly is True:
			if genSpdx is True:
				spdxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'spdx',saveSpdxPath)
			if genCyclonedx is True:
				cyclonedxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'cyclonedx',saveCyclonedxPath)
			continue
		spdxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'spdx',saveSpdxPath)
		if genCyclonedx is True:
			cyclonedxPath=spdxmain(selectedPackageName,packageFilePath,dependsList,'cyclonedx',saveCyclonedxPath)
		#print("spdx file at "+spdxPath)

		with open(spdxPath,"r") as f:
			spdxObj=json.load(f)
		cves=queryCVE.queryCVE(spdxObj,aptConfigure)
		for package in willInstallPackages:
			if package==selectedPackage:
				continue
			packageFilePath=downloadPackage(package)
			if packageFilePath is None:
				continue
			spdxPath=spdxmain(package.fullName,packageFilePath,[],'spdx')
			with open(spdxPath,"r") as f:
				spdxObj=json.load(f)
			if not checkIncludeDepends(spdxObj):
				continue
			#print("find depends!!!")
			#print(spdxPath)
			dependsCves=queryCVE.queryCVE(spdxObj,aptConfigure)
			if dependsCves is None:
				continue
			for projectName,c in dependsCves.items():
				if len(c)==0:
					continue
				if projectName not in cves[package.packageInfo.name]:
					cves[package.packageInfo.name].extend(c)
			
			
		if cves is None:
			continue
		if selectedPackage.packageInfo.name in cves:
			selectedPackage_cves=cves[selectedPackage.packageInfo.name]
		else:
			selectedPackage_cves=[]
		for projectName,c in cves.items():
			if len(c)==0:
				continue
			if projectName not in project_packages:
				selectedPackage_cves.extend(c)
		cves[selectedPackage.packageInfo.name]=selectedPackage_cves
		for projectName,cves in cves.items():
			if len(cves)==0:
				continue
			haveOutput=True
			print("package: ",end='')
			first=True
			if projectName in project_packages:
				for packageName in project_packages[projectName]:
					if first is True:
						first=False
					else:
						print(", ",end='')
					print(packageName,end='')
				print(" have cve:")
				for cve in cves:
					print(" "+cve['name']+", score: "+str(cve['score']))
	if assumeNo is True or dumpFileOnly is True:
		return False
	if noPackagesWillInstalled is True:
		return True
	if haveOutput is False:
		print("All packages have no CVE")
	print('Are you sure to continue? (y/n)')
	userinput=input()
	if userinput=='y':
		return True
	else:
		print('abort')
	return False

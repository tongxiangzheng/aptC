import getNewInstall
import SourcesListManager
import nwkTools
from loguru import logger as log
from spdx.spdxmain import spdxmain 
import normalize
import json
import requests
import loadConfig

def downloadPackage(selectedPackage):
	return nwkTools.downloadFile(selectedPackage.repoURL+'/'+selectedPackage.fileName,'/tmp/aptC/packages',normalize.normalReplace(selectedPackage.fileName.rsplit('/',1)[1]))

def queryCVE(spdxObj,aptConfigure:loadConfig.aptcConfigure):
	url=aptConfigure.querycveURL
	try:
		response = requests.post(url, json=spdxObj)
	except requests.exceptions.ConnectionError as e:
		print("failed to query CVE: Unable to connect: "+url)
		return {}
	except Exception as e:
		print(f'failed to query CVE: {e}')
	if response.status_code == 200:
		return response.json()
	else:
		print(f'failed to query CVE: Request failed with status code {response.status_code}')
		return {}
def scandeb(command,options,packages,genSpdx=True,saveSpdxPath=None,genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=False):
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
	for selectedPackageName in packages:
		selectedPackage,willInstallPackages=getNewInstall.getNewInstall(selectedPackageName,options,sourcesListManager,dumpFileOnly)
		if selectedPackage is None:
			continue
		if len(willInstallPackages)>0:
			noPackagesWillInstalled=False
		selectedPackageName=selectedPackage.fullName
		packageProvides[selectedPackageName]=willInstallPackages
		depends=dict()
		project_packages=dict()
		for p in willInstallPackages:
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
			if p.packageInfo.name not in project_packages:
				project_packages[p.packageInfo.name]=[]
			project_packages[p.packageInfo.name].append(p.fullName)
		dependsList=list(depends.values())
		packageFilePath=downloadPackage(selectedPackage)
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
		cves=queryCVE(spdxObj,aptConfigure)
		
		selectedPackage_cves=cves[selectedPackage.packageInfo.name]
		for projectName,cves in cves.items():
			if len(cves)==0:
				continue
			if projectName not in project_packages:
				selectedPackage_cves.extend(cves)
		cves[selectedPackage.packageInfo.name]=selectedPackage_cves

		for projectName,cves in cves.items():
			if len(cves)==0:
				continue
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
				cves=set(cves)
				for cve in cves:
					print(" "+cve)
	if assumeNo is True or dumpFileOnly is True:
		return False
	if noPackagesWillInstalled is True:
		return True
	
	print('Are you true to continue? (y/n)')
	userinput=input()
	if userinput=='y':
		return True
	else:
		print('abort')
	return False

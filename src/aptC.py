import sys
import os
import getNewInstall
import SourcesListManager
import nwkTools
from loguru import logger as log
from spdx.spdxmain import spdxmain 
import normalize
import json
import requests
import loadConfig
import scansrc

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
def main(command,options,packages,genSpdx=True,saveSpdxPath=None,genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=False):
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


def core(exec,args,setyes=False):
	cmd=exec
	for arg in args:
		if arg.startswith('--genspdx'):
			continue
		if arg.startswith('--gencyclonedx'):
			continue
		cmd+=" "+arg
		if arg=='-y':
			setyes=False
		
	if setyes is True:
		cmd+=" -y"
	return os.system(cmd)

def parseCommand(args):
	command=None
	options=[]
	packages=[]
	needMerge=False
	for arg in args:
		if arg.startswith('-'):
			if needMerge is True:
				options[-1]+=" "+arg
				needMerge=False
			else:
				options.append(arg)
			if arg=='-o' or arg=='-c' or arg=='-t' or arg=='-a' or arg.endswith('='):
				needMerge=True
		else:
			if arg.startswith('=') or needMerge is True:
				options[-1]+=" "+arg
				needMerge=False
			else:
				if command is None:
					command=arg
				else:
					packages.append(arg)
			if arg.endswith('='):
				needMerge=True
	return command,options,packages

def user_main(exec,args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='-s' or arg=="--simulate" or arg=="--just-print" or arg=="--dry-run" or arg=="--recon" or arg=="--no-act" or arg=="-y":
			errcode=core(exec,args)
			break
	if errcode is None:
		command,options,packages=parseCommand(args)
		if command=='install' or command=='reinstall':
			if main(command,options,packages) is True:
				core(exec,args,setyes=True)
			else:
				errcode=0
		elif command=='genspdx':
			if len(packages)!=2:
				print("unknown usage for apt genspdx")
				return 1
			main(command,options,[packages[0]],genSpdx=True,saveSpdxPath=packages[1],genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=True)
			return 0
		elif command=='gencyclonedx':
			if len(packages)!=2:
				print("unknown usage for apt gencyclonedx")
				return 1
			main(command,options,[packages[0]],genSpdx=False,saveSpdxPath=None,genCyclonedx=True,saveCyclonedxPath=packages[1],dumpFileOnly=True)
			return 0
		elif command=='scansrc':
			errcode=scansrc.scansrc(packages)
	if errcode is None:
		errcode=core(exec,args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[0],sys.argv[1:],True)
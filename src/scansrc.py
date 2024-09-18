import osInfo
import loadConfig
import requests
import RepoFileManager
import SpecificPackage
import SourcesListManager
import normalize
from subprocess import PIPE, Popen
import shutil
import os
from spdx.sourcemain import srcmain
def postFile(file,aptConfigure:loadConfig.aptcConfigure):
	try:
		files = {'file': open(file, 'rb')}
		response = requests.post(aptConfigure.postfileURL,files=files)
	except requests.exceptions.ConnectionError as e:
		print("failed to upload file: Unable to connect: "+aptConfigure.postfileURL)
		return None
	except Exception as e:
		print(f'failed to upload file: {e}')
	if response.status_code == 200:
		data=response.json()
		if data['error']==0:
			return data['token']
		else:
			print("failed to upload file: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to upload file: Request failed with status code {response.status_code}')
		return None
	
def queryBuildInfo(srcFile,srcFile2,osType,osDist,arch,aptConfigure:loadConfig.aptcConfigure):
	src1token=postFile(srcFile,aptConfigure)
	if src1token is None:
		return None
	src2token=None
	if srcFile2 is not None:
		src2token=postFile(srcFile2,aptConfigure)
		if src2token is None:
			return None
	try:
		data={"srcFile":src1token,"srcFile2":src2token,"osType":osType,"osDist":osDist,"arch":arch}
		response = requests.post(aptConfigure.querybuildinfoURL, json=data)
	except requests.exceptions.ConnectionError as e:
		print("failed to query buildInfo: Unable to connect: "+aptConfigure.querybuildinfoURL)
		return None
	except Exception as e:
		print(f'failed to query buildInfo: {e}')
	if response.status_code == 200:
		data=response.json()
		if data['error']==0:
			return data['buildinfo']
		else:
			print("failed to upload file: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to query buildInfo: Request failed with status code {response.status_code}')
		return None
def setInstalledPackagesStatus(sourcesListManager):
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
			continue
		version_release=info.split(' ')[1].split('-')
		version=version_release[0].split(':')[-1]
		release=None
		if len(version_release)>1:
			release=version_release[1]
		package=sourcesListManager.getSpecificPackage(packageName,dist,version,release)
		if package is not None:
			package.status="installed"
def scansrc(srcs):
	if len(srcs)==1:
		srcFile=srcs[0]
		srcFile2=None
	elif len(srcs)==2:
		srcFile=srcs[0]
		srcFile2=srcs[1]
	else:
		print("usage: apt scansrc <src> or apt scansrc <orig> <patch>")
		return 0
	osType=osInfo.OSName
	osDist=osInfo.OSDist
	arch=osInfo.arch
	aptConfigure=loadConfig.loadConfig()
	if aptConfigure is None:
		print('ERROR: cannot load config file in /etc/aptC/config.json, please check config file ')
		return 1
	buildInfo=queryBuildInfo(srcFile,srcFile2,osType,osDist,arch,aptConfigure)
	if buildInfo is None:
		return 1
	buildInfo=buildInfo.split('\n')
	packages=RepoFileManager.parseDEBPackages(buildInfo,osType,osDist,"")
	if len(packages)==0:
		print("ERROR::failed to get package info: unknown fail")
		return 1
	sourcesListManager=SourcesListManager.SourcesListManager()
	entryMap=SpecificPackage.EntryMap()
	setInstalledPackagesStatus(sourcesListManager)
	repoPackages=sourcesListManager.getAllPackages()
	
	for package in packages:
		package.status="installed"
		package.registerProvides(entryMap)
	for package in repoPackages:
		package.registerProvides(entryMap)
	
	for package in repoPackages:
		package.findRequires(entryMap)
	for package in packages:
		print(package.fullName)
		package.findRequires(entryMap)
	for package in packages:
		depset=set()
		print(package.fullName)
		SpecificPackage.getDependes(package,depset)
		depends=dict()
		for p in depset:
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
		dependsList=list(depends.values())
		print(normalize.normalReplace(package.fullName))
		srcPath=os.path.join("/tmp/aptC/",normalize.normalReplace(os.path.abspath(srcFile)))
		print(srcPath)
		shutil.copyfile(srcFile,srcPath)
		srcmain(normalize.normalReplace(package.fullName),srcPath,dependsList,'spdx',".")
		print("generate SPOM for "+package.fullName)
	return 0

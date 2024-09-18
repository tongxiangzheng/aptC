import os
import sys
import re
DIR = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(DIR,"deb"))
sys.path.append(os.path.join(DIR,"lib"))


class ExternalDependency:
	name:str
	version:str
	gitLink:str
	purl:str
	def __init__(self,name,version,gitLink,purl):
		self.name = name
		self.version = version
		self.gitLink = gitLink
		self.purl = purl
def srcmain(packageName,packageFilePath,dependsList,sbomType='spdx',saveSbomPath='/tmp/aptC/source'):
    ExternalDependencies=getExternalDependencies(dependsList)
	# resPath=packageFilePath+".spdx.json"
	if sbomType == 'spdx':
		resPath = saveSbomPath+packageName+".spdx.json"
	if sbomType == 'cyclonedx':
		resPath = saveSbomPath+packageName+".cyclonedx.json"
	BinaryDebAnalysis.binaryDebScan(packageFilePath,resPath,ExternalDependencies,sbomType)
	return resPath
#获取外部依赖
def getExternalDependencies(dependsList):
	
	ExternalDependencies = []
	
	print("解析")
	
	for depends in dependsList:
		
		#获取dependency实例数组
	   
		name = depends['name']
		version = depends['version']
		purl = depends['purl']
		gitLink = ''
		if 'gitLink' in depends:
			gitLink = str(depends['gitLink'])
		Dependency = ExternalDependency(
			name = name,
			version= version,
			gitLink= gitLink,
			purl=purl
		)
		ExternalDependencies.append(Dependency)
		#print("require:",require)
		print("name:",name)
		print("version",version)
		print('gitLink',gitLink)
		print('purl',purl)

	return ExternalDependencies
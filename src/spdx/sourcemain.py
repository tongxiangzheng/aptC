import os
import sys
import re
DIR = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(DIR,"deb"))
sys.path.append(os.path.join(DIR,"lib"))
import SyftAnalysis

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

def srcmain(packageName,packageFilePath,dependsList,sbomType='spdx',saveSbomPath='/tmp/aptC/src'):
	#print("binary deb file at: "+packageFilePath)
	#print("purl for: "+packageName)
	#for depends in dependsList:
	#	print(depends)
	ExternalDependencies=getExternalDependencies(dependsList)
	if saveSbomPath is None:
		saveSbomPath='/tmp/aptC/src'
	if sbomType == 'spdx':
		resPath = os.path.join(saveSbomPath,packageName+".spdx.json")
	if sbomType == 'cyclonedx':
		resPath = os.path.join(saveSbomPath,packageName+".cyclonedx.json")
	SyftAnalysis.Scan(packageFilePath,resPath,ExternalDependencies,sbomType)
	return resPath
#获取外部依赖
def getExternalDependencies(dependsList):
	
	ExternalDependencies = []
	
	#print("解析")
	# print('进入purl装载阶段')
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
		#print("name:",name)
		#print("version",version)
		#print('gitLink',gitLink)
		# print('purl',purl)

	return ExternalDependencies
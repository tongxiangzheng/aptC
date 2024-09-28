from collections import defaultdict
from loguru import logger as log
from PackageInfo import PackageInfo
import DscParser

def firstNumber(rawstr)->str:
	res=""
	for c in rawstr:
		if c.isdigit() is True or c == '.':
			res+=c
		else:
			break
	if res.endswith('.'):
		res=res[:-1]
	return res
def compareVersion(version1,version2):
	# -1: version1<version2 0:version1==version2 1:version1>version2
	v1=version1.split('.')
	v2=version2.split('.')
	for i in range(min(len(v1),len(v2))):
		if v1[i].isdigit():
			v1i=int(v1[i])
		else:
			v1i=v1[i]
		if v2[i].isdigit():
			v2i=int(v2[i])
		else:
			v2i=v2[i]
		if type(v1i)!=type(v2i):
			v1i=int(firstNumber(v1[i]))
			v2i=int(firstNumber(v2[i]))
		if v1i<v2i:
			return -1
		if v1i>v2i:
			return 1
	if len(v1)<len(v2):
		return -1
	if len(v1)>len(v2):
		return 1
	return 0
def compareEntry(a,b):
	v1=compareVersion(a.version,b.version)
	if v1!=0:
		return v1
	if a.release is None or b.release is None:
		return 0
	return compareVersion(a.release,b.release)
class PackageEntrys:
	def __init__(self):
		self.entrys=[]
		self.qualified=False
		#表示或逻辑，entrys匹配任意一个即可
	def addEntry(self,entry):
		self.entrys.append(entry)
		entry.fatherNode=self
	def setQualified(self):
		self.qualified=True
	def queryIsQualified(self):
		return self.qualified
class PackageEntry:
	def __init__(self,name:str,flags:str,version:str,release:str):
		self.name=name
		self.flags=flags
		if version is not None:
			version=version.split(':')[-1]
		self.version=version
		self.release=release
		self.fatherNode=None
	def checkMatch(self,dist):
		if self.flags is None or dist.flags is None:
			return True
		if dist.version is None:
			log.warning(self.name+" have problem: dist version is None")
			return True
		flags=self.flags
		if self.flags=='EQ' and dist.flags!='EQ':
			if dist.flags=='LE':
				flags='GE'
			elif dist.flags=='LT':
				flags='GT'
			elif dist.flags=='GE':
				flags='LE'
			elif dist.flags=='GT':
				flags='LT'
		if flags=='EQ':
			if compareEntry(dist,self)==0:
				return True
			else:
				return False
		elif flags=='LE':
			if compareEntry(dist,self)==-1:
				return True
			else:
				return False
		elif flags=='LT':
			if compareEntry(dist,self)<=0:
				return True
			else:
				return False
		elif flags=='GE':
			if compareEntry(dist,self)==1:
				return True
			else:
				return False
		elif flags=='GT':
			if compareEntry(dist,self)>=0:
				return True
			else:
				return False
	def setQualified(self):
		self.fatherNode.setQualified()
	def queryIsQualified(self):
		return self.fatherNode.queryIsQualified()
	def dump(self):
		res=self.name
		if self.flags=='EQ':
			res+=' = '
		elif self.flags=='LE':
			res+=' <= '
		elif self.flags=='LT':
			res+=' < '
		elif self.flags=='GE':
			res+=' >= '
		elif self.flags=='GT':
			res+=' > '
		
		if self.version is not None:
			res+=self.version
		if self.release is not None:
			res+='-'+self.release
		return res
	
def defaultNoneList():
	return []
class EntryMap:
	def __init__(self):
		self.provideEntryPackages=defaultdict(defaultNoneList)
	def registerEntry(self,entry:PackageEntry,package):
		self.provideEntryPackages[entry.name].append((package,entry))
	def queryRequires(self,packageName,requireName:str,entrys:list,mustInstalled:bool):
		# requireName==entrys[i].name
		infoList=self.provideEntryPackages[requireName]
		res=[]
		for info in infoList:
			package=info[0]
			if mustInstalled is True:
				if package.status=='uninstalled':
					continue
			provideEntry=info[1]
			isMatch=True
			for entry in entrys:
				if entry.checkMatch(provideEntry):
					continue
				else:
					isMatch=False
				
			if isMatch is True:
				res.append(package)
		#print(" "+entry.name)
		#for r in res:
			#print("  "+r[0].fullName)
		if len(res)<=1 or mustInstalled is True:
			return res
		
		name=res[0].packageInfo.name
		versionEntry=res[0].getSelfEntry()
		res2=res[0]
		for r in res[1:]:
			if(name!=r.packageInfo.name):
				#log.warning("failed to decide require package for: "+entry.name+" in pacakge: "+packageName)
				#for r1 in res:
				#	log.info(" one of provider is: "+r1.fullName)
				return [res[0]]
			if compareEntry(versionEntry,r.getSelfEntry())==-1:
				versionEntry=r.getSelfEntry()
				res2=r
		return [res2]
def getDependes_dfs(package,dependesSet:set,entryMap,includeInstalled):
	if package in dependesSet:
		return
	if includeInstalled is False and package.status=='installed':
		return
	if package.status=='uninstalled':
		package.status='willInstalled'
	dependesSet.add(package)
	package.findRequires(entryMap)
	if includeInstalled is True:
		print("%"+package.fullName,package.packageInfo.version,package.packageInfo.release,package.status)
		print("%",end="")
		for p in package.requirePointers:
			print(" "+p.fullName,end="")
		print("")
	for p in package.requirePointers:
		getDependes_dfs(p,dependesSet,entryMap,includeInstalled)	
def getDependsPrepare(entryMap,package):
	depset=set()
	getDependes_dfs(package,depset,entryMap,False)
	return depset
def getDepends(entryMap,package,depset=set()):
	getDependes_dfs(package,depset,entryMap,True)
	return depset
def defaultCVEList():
	return 0
class SpecificPackage:
	def __init__(self,packageInfo:PackageInfo,fullName:str,provides:list,requires:list,arch:str,source,status="uninstalled",repoURL=None,fileName=""):
		provides.append(PackageEntry(fullName,"EQ",packageInfo.version,packageInfo.release))
		self.packageInfo=packageInfo
		self.fullName=fullName
		self.providesInfo=provides
		self.requiresInfo=requires
		self.status=status
		self.arch=arch
		self.providesPointers=[]
		self.requirePointers=[]
		self.repoURL=repoURL
		self.fileName=fileName
		self.getGitLinked=False
		self.source=source
		self.registerProvided=False
		self.haveFoundRequires=False
	def addProvidesPointer(self,package):
		#无需手动调用，addRequirePointer自动处理
		self.providesPointers.append(package)
	def addRequirePointer(self,package):
		self.requirePointers.append(package)
		package.addProvidesPointer(self)
	def registerProvides(self,entryMap:EntryMap)->None:
		if self.registerProvided is True:
			return
		self.registerProvided=True
		for provide in self.providesInfo:
			entryMap.registerEntry(provide,self)
	def findRequires(self,entryMap:EntryMap)->None:
		if self.haveFoundRequires is True:
			return
		self.haveFoundRequires=True
		requirePackageSet=set()
		requires=dict()
		for requireEntrys in self.requiresInfo:
			for require in requireEntrys.entrys:
				if require.name not in requires:
					requires[require.name]=[]
				requires[require.name].append(require)
		checkedRequireItems=set()
		for requireEntrys in self.requiresInfo:
			for require in requireEntrys.entrys:
				requireName=require.name
				if requireName in checkedRequireItems:
					continue
				#print('-----')
				#print(requireName)
				checkedRequireItems.add(requireName)
				requireList=requires[requireName]
				res=entryMap.queryRequires(self.fullName,requireName,requireList,True)
				for r in res:
					if r not in requirePackageSet:
						#print(res.fullName)
						for require in requireList:
							require.setQualified()
						self.addRequirePointer(r)
						requirePackageSet.add(r)
		if self.status=="installed":
			return
		checkedRequireItems=set()
		for requireEntrys in self.requiresInfo:
			for require in requireEntrys.entrys:
				requireName=require.name
				if requireName in checkedRequireItems:
					continue
				#print('-----')
				#print(requireName)
				checkedRequireItems.add(requireName)
				requireList=requires[requireName]
				needSolve=False
				for require in requireList:
					if require.queryIsQualified() is False:
						needSolve=True
						break
				#print(needSolve)
				if needSolve is False:
					continue
				res=entryMap.queryRequires(self.fullName,requireName,requireList,False)
				for r in res:
					if r not in requirePackageSet:
						#print(res.fullName)
						for require in requireList:
							require.setQualified()
						self.addRequirePointer(r)
						requirePackageSet.add(r)
	def dump(self):
		print(self.fullName,self.packageInfo.version,self.packageInfo.release,self.status)
		for p in self.requirePointers:
			print(" "+p.fullName,end="")
		print("")
	def getSelfEntry(self):
		return self.providesInfo[-1]
	def setGitLink(self):
		if self.getGitLinked is True:
			return
		gitLink=DscParser.getGitLink(self)
		self.getGitLinked=True
		self.packageInfo.gitLink=gitLink
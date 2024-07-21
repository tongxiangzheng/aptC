import RepoFileManager
import SpecificPackage
from loguru import logger as log
class sourceConfigItem:
	def __init__(self,url,dist,channel):
		self.url=url
		self.url_without_prefix=url.split('//')[1].split('/')[0]
		self.dist=dist
		self.channel=channel
		self.repoFiles=dict()
	def getFilePath(self,arch):
		return '/var/lib/apt/lists/'+self.url_without_prefix+'_ubuntu_dists_'+self.dist+'_'+self.channel+"_binary-"+arch+"_Packages"
	def getGitLink(self,name,arch):
		#abandon
		log.warning("abandon")
		repoPath=self.getFilePath(arch)
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(self.url,repoPath,"ubuntu",self.dist)
		return self.repoFiles[repoPath].getGitLink(name)
	def getSpecificPackage(self,name,version,release,arch)->SpecificPackage.SpecificPackage:
		repoPath=self.getFilePath(arch)
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(self.url,repoPath,"ubuntu",self.dist)
		return self.repoFiles[repoPath].queryPackage(name,version,release)
class SourcesListManager:
	def __init__(self):
		with open('/etc/apt/sources.list') as f:
			data=f.readlines()
		self.binaryConfigItems=dict()
		self.srcConfigItems=dict()
		for info in data:
			info=info.split('#',1)[0].strip()
			if info.startswith('deb '):
				item=info.split(' ')
				url=item[1]
				dist=item[2]
				configItems=[]
				for channel in item[3:]:
					configItems.append(sourceConfigItem(url,dist,channel))
				self.binaryConfigItems[dist]=configItems
			elif info.startswith('deb-src '):
				item=info.split(' ')
				url=item[1]
				dist=item[2]
				configItems=[]
				for channel in item[3:]:
					configItems.append(sourceConfigItem(url,dist,channel))
				self.srcConfigItems[dist]=configItems
				
	def setGitLink(self,name,arch,dist):
		#abandon
		log.warning("abandon")
		for configItem in self.binaryConfigItems[dist]:
			res=configItem.getGitLink(name,arch)
			if res is not None:
				return res
		return None
	def getSpecificPackage(self,name,dist,version,release,arch)->SpecificPackage.SpecificPackage:
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release,arch)
			if specificPackage is not None:
				return specificPackage
		return None
	def getSpecificSrcPackage(self,name,dist,version,release,arch)->SpecificPackage.SpecificPackage:
		for configItem in self.binaryConfigItems[dist]:
			specificPackage=configItem.getSpecificPackage(name,version,release,arch)
			if specificPackage is not None:
				return specificPackage
		return None
	
	def getBinaryDebPackage(self,packageInfo):
		pass

import RepoFileManager
import repodataParser
class sourceConfigItem:
	def __init__(self,url,dist,channel):
		self.url=url
		self.url_without_prefix=url.split('//')[1][:-1]
		self.dist=dist
		self.channel=channel
		self.repoFiles=dict
	def getFilePath(self,arch):
		return '/var/lib/apt/lists'+self.url_without_prefix+'_ubuntu_dists_'+self.dist+'_'+self.channel+"/binary-"+arch+"_Packages"
	def getGitLink(self,name,arch):
		repoPath=self.getFilePath(arch)
		if repoPath not in self.repoFiles:
			self.repoFiles[repoPath]=RepoFileManager.RepoFileManager(self.url,repoPath,"ubuntu",self.dist)
		self.repoFiles[repoPath].getGitLink(name)
class SourceListManager:
	def __init__(self):
		with open('/etc/apt/sources.list') as f:
			data=f.readlines()
		self.sourceConfigItems=dict()
		for info in data:
			info=info.split('#',1)[0].strip()
			if info.startswith('deb '):
				item=info.split(' ')
				url=item[1]
				dist=item[2]
				configItems=[]
				for channel in item[3:]:
					configItems.append(sourceConfigItem(url,dist,channel))
				self.sourceConfigItems[dist]=configItems
	def getGitLink(self,name,dist,arch):
		for configItem in self.sourceConfigItems[dist]:
			res=configItem.getGitLink(name,arch)
			if res is not None:
				return res
		return None

import osInfo
import loadConfig
import requests
import RepoFileManager
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
		print(data)
		if data['error']==0:
			return data['buildinfo']
		else:
			print("failed to upload file: failinfo: "+data['errorMessage'])
			return None
	else:
		print(f'failed to query buildInfo: Request failed with status code {response.status_code}')
		return None
	
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
	buildInfos=queryBuildInfo(srcFile,srcFile2,osType,osDist,arch,aptConfigure)
	if buildInfos is None:
		return 1
	for buildInfo in buildInfos:
		buildInfo=buildInfo.split('\n')
		print(buildInfo)
		packages=RepoFileManager.parseDEBPackages(buildInfo,osType,osDist,"")
	return 0

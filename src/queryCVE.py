import loadConfig
import requests
import json
def queryCVE(spdxObj,aptConfigure:loadConfig.aptcConfigure):
	url=aptConfigure.querycveURL
	try:
		response = requests.post(url, json=spdxObj)
	except requests.exceptions.ConnectionError as e:
		print("failed to query CVE: Unable to connect: "+url)
		return None
	except Exception as e:
		print(f'failed to query CVE: {e}')
		return None
	if response.status_code == 200:
		return response.json()
	else:
		print(f'failed to query CVE: Request failed with status code {response.status_code}')
		return None
	
def queryCVECli(packages,options):
	aptConfigure=loadConfig.loadConfig()
	if aptConfigure is None:
		print('ERROR: cannot load config file in /etc/aptC/config.json, please check config file ')
		return False
	if len(packages)==0:
		print("usage: apt queryCVE <spdxfile>")
		return False
	spdxPath=packages[0]
	with open(spdxPath,"r") as f:
		spdxObj=json.load(f)
	cves=queryCVE(spdxObj,aptConfigure)
	haveOutput=False
	if cves is not None:
		for projectName,cves in cves.items():
			if len(cves)==0:
				continue
			haveOutput=True
			print("package: "+projectName)
			print(" have cve:")
			for cve in cves:
				print(" "+cve['name']+", score: "+str(cve['score']))
	else:
		haveOutput=True
	if haveOutput is False:
		print("All packages have no CVE")
	return False
import pandas as pd
import os
import json
import spdxReader

df = pd.DataFrame(columns=['项目名','软件包名','软件包版本', 'apt输出的未安装依赖数量+分析得出的已安装依赖数量','分析得出的未安装和已安装依赖数量'])
for fileDir in os.listdir("./src"):
	for file in os.listdir("./src/"+fileDir):
		projName=file.split(".")[0]
		projVersion=None
		file=os.path.join(fileDir,file)
		if not os.path.isfile("./binary/"+file):
			#print("")
			#print(file+" not in binary")
			continue
		srcres=dict()
		binres=dict()
		with open("./src/"+file) as f:
			spdxObj=json.load(f)
			res=spdxReader.parseSpdxObj(spdxObj)
			for s in res:
				srcres[s.name]=s
		with open("./binary/"+file) as f:
			spdxObj=json.load(f)
			res=spdxReader.parseSpdxObj(spdxObj)
			for s in res:
				binres[s.name]=s
				if s.name==fileDir:
					projVersion=s.version
					if s.release is not None:
						projVersion+="-"+s.release
		df.loc[len(df)] = [fileDir,projName,projVersion,len(binres),len(srcres)]
df.to_csv("res.csv", index=False,encoding='utf_8_sig')
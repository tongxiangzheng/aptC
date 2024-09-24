import os
import json
import spdxReader
for file in os.listdir("./src"):
	if not os.path.isfile("./binary/"+file):
		print(file+"not in binary")
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

	needOutput=False
	for s in srcres.values():
		if s.name not in binres:
			needOutput=True
			break
	print("--")
	for s in binres.values():
		if s.name not in srcres:
			needOutput=True
			break
	if needOutput is False:
		continue
	print("")
	print(file)
	print("src:")
	for s in srcres.values():
		if s.name not in binres:
			print(s.name,s.version,s.release)
	print("binary:")
	for s in binres.values():
		if s.name not in srcres:
			print(s.name,s.version,s.release)
	
import os
import json
import spdxReader
for fileDir in os.listdir("./src"):
	if not os.path.isdir("./binary/"+fileDir):
		continue
	for file in os.listdir("./src/"+fileDir):
		if not os.path.isfile("./binary/"+fileDir+"/"+file):
			print("in "+fileDir+":")
			print(" "+file+" not in binary")
			
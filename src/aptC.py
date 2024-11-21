import sys
import os
import scanDeb
import scanBin
import scanSrc
import queryCVE
def runApt(exec,args,setyes=False):
	cmd=exec
	for arg in args:
		if arg.startswith('--genspdx'):
			continue
		if arg.startswith('--gencyclonedx'):
			continue
		if arg=='-n':
			continue
		cmd+=" "+arg
		if arg=='-y':
			setyes=False
		
	if setyes is True:
		cmd+=" -y"
	return os.system(cmd)

def parseCommand(args):
	command=None
	options=[]
	packages=[]
	needMerge=False
	for arg in args:
		if arg.startswith('-'):
			if needMerge is True:
				options[-1]+=" "+arg
				needMerge=False
			else:
				options.append(arg)
			if arg=='-o' or arg=='-c' or arg=='-t' or arg=='-a' or arg.endswith('='):
				needMerge=True
		else:
			if arg.startswith('=') or needMerge is True:
				options[-1]+=" "+arg
				needMerge=False
			else:
				if command is None:
					command=arg
				else:
					packages.append(arg)
			if arg.endswith('='):
				needMerge=True
	return command,options,packages

def user_main(exec,args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='-s' or arg=="--simulate" or arg=="--just-print" or arg=="--dry-run" or arg=="--recon" or arg=="--no-act" or arg=="-y":
			errcode=runApt(exec,args)
			break
	if errcode is None:
		command,options,packages=parseCommand(args)
		if command=='install' or command=='reinstall':
			if scanDeb.scanDeb(command,options,packages) is True:
				errcode=runApt(exec,args,setyes=True)
			else:
				errcode=0
		elif command=='genspdx':
			if len(packages)<2:
				print("unknown usage for apt genspdx")
				return 1
			scanDeb.scanDeb(command,options,packages[:-1],genSpdx=True,saveSpdxPath=packages[-1],genCyclonedx=False,saveCyclonedxPath=None,dumpFileOnly=True)
			return 0
		elif command=='gencyclonedx':
			if len(packages)<2:
				print("unknown usage for apt gencyclonedx")
				return 1
			scanDeb.scanDeb(command,options,packages[:-1],genSpdx=False,saveSpdxPath=None,genCyclonedx=True,saveCyclonedxPath=packages[1],dumpFileOnly=True)
			return 0
		elif command=='scanbin':
			errcode=scanBin.scanBin(packages,options)
		elif command=='scansrc':
			errcode=scanSrc.scanSrc(packages,options)
		elif command=='querycve':
			errcode=queryCVE.queryCVECli(packages,options)
	if errcode is None:
		errcode=runApt(exec,args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[0],sys.argv[1:],True)
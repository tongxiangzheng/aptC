import sys
import os
import getNewInstall
import SourcesListManager
from loguru import logger as log
def main(command,options,packages):
	sourcesListManager=SourcesListManager.SourcesListManager()
	packageProvides=dict()
	for selectedPackageName in packages:
		selectedPackage=None
		willInstallPackages=getNewInstall.getNewInstall(selectedPackageName,options,sourcesListManager)
		packageProvides[selectedPackageName]=willInstallPackages
		purls=set()
		for p in willInstallPackages:
			purls.add(p.packageInfo.dumpAsPurl())
			if p.fullName==selectedPackageName:
				selectedPackage=p
		purlList=list(purls)
		if selectedPackage==None:
			log.warning("cannot find package for "+selectedPackageName)
		print(selectedPackageName+":")
		for purl in purlList:
			print(" "+purl)

	return False


def core(args):
	cmd="/usr/bin/apt"
	setyes=False
	for arg in args:
		cmd+=" "+arg
		if arg=='-y':
			setyes=True
	if setyes is False:
		cmd+=" -y"
	return os.system(cmd)
def parseCommand(args):
	command=None
	options=[]
	packages=[]
	for arg in args:
		if arg.startswith('-'):
			options.append(arg)
		else:
			if command is None:
				command=arg
			else:
				packages.append(arg)
	return command,options,packages
def user_main(args, exit_code=False):
	errcode=None
	for arg in args:
		if arg=='-s':
			errcode=core(args)
			break
	if errcode is None:
		command,options,packages=parseCommand(args)
		if command=='install' or command=='reinstall':
			if main(command,options,packages) is False:
				errcode=1
	if errcode is None:
		errcode=core(args)

	if exit_code:
		sys.exit(errcode)
	return errcode

if __name__ == '__main__':
	user_main(sys.argv[1:],True)
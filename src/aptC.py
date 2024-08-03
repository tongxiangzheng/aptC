import sys
import os
import getNewInstall
import SourcesListManager
import nwkTools
from loguru import logger as log
from spdx.spdxmain import spdxmain 
import normalize
def downloadPackage(selectedPackage):
	return nwkTools.downloadFile(selectedPackage.repoURL+'/'+selectedPackage.fileName,'/tmp/aptC/packages',normalize.normalReplace(selectedPackage.fileName.rsplit('/',1)[1]))
	
def main(command,options,packages):
	sourcesListManager=SourcesListManager.SourcesListManager()
	packageProvides=dict()
	for selectedPackageName in packages:
		selectedPackage,willInstallPackages=getNewInstall.getNewInstall(selectedPackageName,options,sourcesListManager)
		if selectedPackage is None:
			continue
		selectedPackageName=selectedPackage.fullName
		packageProvides[selectedPackageName]=willInstallPackages
		depends=dict()
		for p in willInstallPackages:
			depends[p.packageInfo.name+'@'+p.packageInfo.version]=p.packageInfo.dumpAsDict()
		dependsList=list(depends.values())
		packageFilePath=downloadPackage(selectedPackage)
		spdxPath=spdxmain(selectedPackageName,packageFilePath,dependsList)
		print(spdxPath)
	return False


def core(exec,args):
	cmd=exec
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
		if arg=='-s' or arg=="--simulate" or arg=="--just-print" or arg=="--dry-run" or arg=="--recon" or arg=="--no-act":
			errcode=core(exec,args)
			break
	if errcode is None:
		command,options,packages=parseCommand(args)
		if command=='install' or command=='reinstall':
			if main(command,options,packages) is False:
				errcode=1
	if errcode is None:
		errcode=core(exec,args)

	if exit_code:
		sys.exit(errcode)
	return errcode

#if __name__ == '__main__':
#	user_main(sys.argv[0],sys.argv[1:],True)
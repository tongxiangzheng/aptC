import os,sys
DIR=os.path.split(os.path.abspath(__file__))[0]
sys.path.insert(0,os.path.join(DIR,'..','src'))
import RepoFileManager

repoFileManager=RepoFileManager.RepoFileManager("","./jammy-updates","ubuntu","jammy-updates")

for package in repoFileManager.getAllPackages():
	if package.packageInfo.name.startswith("linux") or package.packageInfo.name.startswith("gcc") or package.packageInfo.name.startswith("llvm") or package.packageInfo.name.startswith("texlive") or package.packageInfo.name.startswith("language"):
		continue
	if package.packageInfo.release is None:
		print(package.packageInfo.name,package.fullName,package.packageInfo.version)
	else:
		print(package.packageInfo.name,package.fullName,package.packageInfo.version,package.packageInfo.release)
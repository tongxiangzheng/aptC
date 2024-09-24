import json
import os
import subprocess

from spdx.deb.Unpack import  extract_archive
import numpy as  np

import os
import re

from spdx.Utils.convertSbom import convertSpdx,convertSpdx_Deb_syft11,convertCyclonedx
from spdx.Utils.extract import remove_file_extension
from spdx.Utils.java.mavenAnalysis import AnalysisVariabele
from collections import defaultdict

syft_path = '/usr/share/aptC/spdx/syft/syft'
syft_path11 = '/usr/share/aptC/spdx/syft11/syft'
#针对Deb包进行解压缩
def extract_deb(deb_path):
    dir_Path = re.sub(r'\.deb$', '', deb_path)
    #print(dir_Path)
    # mkdir_command = f'mkdir {dir_Path}'
    #使用命令解压
    command_extract = f"dpkg -x {deb_path} {dir_Path}"
    os.system(command_extract)
    return dir_Path

#获取外部依赖
def getExternalDependenies(scan_path):
    dpkg_command = f'dpkg -I {scan_path}'
    dpkg_output = subprocess.check_output(dpkg_command,shell=True)
    # print(dpkg_output)
    dpkg_output_json = json.loads(dpkg_output.decode())
    #print(dpkg_output_json)
#针对二进制的deb包做分析
def binaryDebScan(inputPath,output_file,ExterDependencies,sbomType):
    #获取外部依赖
    
    #获取内部依赖：
    scan_path = extract_deb(inputPath)
    project_name = scan_path
    # 生成syft普通json
    command_syft = f"{syft_path11} scan  {scan_path} -o json"
    p = subprocess.Popen(command_syft, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    syft_output, stderr = p.communicate()
    syft_json = json.loads(syft_output.decode())
    tempath = scan_path + '-syft.json'
    with open(tempath, "w") as f:
        json_string =json.dumps(syft_json,indent=4, separators=(',', ': '))
        f.write(json_string)
    if sbomType == 'spdx':
    # convertSpdx(syft_json, project_name, output_file, ExterDependencies)
        convertSpdx_Deb_syft11(syft_json, project_name, output_file, ExterDependencies)
    if sbomType == 'cyclonedx':
        convertCyclonedx(syft_json,project_name,output_file,ExterDependencies)

# scan_path = "/home/jiliqiang/Deb/deb/libopencensus-java/"
# output_file = "/home/jiliqiang/Deb/deb/spdx_sbom/my_spdx_document.spdx.json"
#binaryDebScan(scan_path,output_file)
#scan_path = "/home/jiliqiang/Deb/deb/libopencensus-java_0.24.0+ds-1_all.deb"
#getExternalDependenies(scan_path)

import json
import os
import subprocess

from Deb.Unpack import  extract_archive
import numpy as  np

import os
import re

from Utils.convertSbom import convertSpdx, convertCyclonedx
from Utils.extract import remove_file_extension
from Utils.java.mavenAnalysis import AnalysisVariabele
from collections import defaultdict

def is_source_code_file(filename):
    return bool(re.match(r"\.(py|java|c|cpp|js|go|swift|rs|php)$", filename))

def is_config_file(filename):
    return bool(re.match(r"\.(ini|json|yaml|toml|xml|conf|spec|install|control)$", filename))

def find_folder_with_control_file(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if "control" in file_name:
                return root
    return None

# # 使用示例
# start_folder = "/path/to/starting/folder"
# result = find_folder_with_control_file(start_folder)
#
# if result:
#     print("包含名字中含有 'control' 的文件的文件夹路径是:", result)
# else:
#     print("未找到包含名字中含有 'control' 的文件的文件夹")



#调用syft分析路径下的deb包源码文件
# 定义路径
# base_path = '/home/jiliqiang/SCA_Code/Deb_package_src'

syft_path = '/home/jiliqiang/SCA_Tools/Syft/./syft'
#syft_path = '/home/jiliqiang/SCA_Tools/Syft/syft_1.4.1/./syft'
# extract_dir = "/home/jiliqiang/Rpm_Deb/Deb/Deb_exact"
def Extract(base_path,extract_dir):
    analysis_paths = []
    # 遍历路径下的压缩包
    for root, dirs, files in os.walk(base_path):

        for file in files:

            if file.endswith('.zip') or file.endswith('.rar') or file.endswith('.tar') or file.endswith(
                    '.gz') or file.endswith('.bz2'):
                # 获取压缩包的完整路径
                zip_path = os.path.join(root, file)
                print("处理压缩包：", zip_path)
                # 解压压缩包：
                result = extract_archive(zip_path, zip_path,extract_dir)

                ##找到分析路径
                # analysis_path = find_folder_with_control_file(result)
                #analysis_path = result
                analysis_paths.append(result)
    return analysis_paths
#分析的是deb包的源代码文件，zip形式
def Analysis(analysis_paths):
    for analysis_path in analysis_paths:
        #analysis_path=/home/jiliqiang/Rpm_Deb/Deb/Deb_exact/activemq-master
        #分析整体的json
        command = f"{syft_path} scan  {analysis_path} -o json"
        output = subprocess.check_output(command, shell=True)
        print("整体")
        print(output.decode())
        overView_json = json.loads(output.decode())

        for art in overView_json['artifacts']:
            print(art['name'])
        #分析局部的json
        # 遍历路径下的压缩包
        for root, dirs, files in os.walk(analysis_path):

            for file in files:

                if is_source_code_file(file):
                    print("处理源代码文件")
                if is_config_file(file):
                    print("配置文件")
                if file.endswith('.zip') or file.endswith('.rar') or file.endswith('.tar') or file.endswith(
                        '.gz') or file.endswith('.bz2'):
                    # 获取压缩包的完整路径
                    zip_path = os.path.join(root, file)
                    print("处理压缩包：", zip_path)
                    # 解压压缩包：
                    result = extract_archive(zip_path, zip_path)

                    ##找到分析路径
                    # analysis_path = find_folder_with_control_file(result)
                    analysis = result
                    # 执行处理压缩包的命令
                    command = f"{syft_path} scan  {analysis} -o json"
                    output = subprocess.check_output(command, shell=True)
                    print("局部压缩包")
                    print(output.decode())
                    #合并json文件
class ExternalDependency:
    name:str
    version:str
    def __init__(self,name,version):
        self.name = name
        self.version = version

def parse_control_file(file_path):
    """
    解析 "control" 文件,并返回一个包含文件信息的字典。

    参数:
    file_path (str): "control" 文件的路径。

    返回:
    dict: 包含文件信息的字典,键为字段名,值为字段值。
    """
    control_info = defaultdict(list)

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                if ':' in line:
                    field, valuelist = line.split(':', 1)
                    parts =  valuelist.split(",")
                    for value in parts:
                        if(value):
                            control_info[field.strip()].append(value.strip())
                else:
                    parts = line.split(",")
                    for value in parts:
                        if(value):
                            control_info[field.strip()].append(value)
    # print(control_info['Build-Depends'])
    return dict(control_info)

#从control文件中提取外部依赖信息
def findExterDependency(scan_path):
    control_path_path =[]
    ExterDependencies = []
    #control_files ={}
    for root,dirs,files in os.walk(scan_path):
        for file in files:
            if file.endswith("control"):
                file_path= os.path.join(root,file)
                control_path_path.append(file_path)
                with open(file_path, 'r') as f:
                    content = f.read()
                    control_data= parse_control_file(file_path)
                    #print(control_data['Build-Depends'])
                    try:
                        dependencyInfo = control_data['Build-Depends']
                        for dependency in dependencyInfo:
                            if dependency:
                                space_index = dependency.find(" ")
                                dependency_name = dependency[:space_index]
                                print(dependency_name)
                                exterDependency = ExternalDependency(
                                    name=dependency_name.replace("+",""),
                                    version="12",
                                )
                                ExterDependencies.append(exterDependency)
                    except KeyError:
                        print("Build-Depends键不存在")
                    # for dependency in control_data['Build-Depends']:
                    #     if dependency:
                    #         print(dependency)
                    #         space_index = dependency.find(" ")
                    #         dependency_name= dependency[:space_index]
                    #         exterDependency= ExternalDependency(
                    #             name = dependency_name,
                    #             version = "12",
                    #         )
                    #         ExterDependencies.append(exterDependency)
    return ExterDependencies
                    # try:
                    #     #control_files[file_path] = json.loads(content)
                    #     controlJson= json.loads(content)
                    #     print(controlJson)
                    # except json.JSONDecodeError:
                    #     print(f"Error parsing {file_path} as JSON.")

#我们在efda数据集上进行分析，得到结果
#scan_path 是扫描项目的路径，deb源码包
#output_file 指定要保存的文件路径
#这里输入的是deb源码包解压后的文件夹，输出的是sbom
def Scan(scan_path,output_file,sbomType):
    #project_name= remove_file_extension(scan_path)
    project_name = scan_path
    #键是变量${xx},值是解析出来的具体数字
    dict_variable={}
    accPathSum=[]

    variableList=[]
    matrix=np.zeros((1024,1024))
    #生成syft普通json
    command_syft = f"{syft_path} scan  {scan_path} -o json"
    syft_output = subprocess.check_output(command_syft,shell=True)
    syft_json = json.loads(syft_output.decode())
    # tempath = scan_path+'-syft.json'
    # with open(tempath,"w") as f:
    #     f.write(syft_json)

    artifacts = syft_json['artifacts']
    for artifact in artifacts:
        foundBy = artifact['foundBy']
        #获取workdir
        workdir=''
        locations = artifact['locations']
        accPathList = []
        for location in locations:
            accessPath=location['accessPath']
            base_path = accessPath.rsplit('/',1)[0]+'/'
            workdir= scan_path+base_path
            accPathList.append(accessPath)
        accPathSum.append(accPathList)
        name = artifact['name']
        version = artifact['version']

        if foundBy=='java-pom-cataloger':
            metadata = artifact['metadata']
            groupId = ''
            pomProperties = metadata['pomProperties']
            if pomProperties:
                groupId = pomProperties['groupId']
                if groupId.startswith('$'):
                    value_name = AnalysisVariabele(workdir, groupId)
                    result = value_name.decode('utf-8').replace('b', '')
                    if result:
                        groupId = result
                        pomProperties['groupId'] = result
                        metadata['pomProperties']= pomProperties
                        artifact['metadata'] = metadata


            if name.startswith('$'):
                variableList.append(name)
                value_name = AnalysisVariabele(workdir, name)
                result = value_name.decode('utf-8').replace('b', '')
                artifact['name'] = result.replace("'", '')
                print(artifact['name'])
                dict_variable[name] = result
                for index_list, value_variableList in enumerate(variableList):
                    if value_variableList == name:
                        for index_path, path_list in enumerate(accPathSum):
                            if path_list == accPathList:
                                matrix[index_list, index_path] = 1
            if version.startswith('$'):
                variableList.append(version)
                value_version = AnalysisVariabele(workdir, version)
                result = value_version.decode('utf-8').replace('b', '')
                artifact['version'] = result.replace("'", '')
                print(artifact['version'])
                dict_variable[version] = result
                for index_variable, value_variable in enumerate(variableList):
                    if value_variable == version:
                        for index_path, path_acc in enumerate(accPathSum):
                            if path_acc == accPathList:
                                matrix[index_variable, index_path] = 1
            if  artifact['name'] == "":
                artifact['purl']= f'pkg:maven/unkonwn/unkonwn@unkonwn'
            if groupId and artifact['name']:
                artifact_name = artifact['name']
                artifact_version = artifact['version']
                artifact['purl'] = f'pkg:maven/{groupId}/{artifact_name}@{artifact_version}'
        try:
            metadataType = artifact['metadataType']
            if metadataType == 'java-archive':
                if artifact['name'] == "":
                    artifact['purl'] = f'pkg:maven/unkonwn/unkonwn@unkonwn'
        except KeyError:
            print("键不存在")
    #syft_json['artifacts'] = artifact
    tempath = scan_path + '-syft.json'
    with open(tempath, "w") as f:
        json_string =json.dumps(syft_json,indent=4, separators=(',', ': '))
        f.write(json_string)
    #处理外部依赖
    ExterDependencies = findExterDependency(scan_path)
    if sbomType=='spdx':
        convertSpdx(syft_json,project_name,output_file,ExterDependencies)
    if sbomType == 'cyclonedx':
        convertCyclonedx(syft_json, project_name, output_file, ExterDependencies)
    #生成cyclonedx的json
    # command_sbom = f"{syft_path} scan  {scan_path} -o cyclonedx-json"
    # cyclonedx_output = subprocess.check_output(command_sbom, shell=True)
    # cyclonedx_json= json.loads(cyclonedx_output.decode())
    # sbom_cyclonedx_json=cyclonedx_json
    # print(sbom_cyclonedx_json)
    # # 创建输出文件
    # open(output_file,"w").close()
    # #写入json文件
    # with open(output_file,"w") as file:
    #     json.dump(sbom_cyclonedx_json,file)
#sbomType = 'spdx'
# scan_path = '/home/jiliqiang/SCA_Evalutation/efda/java/maven/interpolated-variables'
# output_file='/home/jiliqiang/SCA_Evalutation/efda/java/maven/sbom_spdx/interpolated-variables.spdx.json'
#scan_path = '/home/jiliqiang/Deb/src/androguard'
#output_file='/home/jiliqiang/Deb/src/spdx_sbom/androguard.spdx.json'
#Scan(scan_path,output_file,sbomType)
# findExterDependency(scan_path)
import zipfile
import tarfile
import os
from spdx.Utils.extract import detect_file_type, get_all_supported_compressors, decompress,remove_file_extension
def countZip(directory):
    # 获取目录中所有文件列表
    files = os.listdir(directory)
    # 筛选出后缀为zip的文件
    deb_files = [f for f in files if f.endswith('.zip')]
    deb_file_path=[]

    # 使用dpkg -I输出包的详细信息
    for deb_file in deb_files:
        deb_file_path.append(os.path.join(directory, deb_file))

    return deb_file_path,deb_files

def remove_file_extension(file_name):
    base = os.path.basename(file_name)
    file_name_without_extension = os.path.splitext(base)[0]
    return file_name_without_extension

def extract_archive(archive_path,deb_file,extract_dir):
    # 创建目标文件夹
    #os.makedirs(extract_dir, exist_ok=True)
    # 获取解压后文件夹中的当前路径
    current_dir = remove_file_extension(deb_file)
    # extracted_folder_path = os.path.join(extract_dir, current_dir)
    extracted_folder_path = extract_dir
    decompress(archive_path,extracted_folder_path)
    extracted_folder_path = os.path.join(extract_dir, current_dir)
    # # 检测文件类型并解压
    # if zipfile.is_zipfile(archive_path):
    #     with zipfile.ZipFile(archive_path, 'r') as zip_ref:
    #         zip_ref.extractall(extract_dir)
    #         # 获取解压后文件夹中的当前路径
    #         current_dir = remove_file_extension(deb_file)
    #         extracted_folder_path = os.path.join(extract_dir,current_dir)
    #
    # elif tarfile.is_tarfile(archive_path):
    #     with tarfile.open(archive_path, 'r') as tar_ref:
    #         tar_ref.extractall(extract_dir)
    #         # 获取解压后文件夹中的当前路径
    #         current_dir = remove_file_extension(deb_file)
    #         extracted_folder_path = os.path.join(extract_dir,current_dir)
    # else:
    #     return "Unsupported archive format"

    return extracted_folder_path


# # 使用示例
# directory = '/home/jiliqiang/Rpm_Deb/Deb'
# countPath ,deb_files= countZip(directory)
# extract_dir = "/home/jiliqiang/Rpm_Deb/Deb/Deb_exact"
# for archive_path,deb_file in zip(countPath,deb_files):
#     result = extract_archive(archive_path, deb_file)
#     print("解压后的路径：", result)
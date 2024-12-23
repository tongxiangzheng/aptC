import magic
import packaging.version
#检测压缩包格式
def detect_file_type(filename):
    """
    检测文件的类型

    Args:
        filename: 文件名

    Returns:
        文件类型
    """

    m = magic.Magic(mime=True)
    return m.from_file(filename)

#查看支持的所有压缩格式


def get_all_supported_compressors():
    """
    获取所有支持的压缩格式

    Returns:
        所有支持的压缩格式列表
    """

    compressors = []

    for entry_point in packaging.iter_entry_points('packaging.compressors'):
        compressors.append(entry_point.name)

    return compressors

import os
import zipfile
import rarfile
import tarfile
import gzip
import bz2
# import xz
import winrar
#以上代码可以解压缩以下格式的压缩文件:
#
#.zip
#.rar
#.tar
#.gz
#.bz2
#.xz
def remove_file_extension(file_name):
    base = os.path.basename(file_name)
    file_name_without_extension = os.path.splitext(base)[0]
    return file_name_without_extension
def decompress(source_file, target_dir):
    """
    解压缩文件

    Args:
        source_file: 源压缩文件路径
        target_dir: 目标文件夹路径
    """

    # 检查目标文件夹是否存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 获取源文件名称
    filename = os.path.basename(source_file)

    # 判断压缩格式
    if zipfile.is_zipfile(source_file):
        with zipfile.ZipFile(source_file, "r") as z:
            z.extractall(target_dir)
    elif rarfile.is_rarfile(source_file):
        with rarfile.RarFile(source_file, "r") as r:
            r.extractall(target_dir)
    elif tarfile.is_tarfile(source_file):
        with tarfile.open(source_file, "r") as t:
            t.extractall(target_dir)
    elif filename.endswith('.gz'):
        with gzip.open(source_file, "rb") as g:
            with open(os.path.join(target_dir, filename), "wb") as f:
                f.write(g.read())
    elif bz2.is_bz2(source_file):
        with bz2.BZ2File(source_file, "rb") as b:
            with open(os.path.join(target_dir, filename), "wb") as f:
                f.write(b.read())
    # elif xz.is_xz(source_file):
    #     with xz.open(source_file, "rb") as x:
    #         with open(os.path.join(target_dir, filename), "wb") as f:
    #             f.write(x.read())
    else:
        return "Unsupported archive format"
    # with winrar.RARFile(source_file) as rar:
    #     z.extractall(target_dir)



# 使用示例
# source_file = "/path/to/source.zip"
# target_dir = "/path/to/target"
#
# decompress(source_file, target_dir)


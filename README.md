# aptC

## 如何在docker内进行测试：
### 构建docker:
```
docker run --name aptc -v <项目位置>:/code -it ubuntu:latest /bin/bash
```
进入docker后，在docker内执行:
```
/usr/bin/apt update
/usr/bin/apt -y install python3 python3-pip python3-loguru python3-pycurl python3-certifi python3-wget python3-lz4 python3-magic python3-packaging python3-rarfile python3-numpy python3-requests
pip3 install spdx-tools
pip3 install cyclonedx-bom
pip3 install cyclonedx-python-lib
pip3 install winrar

cd /code
make install

```
### 运行docker:
```
docker start aptc
docker exec -it aptc /bin/bash
```
### 在docker内测试：
apt install xxx，此时会执行检查

### 取消安装:
```
cd /code
chmod +x uninstall.sh
./uninstall.sh
```
## 如何打包

### 命令行方式
```
sudo apt install -y dh-make
```
文件夹改名为aptc-1.0

在文件夹内,若对代码进行修改：
```
dh_make --createorig -i -y
```

```
dpkg-buildpackage -us -uc
```
### docker方式
若对代码进行修改
```
dh_make --native -i -y
```

```
docker build --output=<二进制文件保存目录> .
docker build -t build_aptc .
docker run -v <生成deb文件保存目录>:/mnt/res build_aptc --rm
```

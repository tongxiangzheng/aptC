# aptC

## 如何在docker内进行测试：
### 构建docker:
```
docker run --name aptc -v <项目位置>:/code -it ubuntu:latest /bin/bash
```
进入docker后，在docker内执行:
```
/usr/bin/apt update
/usr/bin/apt -y install python3 python3-pip python3-loguru python3-pycurl python3-certifi python3-wget python3-lz4
echo "alias apt='aptc'" >> /etc/bash.bashrc
echo "alias apt-get='apt-getc'" >> /etc/bash.bashrc
cd /code
chmod +x install.sh
./install.sh
```
### 运行docker:
```
docker start aptc
docker exec -it aptc /bin/bash
```
### 在docker内测试：
apt install xxx，此时会执行检查

### 取消安装(test):
cd /code
chmod +x uninstall.sh
./uninstall.sh

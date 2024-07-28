if [ ! -d "/usr/share/aptC" ]; then
	mkdir /usr/share/aptC
fi
if [ ! -d "/usr/share/aptC/spdx" ]; then
	mkdir /usr/share/aptC/spdx
fi
for file in bin/*; do
    if [ -f $file ]; then
		chmod +x $file
		cp $file /usr/bin/
	fi
done

for file in src/*; do
    if [ -f $file ]; then
		cp $file /usr/share/aptC
	fi
done
for file in src/spdx/*; do
    if [ -f $file ]; then
		cp $file /usr/share/aptC/spdx
	fi
done
#/usr/bin/apt -y install python3 python3-pip python3-loguru python3-pycurl python3-certifi python3-wget python3-lz4
#echo "alias apt='aptc'" > /etc/profile.d/aptc-hook.sh
#echo "alias apt='aptc'" >> /etc/bash.bashrc
#echo "alias apt-get='apt-getc'" >> /etc/bash.bashrc
alias apt='aptc'



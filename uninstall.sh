rm /usr/bin/aptc
rm /usr/bin/apt-getc
rm -r /usr/share/aptC
sed -i "/alias apt='aptc'/d" /etc/bash.bashrc
sed -i "/alias apt-get='apt-getc'/d" /etc/bash.bashrc
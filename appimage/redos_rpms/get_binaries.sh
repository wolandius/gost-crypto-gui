#!/bin/bash
rm -rf ./etc
rm -rf ./lib64
rm -rf ./sbin
rm -rf ./usr
rm -rf ./var

if [ ! -f "/usr/bin/dnf" ];
then
    yumdownloader opensc python3-chardet usermode xdg-utils realmd procps-ng wget polkit gtk3 glibc python3;
else
    dnf download opensc qt5 python3-qt5 python3;
fi

rm -rf ./*.i686.rpm
for f in ./*.rpm; do
  rpm2cpio "$f" | cpio -idmv
done
rm -rf ./usr/share/doc
rm -rf ./usr/share/licenses
rm -rf ./usr/share/locale
rm -rf ./usr/share/man
rm -rf *.rpm


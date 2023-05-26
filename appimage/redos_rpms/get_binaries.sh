#!/bin/bash
rm -rf ./etc
rm -rf ./lib64
rm -rf ./sbin
rm -rf ./usr
rm -rf ./var

if [ ! -f "/usr/bin/dnf" ];
then
    yumdownloader opensc qt5 python3-qt5 python3 qt-settings qt5-qdbusviewer qt5-qt3d qt5-qtbase qt5-qtbase-common qt5-qtbase-gui qt5-qtbase-mysql qt5-qtbase-postgresql qt5-qtconnectivityqt5-qtdeclarativeqt5-qtdoc qt5-qtgraphicaleffects qt5-qtimageformatsqt5-qtlocation qt5-qtmultimedia qt5-qtquickcontrols qt5-qtquickcontrols2 qt5-qtscript qt5-qtsensors qt5-qtserialport qt5-qtsvg qt5-qttools qt5-qttools-common qt5-qtwayland qt5-qtwebchannel qt5-qtwebkit qt5-qtwebsockets qt5-qtx11extras qt5-qtxmlpatterns pcre2-utf16 python3-pyqt5-sip assimp irrXML libaesgm libmng libpq minizip poly2tri python3-sip;
else
    dnf download opensc qt5 python3-qt5 python3 qt-settings qt5-qdbusviewer qt5-qt3d qt5-qtbase qt5-qtbase-common qt5-qtbase-gui qt5-qtbase-mysql qt5-qtbase-postgresql qt5-qtconnectivityqt5-qtdeclarativeqt5-qtdoc qt5-qtgraphicaleffects qt5-qtimageformatsqt5-qtlocation qt5-qtmultimedia qt5-qtquickcontrols qt5-qtquickcontrols2 qt5-qtscript qt5-qtsensors qt5-qtserialport qt5-qtsvg qt5-qttools qt5-qttools-common qt5-qtwayland qt5-qtwebchannel qt5-qtwebkit qt5-qtwebsockets qt5-qtx11extras qt5-qtxmlpatterns pcre2-utf16 python3-pyqt5-sip assimp irrXML libaesgm libmng libpq minizip poly2tri python3-sip;
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




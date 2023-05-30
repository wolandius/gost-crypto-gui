#!/bin/bash
if [ ! -f "./appimagetool" ]; then
    wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage -O ./appimagetool
fi
VERSION=$2
rm -rf ./gost-crypto-gui-ro$1*.AppImage
#rm -rf ./AppDir
mkdir -p ./AppDir
cd ..
python3 ./setup.py install --root=./appimage/AppDir --prefix=usr
cd appimage

cp AppRun ./AppDir/
if [ $1 = "72" ]; then
    sed -i 's|python3.8|python3.6|g' ./AppDir/AppRun
fi

cp ../data/gost-crypto-gui.desktop ./AppDir/
cp ../pics/128x128/gost-crypto-gui.png ./AppDir/
pushd ./redos_rpms
bash ./get_binaries.sh
cp -r ./usr ../AppDir/
cp -r ./etc ../AppDir/
popd
pushd ./AppDir/usr/lib64/qt5/plugins
ln -sf platforms/ ../../../bin/platforms
popd
rm -rf ./AppDir/usr/share/caja-python/
chmod +x ./AppDir/gost-crypto-gui.desktop
chmod +x ./AppDir/AppRun
chmod +x ./appimagetool
ARCH=x86-64 ./appimagetool ./AppDir
chmod +x ./gost-crypto-gui-x86_64.AppImage
mv gost-crypto-gui-x86_64.AppImage gost-crypto-gui-$VERSION-ro$1-x86_64.AppImage
./gost-crypto-gui-$VERSION-ro$1-x86_64.AppImage
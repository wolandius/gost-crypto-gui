#!/bin/bash
#rm -f gostcryptogui/*.pyc

mkdir -p ~/rpmbuild/SPECS ~/rpmbuild/SOURCES ./gostcryptogui-$1

rsync -ah --progress src ./gostcryptogui-$1
rsync -ah --progress file-manager ./gostcryptogui-$1
rsync -ah --progress data ./gostcryptogui-$1
rsync -ah --progress pics ./gostcryptogui-$1
rsync -ah --progress setup.py ./gostcryptogui-$1
rsync -ah --progress LICENSE ./gostcryptogui-$1
rsync -ah --progress README.md ./gostcryptogui-$1
rsync -ah --progress Changelog ./gostcryptogui-$1

tar -cvzf ./gostcryptogui-$1.tar.gz ./gostcryptogui-$1
rsync -ah --progress ./gostcryptogui-$1.tar.gz ~/rpmbuild/SOURCES/

rm -rf ~/rpmbuild/SPECS/gostcryptogui.spec

cp gostcryptogui.spec ~/rpmbuild/SPECS/
rpmbuild -ba ~/rpmbuild/SPECS/gostcryptogui.spec

rm -rf gostcryptogui-$1.tar.gz gostcryptogui-$1

cp ~/rpmbuild/RPMS/noarch/gostcryptogui-$1-1.el7.*.noarch.rpm ~/git_projects/gost-crypto-gui/
cp ~/rpmbuild/SRPMS/gostcryptogui-$1-1.el7.*.src.rpm ~/git_projects/gost-crypto-gui/
cp ~/rpmbuild/RPMS/noarch/gostcryptogui-caja-$1-1.el7.*.noarch.rpm ~/git_projects/gost-crypto-gui/

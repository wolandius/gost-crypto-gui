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

#cp spec\ for\ 7.2/gostcryptogui.spec ~/rpmbuild/SPECS/
#rpmbuild -ba ~/rpmbuild/SPECS/gostcryptogui.spec

#rsync -ah --progress ~/rpmbuild/RPMS/noarch/gostcryptogui-$1-1.el7.2.noarch.rpm ~/git_projects/gost-crypto-gui/gostcryptogui-$1-1.el7.2.noarch.rpm
#rsync -ah --progress ~/rpmbuild/SRPMS/gostcryptogui-$1-1.el7.2.src.rpm ~/git_projects/gost-crypto-gui/gostcryptogui-$1-1.el7.2.src.rpm

cp spec\ for\ 7.3/gostcryptogui.spec ~/rpmbuild/SPECS/
rpmbuild -ba ~/rpmbuild/SPECS/gostcryptogui.spec

rm -rf gostcryptogui-$1.tar.gz gostcryptogui-$1

rsync -ah --progress ~/rpmbuild/RPMS/noarch/gostcryptogui-$1-1.el7.3.noarch.rpm ~/git_projects/gost-crypto-gui/gostcryptogui-$1-1.el7.3.noarch.rpm
rsync -ah --progress ~/rpmbuild/SRPMS/gostcryptogui-$1-1.el7.3.src.rpm ~/git_projects/gost-crypto-gui/gostcryptogui-$1-1.el7.3.src.rpm
rsync -ah --progress ~/rpmbuild/RPMS/noarch/gostcryptogui-caja-$1-1.el7.3.noarch.rpm ~/git_projects/gost-crypto-gui/gostcryptogui-caja-$1-1.el7.3.noarch.rpm

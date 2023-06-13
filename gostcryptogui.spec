#
# spec file for package gostcryptogui
#

Name:		gostcryptogui
Version:	2.0.2
%if 0%{?redos_version} < 0730
Release:        1%{dist}.2
%else
Release:        1%{dist}.3
%endif

Summary:	A PyQt GUI for performing cryptographic operations over files using GOST algorithms
Summary(ru):    Графический интерфейс PyQt для выполнения криптографических операций над файлами с использованием алгоритмов ГОСТ

License:	MIT
Group:		System Environment/Base
Url:		https://github.com/wolandius/gost-crypto-gui

Source0:	%{name}-%{version}.tar.gz

BuildArch:	noarch
Buildrequires:  python3
Buildrequires:  python3-devel
Buildrequires:  python3-setuptools
Buildrequires:  redhat-lsb-core


Requires:	qt5
Requires:	python3-qt5
Requires:	xdg-utils


%description
A PyQt5 GUI for performing cryptographic operations over files using GOST algorithms

%description -l ru
Графический интерфейс PyQt5 для выполнения криптографических операций над файлами с использованием алгоритмов ГОСТ.

%if 0%{?redos_version} >= 0730
%package caja
Summary:        Caja plugins for gost-crypto-gui
Summary(ru):    Расширение файлового менеджера caja для gost-crypto-gui
BuildArch:      noarch
Requires:       %{name}
Obsoletes:      caja-gostcryptogui

%description caja
Caja plugins for gost-crypto-gui

%description caja -l ru
Расширение файлового менеджера caja для gost-crypto-gui
%endif

%prep
%setup -q
rm -rf %{name}.egg-info

%build
%if 0%{?redos_version} >= 0730
WITH_CAJA=yes python3 setup.py build
%else
python3 setup.py build
%endif

%install

%if 0%{?redos_version} >= 0730
WITH_CAJA=yes python3 setup.py install --single-version-externally-managed --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
%else
python3 setup.py install --single-version-externally-managed --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
%endif

%post
xdg-mime install %{_datadir}/mime/applications/x-extension-enc.xml
xdg-mime install %{_datadir}/mime/applications/x-extension-sig.xml
xdg-mime install %{_datadir}/mime/applications/x-extension-sgn.xml
xdg-desktop-menu install --mode system %{_datadir}/applications/gost-crypto-gui.desktop
xdg-icon-resource install --context mimetypes --mode system --size 256 %{_datadir}/gostcryptogui/encrypted.png application-x-extension-enc
xdg-icon-resource install --context mimetypes --mode system --size 256 %{_datadir}/gostcryptogui/signed.png application-x-extension-sig
xdg-icon-resource install --size 48 --context emblems %{_datadir}/gostcryptogui/emblem-nochain.png
xdg-icon-resource install --size 48 --context emblems %{_datadir}/gostcryptogui/emblem-unverified.png
xdg-icon-resource install --size 48 --context emblems %{_datadir}/gostcryptogui/emblem-verified.png
xdg-icon-resource forceupdate

%posttrans
VERSION=%{version}
for f in /usr/lib/python3*/site-packages/gostcryptogui*egg*;
do
  if [ -d "$f" ] && [ "$f" != "/usr/lib/python3"*"/site-packages/gostcryptogui-$VERSION"* ]; then
    rm -rf $f ;
  fi;
done

%files -f INSTALLED_FILES
%license LICENSE
%doc README.md Changelog
%exclude  /usr/lib/python3*/site-packages/gostcryptogui/*/*.pyc
%exclude %{_datadir}/caja-python/extensions/gost-crypto-gui-*.py*

%if 0%{?redos_version} >= 0730
%files caja
%{_datadir}/caja-python/extensions/gost-crypto-gui-*.py
%endif

%changelog
* Tue Jun 13 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:2.0.2-1
- changed logic in setup.py for use env variable WITH_CAJA

* Wed Jun 07 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:2.0.1-1
- improve sys.argv logic for compatibility with libreoffice extension
- added buildrequire for successful build in mock environment

* Fri May 26 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:2.0-1
- added appimage support for redos72 and redos73
- added translation files for app
- port gostcryptogui-caja to python3 only for redos73
- upd setup.py, to build caja extensions only for redos >= 7.3

* Tue Apr 25 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:1.4-1
- added new MultiOutputDialog

* Tue Apr 18 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:1.3-1
- replace regex with dictionary funcs in get_store_certs
- fix all funcs in gui.py for work with multiple files

* Wed Apr 12 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:1.2-1
- improved certs parse logic for cryptopro4 cert

* Fri Apr 07 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0:1.1-1
- improved certs parse logic
- fixed popen multithread error if one of chain certs not installed
- added backport to goslinux and redos72

* Thu Mar 23 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 1.0.1-1
- create config if not exist on startup of application

* Thu Mar 23 2023 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 1.0-1
- changed project structure to use setup.py on build
- fix in detached sign verify
- upd years in license files

* Wed Sep 28 2022 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0.9-1
- added encrypt/decrypt to/from p7e/p7m files
- rebased src to use archive as SOURCE0

* Wed Mar 23 2022 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0.8-1
- added missing require python3-qt5
- fix in save report button

* Thu Mar 10 2022 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0.7-1
- changed logic for filenames from libreoffice plugin

* Fri Mar 04 2022 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0.6-1
- port from qt4 to qt5 and python3

* Wed Mar 02 2022 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0.5-1
- added compatibility for new versions of cryptopro 4 and 5
- removed patches, because they are already applied in code

* Mon Oct 25 2021 Vladlen Murylyov <vladlen.murylyov@red-soft.ru> - 0.4-5
- added aarch64 compitibility

* Wed Feb 10 2021 Ilya Vasiltsov <ilya.vasiltsov@red-soft.ru> - 0.4-4
- Patch: dettach sign using -delsign argument

* Wed Dec 16 2020 Ilya Vasiltsov <ilya.vasiltsov@red-soft.ru> - 0.4-3
- Updated to 0.4

* Tue Jul 30 2019 Alexey Rodionov <alexey.rodionov@red-soft.ru> - 0.3-7
- apply commit 0fb6d5b53d4ac46263121b3780018365317c6a04 from git

* Tue Mar 26 2019 Alexey Rodionov <alexey.rodionov@red-soft.ru> - 0.3-6
- apply commit b1b527ecada4acf116e9c19409f339f593a2d1e2 from git

* Mon Apr 02 2018 Alexey Rodionov <alexey.rodionov@red-soft.ru> - 0.3-5
- apply commit 4b7a47a22e9d2059d36b3a9905b7c8240732104b from git

* Mon Mar 12 2018 Alexey Rodionov <alexey.rodionov@red-soft.ru> - 0.3-4
- apply commit d1348e5822a8973900d67fee07973bd1eb6b478f from git

* Fri Feb 16 2018 Alexey Rodionov <alexey.rodionov@red-soft.ru> - 0.3-3
- apply commit df0f050cf8b42ad3c72f2f147db15f243a03cc98 from git

* Thu Feb 15 2018 Alexey Rodionov <alexey.rodionov@red-soft.ru> - 0.3-2
- apply commit f5db7f3f348fb90a52c22ae8413f6c6f4bc296b1 from git

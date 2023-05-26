#!/bin/bash
rm -rf ./GostCryptoGui-en_US.ts
pylupdate5 ../mainwindow.ui \
           ../selectcert.ui \
           ../viewcert.ui \
           ../viewmultiresults.ui \
           ../../src/gostcryptogui/GostCryptoGui.py \
           ../../src/gostcryptogui/cprocsp.py \
           ../../src/gostcryptogui/gui.py \
-ts ./GostCryptoGui-en_US.ts -verbose

#for file manager we need gettext locales, not qt locales

xgettext --language=Python --keyword=_ --keyword=N_ --output=gostcryptogui_caja.pot \
  ~/git_projects/gost-crypto-gui/file-manager/caja/gost-crypto-gui-menu.py


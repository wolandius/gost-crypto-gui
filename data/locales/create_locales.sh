#!/bin/bash
pylupdate5 ../mainwindow.ui \
           ../selectcert.ui \
           ../viewcert.ui \
           ../viewmultiresults.ui \
           ../../src/gostcryptogui/GostCryptoGui.py \
           ../../src/gostcryptogui/cprocsp.py \
           ../../src/gostcryptogui/gui.py \
-ts ./GostCryptoGui-en_US.ts -verbose

#for file manager we need gettext locales, not qt locales
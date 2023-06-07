#!/usr/bin/python3

import sys
import os.path

from gostcryptogui import gui
# import gui
import PyQt5
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QTranslator
import urllib.parse

appdir = os.popen("echo $APPDIR").readline().strip()

def main():
    print(sys.argv)
    global appdir
    app = QtWidgets.QApplication(sys.argv)
    if "ru_RU" in PyQt5.QtCore.QLocale().system().name():
        pass
    elif "en_US" in PyQt5.QtCore.QLocale().system().name():
        translator = QTranslator(app)
        translator.load("GostCryptoGui-en_US.qm",
                        f"{appdir}/usr/share/gostcryptogui") if appdir else \
            translator.load("GostCryptoGui-en_US.qm", "/usr/share/gostcryptogui")
        app.installTranslator(translator)
    else:
        translator = QTranslator(app)
        translator.load("GostCryptoGui-en_US.qm",
                        f"{appdir}/usr/share/gostcryptogui") if appdir else \
            translator.load("GostCryptoGui-en_US.qm", "/usr/share/gostcryptogui")
        app.installTranslator(translator)

    ex = gui.Window()
    if not os.path.exists("~/.gost-crypto-gui/"):
        ex.setOptions()
    ex.readConfig()
    if len(sys.argv) == 1:
        ex.show()
        sys.exit(app.exec_())
    elif sys.argv[1] == '--help':
        print(PyQt5.QtCore.QCoreApplication.translate('', 'Использование: gost-crypto-gui [КЛЮЧ] [ФАЙЛ]'))
        print(PyQt5.QtCore.QCoreApplication.translate('', 'Выполняет криптографические операции над файлами при помощи алгоритмов ГОСТ\n'))
        print(PyQt5.QtCore.QCoreApplication.translate('', 'Ключи:\n'))
        print(PyQt5.QtCore.QCoreApplication.translate('', '-sign\t\tПодписать файл'))
        print(PyQt5.QtCore.QCoreApplication.translate('', '-encr\t\tЗашифровать файл'))
        print(PyQt5.QtCore.QCoreApplication.translate('', '-verify\t\tПроверить электронную подпись файла'))
        print(PyQt5.QtCore.QCoreApplication.translate('', '-decr\t\tРасшифровать файл'))
    else:
        filename = ""
        if " -sign " in sys.argv[1]:
            name = sys.argv[1].split(" -sign ")[1]
            sys.argv[1] = "-sign"
            sys.argv.append(name)
        print(sys.argv)
        for i in range(2, len(sys.argv)):
            tempfilename = urllib.parse.unquote(sys.argv[i])[7:] if "file:///" in sys.argv[i] else sys.argv[i]
            filename += f"{tempfilename} " if i < len(sys.argv)-1 else f"{tempfilename}"
        if os.path.exists(filename):
            if  '-sign' in sys.argv[1]:
                ex.sign(filename)
            elif sys.argv[1] == '-encr':
                ex.encrypt(filename)
            elif sys.argv[1] == '-verify':
                ex.verify(False, filename)
            elif sys.argv[1] == '-decr':
                ex.decrypt(filename)
            elif os.path.isfile(sys.argv[1]):
                if sys.argv[1][-4:] == '.enc':
                    ex.decrypt(sys.argv[1])
                elif sys.argv[1][-4:] == '.sig':
                    ex.verify(True, sys.argv[1])

if __name__ == '__main__':
    main()

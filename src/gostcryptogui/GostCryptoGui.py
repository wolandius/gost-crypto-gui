#!/usr/bin/python3

import sys
import os.path

from gostcryptogui import gui
# import gui

from PyQt5 import QtGui, QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = gui.Window()
    if not os.path.exists("~/.gost-crypto-gui/"):
        ex.setOptions()
    ex.readConfig()
    if len(sys.argv) == 1:
        ex.show()
        sys.exit(app.exec_())
    elif sys.argv[1] == '--help':
        print('Использование: gost-crypto-gui [КЛЮЧ] [ФАЙЛ]')
        print('Выполняет криптографические операции над файлами при помощи алгоритмов ГОСТ\n')
        print('Ключи:\n')
        print('-sign\t\tПодписать файл')
        print('-encr\t\tЗашифровать файл')
        print('-verify\t\tПроверить электронную подпись файла')
        print('-dettach\tОтсоединить электронную подпись от файла')
        print('-decr\t\tРасшифровать файл')
    else:
        filename = ""
        for i in range(2, len(sys.argv)):
            if i < len(sys.argv)-1:
                filename += f"{sys.argv[i]} "
            else:
                filename += f"{sys.argv[i]}"
        if os.path.exists(filename):
            if sys.argv[1] == '-sign':
                ex.sign(filename)
            elif sys.argv[1] == '-encr':
                ex.encrypt(filename)
            elif sys.argv[1] == '-verify':
                ex.verify(False, filename)
            elif sys.argv[1] == '-dettach':
                ex.verify(True, filename)
            elif sys.argv[1] == '-decr':
                ex.decrypt(filename)
            elif os.path.isfile(sys.argv[1]):
                if sys.argv[1][-4:] == '.enc':
                    ex.decrypt(sys.argv[1])
                elif sys.argv[1][-4:] == '.sig':
                    ex.verify(True, sys.argv[1])


if __name__ == '__main__':
    main()

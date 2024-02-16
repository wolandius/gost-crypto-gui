#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Борис Макаренко

Данная лицензия разрешает лицам, получившим копию данного программного
обеспечения и сопутствующей документации (в дальнейшем именуемыми «Программное
Обеспечение»), безвозмездно использовать Программное Обеспечение без
ограничений, включая неограниченное право на использование, копирование,
изменение, добавление, публикацию, распространение, сублицензирование и/или
продажу копий Программного Обеспечения, а также лицам, которым предоставляется
данное Программное Обеспечение, при соблюдении следующих условий:

Указанное выше уведомление об авторском праве и данные условия должны быть
включены во все копии или значимые части данного Программного Обеспечения.

ДАННОЕ ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО
ГАРАНТИЙ, ЯВНО ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ ГАРАНТИИ ТОВАРНОЙ
ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ НАРУШЕНИЙ,
НО НЕ ОГРАНИЧИВАЯСЬ ИМИ. НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ
ОТВЕТСТВЕННОСТИ ПО КАКИМ-ЛИБО ИСКАМ, ЗА УЩЕРБ ИЛИ ПО ИНЫМ ТРЕБОВАНИЯМ, В ТОМ
ЧИСЛЕ, ПРИ ДЕЙСТВИИ КОНТРАКТА, ДЕЛИКТЕ ИЛИ ИНОЙ СИТУАЦИИ, ВОЗНИКШИМ ИЗ-ЗА
ИСПОЛЬЗОВАНИЯ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫХ ДЕЙСТВИЙ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ..

Copyright (c) 2019 Boris Makarenko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from gi.repository import Caja, GObject
import gettext
import subprocess
import os
import urllib.parse
t = gettext.translation('gostcryptogui_caja', "/usr/share/locale/")
t.install()
_ = t.gettext

class GostCryptoGuiMenuProvider(GObject.GObject, Caja.MenuProvider):
    def __init__(self):
        GObject.Object.__init__(self)

    def get_file_items(self, window, files):
        '''Returns the menu items to display when one or more files/folders are
        selected.'''

        global filelist
        global pwd

        pwd = None
        filelist = []
        for file in files:
            if pwd == None:
                pwd = file.get_parent_location().get_path()
            name = file.get_name()
            filelist += [name]


        if pwd == None or len(filelist) == 0:
            return

        elif not os.access(pwd, os.W_OK):
            return

        text = "GostCrypto"
        top_menuitem = Caja.MenuItem(name=f'GostCryptoGuiMenuProvider::Main',
                                     label=text,
                                     tip=text,
                                     icon='')
        extra_actions = Caja.Menu()
        top_menuitem.set_submenu(extra_actions)

        if file.is_directory():
            return
        filename = urllib.parse.unquote(file.get_uri())[7:]
        # if os.path.isfile(filename[:-4]):
        #     return

        if filename[-3:] == 'sig':
            text = _("Проверить ЭЦП")
            item = Caja.MenuItem(name=f'GostCryptoGuiMenuProvider::Verify',
                                 label=text,
                                 tip=f"{text} {filename}",
                                 icon='')
            extra_actions.append_item(item)
            item.connect("activate", self.menu_activate_cb, str(filename), "Verify")

        if filename[-3:] == 'enc':
            text = _("Расшифровать файл")
            item = Caja.MenuItem(name=f'GostCryptoGuiMenuProvider::Decrypt',
                                 label=text,
                                 tip=f"{text} {filename}",
                                 icon='')
            extra_actions.append_item(item)
            item.connect("activate", self.menu_activate_cb, str(filename), "Decrypt")
        ######

        text = _("Подписать файл")
        item = Caja.MenuItem(name='SignMenuProvider::Sign',
                                 label=text,
                                 tip=f"{text} {filename}",
                                 icon='')
        extra_actions.append_item(item)
        item.connect("activate", self.menu_activate_cb, str(filename), "Sign")

        text = _('Зашифровать файл')
        item = Caja.MenuItem(name='EncryptMenuProvider::Encrypt',
                                    label=text,
                                    tip=f"{text} {filename}",
                                    icon='')
        extra_actions.append_item(item)
        item.connect("activate", self.menu_activate_cb, str(filename), "Encrypt")

        return [top_menuitem]

    def menu_activate_cb(self, menu, fileObj, action):
        filename = str(fileObj)
        #todo: works a bit strangly, need to be tested all IF

        print(filename)
        if action == "Verify":
            subprocess.Popen(['python3', '/usr/bin/gost-crypto-gui', '-verify', filename])
        elif action == "Dettach":
            subprocess.Popen(['python3', '/usr/bin/gost-crypto-gui', '-dettach', filename])
        elif action == "Sign":
            subprocess.Popen(['python3', '/usr/bin/gost-crypto-gui', '-sign', filename])
        elif action == "Decrypt":
            subprocess.Popen(['python3', '/usr/bin/gost-crypto-gui', '-decr', filename])
        elif action == "Encrypt":
            subprocess.Popen(['python3', '/usr/bin/gost-crypto-gui', '-encr', filename])
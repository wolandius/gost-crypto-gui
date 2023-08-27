#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (c) 2017 Борис Макаренко
Copyright (c) 2022-2023 Мурылев Владлен

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

Copyright (c) 2017 Boris Makarenko
Copyright (c) 2022-2023 Vladlen Murylev

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
import configparser
import os
import subprocess

from datetime import datetime
import PyQt5
from PyQt5 import QtWidgets, uic, QtCore, QtGui

from gostcryptogui.cprocsp import *
# from cprocsp import *

VERSION = "2.1"
appdir = os.popen("echo $APPDIR").readline().strip()

class ViewCert(QtWidgets.QDialog):
    report = str
    def __init__(self, parent=None):
        super().__init__(parent)
        global appdir
        # uic.loadUi('/home/wolandius/git_projects/gost-crypto-gui/data/viewcert.ui', self)
        uic.loadUi(f'{appdir}/usr/share/gostcryptogui/viewcert.ui', self) if appdir else \
            uic.loadUi('/usr/share/gostcryptogui/viewcert.ui', self)
        self.saveReport.clicked.connect(self.saveReportDialog)
        self.close_cert_view.clicked.connect(self.close)
        self.show()

    def saveReportDialog(self):
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, PyQt5.QtCore.QCoreApplication.translate('', 'Сохранить отчет'), '', '(*.txt)')
        if not fileName[0]:
            return
        fileReport = open(fileName[0], 'w')
        fileReport.write(self.report)
        fileReport.close()


class HTMLDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        model = index.model()
        record = model.stringList()[index.row()]
        doc = QtGui.QTextDocument(self)

        doc.setHtml(record)
        doc.setMetaInformation(QtGui.QTextDocument.DocumentUrl, f"file:///{appdir}/usr/share/") if appdir else \
        doc.setMetaInformation(QtGui.QTextDocument.DocumentUrl, "file:///usr/share/")

        doc.setTextWidth(option.rect.width())
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        painter.save()
        painter.translate(option.rect.topLeft())
        painter.setClipRect(option.rect.translated(-option.rect.topLeft()))
        dl = doc.documentLayout()
        dl.draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        model = index.model()
        record = model.stringList()[index.row()]
        doc = QtGui.QTextDocument(self)
        doc.setHtml(record)
        doc.setTextWidth(option.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())

# TODO Показывать алгоритмы подписи и открытого ключа
class ChooseCert(QtWidgets.QDialog):
    cert = str
    certs_hashes = dict

    def __init__(self, parent=None, withsecret=bool):
        super().__init__(parent)
        global appdir
        # uic.loadUi('/home/wolandius/git_projects/gost-crypto-gui/data/selectcert.ui', self)
        uic.loadUi(f'{appdir}/usr/share/gostcryptogui/selectcert.ui', self) if appdir else \
            uic.loadUi('/usr/share/gostcryptogui/selectcert.ui', self)

        self.certs_hashes = []

        cert_list = []
        # Получаем сертификаты из личного хранилища
        certs_data = CryptoPro().get_store_certs(store='uMy')
        if not withsecret:
            cert_list.append(PyQt5.QtCore.QCoreApplication.translate('', '<i>Из файла...</i>'))
        for line in certs_data:
            png_path = f"{appdir}/usr/share/gostcryptogui/emblem-verified.png" if appdir else "/usr/share/gostcryptogui/emblem-verified.png"
            cert_html = f'<img src="{png_path}" width=22 height=22><b>{line["subjectCN"]}</b> '\
                        f"{PyQt5.QtCore.QCoreApplication.translate('', '<br>Выдан:')}" \
                        f'{line["issuerCN"]} <br>' \
                        f"{PyQt5.QtCore.QCoreApplication.translate('', 'Серийный номер: ')}" \
                        f'{line["serial"]}' \
                        f"{PyQt5.QtCore.QCoreApplication.translate('', '<br>Хэш SHA1: ')}" \
                        f'{line["thumbprint"]}<br>'

            if datetime.strptime(line['notValidBefore'], '%d/%m/%Y  %H:%M:%S') > datetime.utcnow():
                cert_html += f"{PyQt5.QtCore.QCoreApplication.translate('', 'Не действителен до: ')}"\
                f'<font color=red><b>{line["notValidBefore"]}</b></font><br>'
                cert_html = cert_html.replace('emblem-verified.png', 'emblem-unverified.png')
            else:
                cert_html += PyQt5.QtCore.QCoreApplication.translate('', 'Не действителен до: %s<br>') % line['notValidBefore']
            if datetime.strptime(line['notValidAfter'], '%d/%m/%Y  %H:%M:%S') < datetime.utcnow():
                cert_html += PyQt5.QtCore.QCoreApplication.translate('', 'Не действителен после: <font color=red><b>%s</b></font>') % line['notValidAfter']
                cert_html = cert_html.replace('emblem-verified.png', 'emblem-unverified.png')
            else:
                cert_html += PyQt5.QtCore.QCoreApplication.translate('', 'Не действителен после: %s') % line['notValidAfter']
            if withsecret:
                    cert_list.append(cert_html)
                    self.certs_hashes.append(line)
            else:
                cert_list.append(cert_html)
                self.certs_hashes.append(line)

        model = QtCore.QStringListModel(cert_list)
        self.listView.setModel(model)
        self.listView.setItemDelegate(HTMLDelegate(self))
        self.cancelButton.clicked.connect(self.close)
        self.okButton.setEnabled(False)
        self.okButton.clicked.connect(self.accept)

        if withsecret:
            self.listView.clicked.connect(self.select_cert_w_secret)
        else:
            self.listView.clicked.connect(self.select_cert)
        self.show()

    def select_cert(self, index):
        if index.row() == 0:
            self.cert = 'file'
        else:
            self.cert = self.certs_hashes[index.row()-1]
        self.okButton.setEnabled(bool(self.cert))

    def select_cert_w_secret(self, index):
        self.cert = self.certs_hashes[index.row()]
        self.okButton.setEnabled(bool(self.cert))

    def getCertificate(self):
        return self.cert


class ResultDialog(QtWidgets.QDialog):

    filename = str
    result = str
    dettached = False

    def __init__(self, filename, result, message, parent=None, dettached=False):
        super(ResultDialog, self).__init__(parent)
        self.filename, self.result, self.dettached = filename, result, dettached
        msgBox = QtWidgets.QMessageBox()
        closeButton = QtWidgets.QPushButton(PyQt5.QtCore.QCoreApplication.translate('', 'Закрыть'))
        sendButton = QtWidgets.QPushButton(PyQt5.QtCore.QCoreApplication.translate('', 'Отправить по почте'))
        showButton = QtWidgets.QPushButton(PyQt5.QtCore.QCoreApplication.translate('', 'Показать в папке'))
        msgBox.setText(message)
        msgBox.addButton(closeButton, QtWidgets.QMessageBox.NoRole)
        msgBox.addButton(sendButton, QtWidgets.QMessageBox.NoRole)
        msgBox.addButton(showButton, QtWidgets.QMessageBox.NoRole)
        msgBox.setDefaultButton(closeButton)
        sendButton.clicked.connect(self.send)
        showButton.clicked.connect(self.showFile)
        ret = msgBox.exec_()

    # Если создавалась отсоединенная подпись, отправить и оригинал
    def send(self):
        prog_path = f"{appdir}/usr/bin/xdg-email" if appdir else "/usr/bin/xdg-email"
        if self.dettached:

            subprocess.Popen([prog_path, '--attach', self.result, '--attach', self.filename])
        else:
            subprocess.Popen([prog_path, '--attach', self.result])

    def showFile(self):
        prog_path = f"{appdir}/usr/bin/xdg-open" if appdir else "/usr/bin/xdg-open"
        subprocess.Popen(['xdg-open', '/'.join(self.result.split('/')[:-1])])

class MultiResultDialog(QtWidgets.QDialog):
    output = list

    def __init__(self, parent=None, output=None):
        super().__init__(parent)
        global appdir
        # uic.loadUi('/home/wolandius/git_projects/gost-crypto-gui/data/viewmultiresults.ui', self)
        uic.loadUi(f'{appdir}/usr/share/gostcryptogui/viewmultiresults.ui', self) if appdir else \
            uic.loadUi('/usr/share/gostcryptogui/viewmultiresults.ui', self)

        cert_list = []
        for line in output:
            cert_html = f'{line[0]}:<br>' \
                        f'<b>{line[1]}</b><br>' \
                        f"{PyQt5.QtCore.QCoreApplication.translate('', 'Информация о сертификате:<br>')}" \
                        f'<b>{line[2]["subjectCN"]}</b><br>' \
                        f"{PyQt5.QtCore.QCoreApplication.translate('', 'Серийный номер:')}"\
                        f'{line[2]["serial"]}'\
                        f"{PyQt5.QtCore.QCoreApplication.translate('', '<br>Хэш SHA1:')}"\
                        f' {line[2]["thumbprint"]}<br>' \
                        f'{line[3]}'
            cert_list.append(cert_html)
        model = QtCore.QStringListModel(cert_list)
        self.listView.setModel(model)
        self.listView.setItemDelegate(HTMLDelegate(self))
        self.cancelButton.clicked.connect(self.close)
        self.show()

class Window(QtWidgets.QMainWindow):
    provider = str
    encoding = str
    signcheck = bool
    dettached = bool

    def __init__(self):
        super(Window, self).__init__()
        # uic.loadUi('/home/wolandius/git_projects/gost-crypto-gui/data/mainwindow.ui', self)

        # # Translate application
        global appdir
        # uic.loadUi('/home/wolandius/git_projects/gost-crypto-gui/data/viewmultiresults.ui', self)
        uic.loadUi(f'{appdir}/usr/share/gostcryptogui/mainwindow.ui', self) if appdir else \
            uic.loadUi('/usr/share/gostcryptogui/mainwindow.ui', self)
        aboutAction = QtWidgets.QAction(PyQt5.QtCore.QCoreApplication.translate('', 'О программе'), self)
        aboutAction.setShortcut('Ctrl+Q')
        self.menubar.addAction(aboutAction)
        self.setWindowIcon(PyQt5.QtGui.QIcon(f"{appdir}/usr/share/icons/hicolor/64x64/apps/gost-crypto-gui.png")) if appdir else \
            self.setWindowIcon(PyQt5.QtGui.QIcon("/usr/share/icons/hicolor/64x64/apps/gost-crypto-gui.png"))

        encodingActionGroup = QtWidgets.QActionGroup(self)
        self.actionBase64.setActionGroup(encodingActionGroup)
        self.actionDER.setActionGroup(encodingActionGroup)
        providerActionGroup = QtWidgets.QActionGroup(self)
        self.action_CSP.setActionGroup(providerActionGroup)
        self.actionOpenSSL.setActionGroup(providerActionGroup)
        signcheckActionGroup = QtWidgets.QActionGroup(self)
        self.actionSignCheckOn.setActionGroup(signcheckActionGroup)
        self.actionSignCheckOff.setActionGroup(signcheckActionGroup)
        dettachedActionGroup = QtWidgets.QActionGroup(self)
        self.actionDettachedOn.setActionGroup(dettachedActionGroup)
        self.actionDettachedOff.setActionGroup(dettachedActionGroup)
        outFileEnd = QtWidgets.QActionGroup(self)
        self.actionenc.setActionGroup(outFileEnd)
        self.actionp7e.setActionGroup(outFileEnd)
        self.actionp7m.setActionGroup(outFileEnd)

        aboutAction.triggered.connect(self.aboutProgram)
        self.actionDER.triggered.connect(self.setOptions)
        self.actionBase64.triggered.connect(self.setOptions)
        self.action_CSP.triggered.connect(self.setOptions)
        self.actionOpenSSL.triggered.connect(self.setOptions)
        self.actionSignCheckOn.triggered.connect(self.setOptions)
        self.actionSignCheckOff.triggered.connect(self.setOptions)
        self.actionDettachedOn.triggered.connect(self.setOptions)
        self.actionDettachedOff.triggered.connect(self.setOptions)
        self.actionenc.triggered.connect(self.setOptions)
        self.actionp7e.triggered.connect(self.setOptions)
        self.actionp7m.triggered.connect(self.setOptions)

        self.btnSign.clicked.connect(self.sign)
        self.btnVerify.clicked.connect(self.verify)
        self.btnEncrypt.clicked.connect(self.encrypt)
        self.btnDecrypt.clicked.connect(self.decrypt)
        self.readConfig()
        try:
            CryptoPro()
        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)


    def writeConfig(self):
        config = configparser.RawConfigParser()
        config.add_section('gost-crypto-gui')
        config.set('gost-crypto-gui', 'provider', self.provider)
        config.set('gost-crypto-gui', 'encoding', self.encoding)
        config.set('gost-crypto-gui', 'fileend', self.fileend)
        config.set('gost-crypto-gui', 'signcheck', 'True' if self.signcheck else 'False')
        config.set('gost-crypto-gui', 'dettached', 'True' if self.dettached else 'False')
        if not os.path.exists(os.path.expanduser('~/.gost-crypto-gui/config.cfg')):
            try:
                os.makedirs(os.path.expanduser('~/.gost-crypto-gui/'))
            except OSError:
                pass
            config.set('gost-crypto-gui', 'provider', 'cprocsp')
            config.set('gost-crypto-gui', 'encoding', 'der')
            config.set('gost-crypto-gui', 'signcheck', 'True')
            config.set('gost-crypto-gui', 'dettached', 'False')
            config.set('gost-crypto-gui', 'fileend', '.enc')
        with open(os.path.expanduser('~/.gost-crypto-gui/config.cfg'), 'w') as configfile:
            config.write(configfile)

    def readConfig(self):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.expanduser('~/.gost-crypto-gui/config.cfg'))
            self.provider = config.get('gost-crypto-gui', 'provider')
            self.encoding = config.get('gost-crypto-gui', 'encoding')
            try:
                self.fileend = config.get('gost-crypto-gui', 'fileend')
            except Exception as e:
                self.fileend = ".enc"
            self.signcheck = config.getboolean('gost-crypto-gui', 'signcheck')
            self.dettached = config.getboolean('gost-crypto-gui', 'dettached')
        except configparser.NoSectionError:
            return
        except configparser.NoOptionError:
            return
        except configparser.MissingSectionHeaderError:
            return
        self.action_CSP.setChecked(self.provider == 'cprocsp')
        self.actionOpenSSL.setChecked(self.provider == 'openssl')
        self.actionBase64.setChecked(self.encoding == 'base64')
        self.actionDER.setChecked(self.encoding == 'der')
        self.actionenc.setChecked(self.fileend == '.enc')
        self.actionp7e.setChecked(self.fileend == '.p7e')
        self.actionp7m.setChecked(self.fileend == '.p7m')

        self.actionSignCheckOn.setChecked(True if self.signcheck else False)
        self.actionSignCheckOff.setChecked(False if self.signcheck else True)
        self.actionDettachedOn.setChecked(True if self.dettached else False)
        self.actionDettachedOff.setChecked(False if self.dettached else True)

    def setOptions(self):
        if self.actionDER.isChecked():
            self.encoding = 'der'
        elif self.actionBase64.isChecked():
            self.encoding = 'base64'
        if self.action_CSP.isChecked():
            self.provider = 'cprocsp'
        if self.actionSignCheckOn.isChecked():
            self.signcheck = True
        elif self.actionSignCheckOff.isChecked():
            self.signcheck = False
        if self.actionDettachedOn.isChecked():
            self.dettached = True
        elif self.actionDettachedOff.isChecked():
            self.dettached = False
        if self.actionenc.isChecked():
            self.fileend = '.enc'
        elif self.actionp7e.isChecked():
            self.fileend = '.p7e'
        elif self.actionp7m.isChecked():
            self.fileend = '.p7m'
        self.writeConfig()

    def sign(self, *args):
        if self.sender():
            file_names = QtWidgets.QFileDialog().getOpenFileNames(self, PyQt5.QtCore.QCoreApplication.translate('', "Выберите файл(ы)"), "", "")
            if not file_names[0]:
                return
        else:
            file_names = args
        if type(file_names) is tuple and type(file_names[0]) is not list:
            file_names = (list(file_names),)
        try:
            choose = ChooseCert(parent=self, withsecret=True)
        except Exception as error:
            # QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)
            print(error)
            return
        if choose.exec_():
            cert_info = choose.getCertificate()
        else:
            return
        progressDialog = QtWidgets.QProgressDialog("", PyQt5.QtCore.QCoreApplication.translate('', "Отмена"), 0, 0, self)
        progressDialog.setValue(-1)
        if len(file_names) > 1:
            file_names = list(file_names)
            del file_names[-1]
            file_names = tuple(file_names)
        outputs = []
        for index, filenames in enumerate(file_names, start=0):
            if len(filenames) > 0:
                print(type(filenames))
                if len(filenames) == 1:
                    filename = filenames[0]
                    print("here")
                    self.call_sign_dialog(progressDialog=progressDialog, index=index, file_names=filenames,
                                          filename=filename, cert_info=cert_info, multimode=False)
                else:

                    for filename in filenames:
                        outputs.append(
                            self.call_sign_dialog(progressDialog=progressDialog, index=index, file_names=filenames,
                                                  filename=filename, cert_info=cert_info, multimode=True))
                        index += 1

        progressDialog.close()
        if len(outputs) > 0:
            MultiResultDialog(parent=self, output=outputs)

    def call_sign_dialog(self, progressDialog, index, file_names, filename, cert_info, multimode):

        progressDialog.setLabelText(
            PyQt5.QtCore.QCoreApplication.translate('', 'Подпись файла %s из %s<br>Текущий файл: %s') % (index + 1, len(file_names), filename.split('/')[-1]))
        progressDialog.show()
        if progressDialog.wasCanceled():
            return
        try:

            result = CryptoPro().sign(thumbprint=cert_info['thumbprint'], filepath=filename, encoding=self.encoding,
                                      dettached=self.dettached)
            message = ''
            if result[0]:
                message = PyQt5.QtCore.QCoreApplication.translate('', "Файл %s успешно подписан.\n\nПодписанный файл: %s\n\n") % \
                          (filename, filename + '.sig')
                message += PyQt5.QtCore.QCoreApplication.translate('', 'Сертификат:\n{p[subjectCN]}\nВыдан: {p[issuerCN]}\nСерийный номер: {p[serial]}\nНе действителен до: {p[notValidBefore]}\nНе действителен после: {p[notValidAfter]}\n\n').format(
                    p=cert_info)
            if result[1]:
                message += PyQt5.QtCore.QCoreApplication.translate('', "\n\nПредупреждение: %s") % result[1]
            progressDialog.hide()
            if not multimode:
                ResultDialog(filename, filename + '.sig',
                             message, dettached=self.dettached).show()
            else:
                message = ""
                if result[1]:
                    message += PyQt5.QtCore.QCoreApplication.translate('', "\nПредупреждение: %s") % result[1]
                return (PyQt5.QtCore.QCoreApplication.translate('', 'Файл успешно подписан'), filename + '.sig', cert_info,  message)
        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)

    def verify(self, dettach=False, *args):
        if self.sender():
            file_names = QtWidgets.QFileDialog().getOpenFileNames(self, PyQt5.QtCore.QCoreApplication.translate('', "Выберите файл(ы)"), "", "*.sig")
            if not file_names[0]:
                return
        else:
            file_names = args
        if type(file_names) is tuple and type(file_names[0]) is not list :
            file_names = (list(file_names),)
        # print(file_names, len(file_names), type(file_names))
        # file_names = (['/home/wolandius/caja.sig'],)
        progressDialog = QtWidgets.QProgressDialog("", PyQt5.QtCore.QCoreApplication.translate('', "Отмена"), 0, 0, self)
        progressDialog.setValue(-1)
        progressDialog.show()
        if len(file_names) > 1:
            file_names = list(file_names)
            del file_names[-1]
            file_names = tuple(file_names)
        for index, filenames in enumerate(file_names, start=0):
            print(index, filenames)
            if len(filenames) > 0:
                if len(filenames) == 1:
                    filename = filenames[0]
                    self.call_verify_dialog(progressDialog=progressDialog, index=index, file_names=filenames, filename=filename, dettach=dettach)
                else:
                    for filename in filenames:
                        self.call_verify_dialog(progressDialog=progressDialog, index=index, file_names=filenames, filename=filename, dettach=dettach)
                        index += 1
        progressDialog.close()

    def call_verify_dialog(self, progressDialog, index, file_names, filename, dettach):
        def add_line(text=None):
            item = QtWidgets.QListWidgetItem(cert_view.cert_listview)
            if text:
                label = QtWidgets.QLabel()
                label.setText(text)
                cert_view.cert_listview.setItemWidget(item, label)
        progressDialog.setLabelText(PyQt5.QtCore.QCoreApplication.translate('', 'Проверка подписи файла %s из %s<br>Текущий файл: %s') % (index+1, len(file_names),
                                                                                             filename.split('/')[-1]))
        if progressDialog.wasCanceled():
            return
        try:
            cert_info, chain, revoked, expired, output = CryptoPro().verify(filename, dettach)
            cert_info = list(cert_info)[0]
            cert_view = ViewCert(self)
            cert_view.report = output
            add_line(PyQt5.QtCore.QCoreApplication.translate('', 'Файл: %s') % filename)
            add_line(PyQt5.QtCore.QCoreApplication.translate('', '<b>Информация о сертификате подписи:</b>:'))
            add_line(PyQt5.QtCore.QCoreApplication.translate('', '<b>Эмитент</b>:'))
            for field, value in cert_info['issuerDN'].items():
                add_line('<b>%s</b>: %s' % (self.translate_cert_fields(field), value))
            add_line()
            add_line(PyQt5.QtCore.QCoreApplication.translate('', '<b>Субъект</b>:'))
            for field, value in cert_info['subjectDN'].items():
                add_line('<b>%s</b>: %s' % (self.translate_cert_fields(field), value))
            add_line()
            add_line(PyQt5.QtCore.QCoreApplication.translate('', '<b>Серийный номер</b>: %s') % cert_info['serial'])
            not_valid_before = datetime.strptime(cert_info['notValidBefore'], '%d/%m/%Y  %H:%M:%S')
            add_line(PyQt5.QtCore.QCoreApplication.translate('', '<b>Не действителен до</b>: %s') % datetime.strftime(not_valid_before, '%d.%m.%Y %H:%M:%S'))
            not_valid_after = datetime.strptime(cert_info['notValidAfter'], '%d/%m/%Y  %H:%M:%S')
            add_line(PyQt5.QtCore.QCoreApplication.translate('', '<b>Не действителен после</b>: %s') % datetime.strftime(not_valid_after, '%d.%m.%Y %H:%M:%S'))
            add_line()
            if chain:
                add_line(PyQt5.QtCore.QCoreApplication.translate('', '<font color="green"><b>Цепочка сертификатов была проверена.</b></font>'))
            else:
                add_line(PyQt5.QtCore.QCoreApplication.translate('', '<font color="orange"><b>ВНИМАНИЕ: Цепочка сертификатов не была проверена.</b></font>'))
            if revoked:
                add_line(
                    PyQt5.QtCore.QCoreApplication.translate('', '<font color="red"><b>ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!</b></font>'))
            elif expired:
                add_line(
                    PyQt5.QtCore.QCoreApplication.translate('', '<font color="red"><b>ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!</b></font>'))
            elif chain:
                add_line(PyQt5.QtCore.QCoreApplication.translate('', '<font color="green"><b>Сертификат действителен.</b></font>'))
            cert_view.exec_()
        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)

    def encrypt(self, *args):
        if self.sender():
            file_names = QtWidgets.QFileDialog().getOpenFileNames(self, PyQt5.QtCore.QCoreApplication.translate('', "Выберите файл(ы)"), "", "")
            if not file_names[0]:
                return
        else:
            file_names = args
        if type(file_names) is tuple and type(file_names[0]) is not list:
            file_names = (list(file_names),)
        try:
            choose = ChooseCert(parent=self, withsecret=False)
        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)
            return
        if choose.exec_():
            cert_info = choose.getCertificate()
            if cert_info == 'file':
                thumbprint = QtWidgets.QFileDialog().getOpenFileName(self, PyQt5.QtCore.QCoreApplication.translate('', "Выберите файл(ы)"), "", "*.crt *cer")
                if len(thumbprint) > 0:
                    thumbprint = list(thumbprint)
                    del thumbprint[-1]
                    thumbprint = thumbprint[0]
                    if not thumbprint[0]:
                        return
                    cert_info = list(CryptoPro().get_store_certs(crt_file=thumbprint))[0]
            else:
                thumbprint = cert_info['thumbprint']
        else:
            return
        progressDialog = QtWidgets.QProgressDialog("", PyQt5.QtCore.QCoreApplication.translate('', "Отмена"), 0, 0, self)
        progressDialog.setValue(-1)
        if len(file_names) > 1:
            file_names = list(file_names)
            del file_names[-1]
            file_names = tuple(file_names)
        outputs = []
        for index, filenames in enumerate(file_names, start=0):
            if len(filenames) > 0:
                if len(filenames) == 1:
                    filename = filenames[0]
                    self.call_encrypt_dialog(progressDialog=progressDialog, index=index, file_names=filenames, filename=filename, thumbprint=thumbprint, cert_info=cert_info, multimode=False)

                else:
                    for filename in filenames:
                        outputs.append(self.call_encrypt_dialog(progressDialog=progressDialog, index=index, file_names=filenames, filename=filename, thumbprint=thumbprint, cert_info=cert_info, multimode=True))
                        index += 1
        progressDialog.close()
        if len(outputs) > 0:
            MultiResultDialog(parent=self, output=outputs)

    def call_encrypt_dialog(self, progressDialog, index, file_names, filename, thumbprint, cert_info, multimode):
        progressDialog.setLabelText(PyQt5.QtCore.QCoreApplication.translate('', 'Шифрование файла %s из %s<br>Текущий файл: %s') % (index+1, len(file_names),
                                                                                        filename.split('/')[-1]))

        progressDialog.show()
        if progressDialog.wasCanceled():
            return
        try:
            encrypted, chain, revoked, expired = CryptoPro().encrypt(thumbprint, filename, self.encoding, self.fileend)
            if encrypted:
                message = PyQt5.QtCore.QCoreApplication.translate('', 'Файл %s успешно зашифрован.\n\nЗашифрованный файл: %s\n\n') % (
                filename, filename + self.fileend)
                message += PyQt5.QtCore.QCoreApplication.translate('', 'Сертификат:\n{p[subjectCN]}\nВыдан: {p[issuerCN]}\nСерийный номер: {p[serial]}\nНе действителен до: {p[notValidBefore]}\nНе действителен после: {p[notValidAfter]}\n\n').format(
                    p=cert_info)
                if not chain:
                    message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Статус отзыва сертификата не был проверен!\n')
                if revoked:
                    message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!\n')
                if expired:
                    message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!\n')
                progressDialog.hide()
                if not multimode:
                    ResultDialog(filename, filename + self.fileend, message).show()
                else:
                    message = ""
                    if not chain:
                        message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Статус отзыва сертификата не был проверен!\n')
                    if revoked:
                        message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!\n')
                    if expired:
                        message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!\n')

                    return (PyQt5.QtCore.QCoreApplication.translate('', 'Файл успешно зашифрован'), filename + self.fileend, cert_info, message)

        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)
    def decrypt(self, *args):
        if self.sender():
            file_names = QtWidgets.QFileDialog().getOpenFileNames(self, PyQt5.QtCore.QCoreApplication.translate('', "Выберите файл(ы)"), "", "*.enc *.encr *.p7e *p7m")
            if not file_names[0]:
                return
        else:
            file_names = args
        if type(file_names) is tuple and type(file_names[0]) is not list:
            file_names = (list(file_names),)
        try:
            choose = ChooseCert(parent=self, withsecret=True)
        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('', "Cообщение"), PyQt5.QtCore.QCoreApplication.translate('', "Произошла ошибка:\n%s") % error)
            return
        if choose.exec_():
            cert_info = choose.getCertificate()
        else:
            return
        progressDialog = QtWidgets.QProgressDialog("", PyQt5.QtCore.QCoreApplication.translate('', "Отмена"), 0, 0, self)
        progressDialog.setValue(-1)
        if len(file_names) > 1:
            file_names = list(file_names)
            del file_names[-1]
            file_names = tuple(file_names)
        for index, filenames in enumerate(file_names, start=0):
            if len(filenames) > 0:
                if len(filenames) == 1:
                    filename = filenames[0]
                    self.call_decrypt_dialog(progressDialog=progressDialog, index=index, file_names=filenames,
                                             filename=filename, cert_info=cert_info)

                else:
                    for filename in filenames:
                        self.call_decrypt_dialog(progressDialog=progressDialog, index=index, file_names=filenames,
                                                 filename=filename, cert_info=cert_info)
                        index += 1
        progressDialog.close()

    def call_decrypt_dialog(self, progressDialog, index, file_names, filename, cert_info):
        progressDialog.setLabelText(PyQt5.QtCore.QCoreApplication.translate('', 'Расшифровка файла %s из %s<br>Текущий файл: %s') % (index+1, len(file_names),
                                                                                         filename.split('/')[-1]))
        progressDialog.show()
        if progressDialog.wasCanceled():
            return
        try:
            decrypted, chain, revoked, expired = CryptoPro().decrypt(cert_info['thumbprint'], filename)
            if decrypted:
                message = PyQt5.QtCore.QCoreApplication.translate('', 'Файл %s успешно расшифрован.\n\nРасшифрованный файл: %s\n\n') % (filename, filename[:-4])
                if not chain:
                    message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Статус отзыва сертификата не был проверен!\n')
                if revoked:
                    message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Один или несколько сертификатов в цепочке отозваны!\n')
                if expired:
                    message += PyQt5.QtCore.QCoreApplication.translate('', 'ВНИМАНИЕ: Срок действия сертификата истек или еще не наступил!\n')
                progressDialog.hide()
                ResultDialog(filename, filename[:-4], message).show()
        except Exception as error:
            QtWidgets.QMessageBox().warning(self, PyQt5.QtCore.QCoreApplication.translate('',"Cообщение"), PyQt5.QtCore.QCoreApplication.translate('',"Произошла ошибка:\n%s") % error)
    def translate_cert_fields(self, fieldname):
        fields = {'1.2.840.113549.1.9.2': PyQt5.QtCore.QCoreApplication.translate('', 'неструктурированное имя'),
                  '1.2.643.5.1.5.2.1.2': PyQt5.QtCore.QCoreApplication.translate('', 'код должности'),
                  '1.2.643.5.1.5.2.1.1': PyQt5.QtCore.QCoreApplication.translate('', 'код структурного подразделения ФССП России (ВКСП)'),
                  '1.2.643.5.1.5.2.2.1': PyQt5.QtCore.QCoreApplication.translate('', 'Полномочия публикации обновлений ПО'),
                  '1.2.643.5.1.5.2.2.2': PyQt5.QtCore.QCoreApplication.translate('', 'Подсистема АИС ФССП России'),
                  '1.2.643.5.1.24.2.9': PyQt5.QtCore.QCoreApplication.translate('', 'Главный судебный пристав Российской Федерации'),
                  '1.2.643.5.1.24.2.10': PyQt5.QtCore.QCoreApplication.translate('', 'Заместитель главного судебного пристава Российской Федерации'),
                  '1.2.643.5.1.24.2.11': PyQt5.QtCore.QCoreApplication.translate('', 'Главный судебный пристав субъекта Российской Федерации'),
                  '1.2.643.5.1.24.2.12': PyQt5.QtCore.QCoreApplication.translate('', 'Заместитель главного судебного пристава субъекта Российской Федерации'),
                  '1.2.643.5.1.24.2.13': PyQt5.QtCore.QCoreApplication.translate('', 'Старший судебный пристав'),
                  '1.2.643.5.1.24.2.14': PyQt5.QtCore.QCoreApplication.translate('', 'Судебный пристав-исполнитель'),
                  '1.2.643.100.2.1': PyQt5.QtCore.QCoreApplication.translate('', 'Доступ к СМЭВ (ФЛ)'),
                  '1.2.643.100.2.2': PyQt5.QtCore.QCoreApplication.translate('', 'Доступ к СМЭВ (ЮЛ)'),
                  '1.2.643.2.2.34.2': PyQt5.QtCore.QCoreApplication.translate('', 'Временный доступ к Центру Регистрации'),
                  '1.2.643.2.2.34.4': PyQt5.QtCore.QCoreApplication.translate('', 'Администратор Центра Регистрации КриптоПро УЦ'),
                  '1.2.643.2.2.34.5': PyQt5.QtCore.QCoreApplication.translate('', 'Оператор Центра Регистрации КриптоПро УЦ'),
                  '1.2.643.2.2.34.6': PyQt5.QtCore.QCoreApplication.translate('', 'Пользователь центра регистрации КриптоПро УЦ'),
                  '1.2.643.2.2.34.7': PyQt5.QtCore.QCoreApplication.translate('', 'Центр Регистрации КриптоПро УЦ'),
                  '1.3.6.1.5.5.7.3.1': PyQt5.QtCore.QCoreApplication.translate('', 'Проверка подлинности сервера'),
                  '1.3.6.1.5.5.7.3.2': PyQt5.QtCore.QCoreApplication.translate('', 'Проверка подлинности клиента'),
                  '1.3.6.1.5.5.7.3.4': PyQt5.QtCore.QCoreApplication.translate('', 'Защищенная электронная почта'),
                  '1.3.6.1.5.5.7.3.8': PyQt5.QtCore.QCoreApplication.translate('', 'Установка штампа времени'),
                  '1.2.643.3.61.502710.1.6.3.4.1.1': PyQt5.QtCore.QCoreApplication.translate('', 'Администратор организации'),
                  '1.2.643.3.61.502710.1.6.3.4.1.2': PyQt5.QtCore.QCoreApplication.translate('', 'Уполномоченный специалист'),
                  '1.2.643.3.61.502710.1.6.3.4.1.3': PyQt5.QtCore.QCoreApplication.translate('', 'Должностное лицо с правом подписи контракта'),
                  '1.2.643.3.61.502710.1.6.3.4.1.4': PyQt5.QtCore.QCoreApplication.translate('', 'Специалист с правом направления проекта контракта участнику размещения заказа'),
                  'CN': PyQt5.QtCore.QCoreApplication.translate('', 'общее имя'),
                  'SN': PyQt5.QtCore.QCoreApplication.translate('', 'фамилия'),
                  'G': PyQt5.QtCore.QCoreApplication.translate('', 'имя и отчество'),
                  'I': PyQt5.QtCore.QCoreApplication.translate('', 'инициалы'),
                  'T': PyQt5.QtCore.QCoreApplication.translate('', 'должность'),
                  'OU': PyQt5.QtCore.QCoreApplication.translate('', 'структурное подразделение'),
                  'O': PyQt5.QtCore.QCoreApplication.translate('', 'организация'),
                  'L': PyQt5.QtCore.QCoreApplication.translate('', 'населенный пункт'),
                  'S': PyQt5.QtCore.QCoreApplication.translate('', 'субъект РФ'),
                  'C': PyQt5.QtCore.QCoreApplication.translate('', 'страна'),
                  'E': PyQt5.QtCore.QCoreApplication.translate('', 'адрес электронной почты'),
                  'INN': PyQt5.QtCore.QCoreApplication.translate('', 'ИНН'),
                  'OGRN': PyQt5.QtCore.QCoreApplication.translate('', 'ОГРН'),
                  'SNILS': PyQt5.QtCore.QCoreApplication.translate('', 'СНИЛС'),
                  'STREET': PyQt5.QtCore.QCoreApplication.translate('', 'название улицы, номер дома'),
                  'StreetAddress': PyQt5.QtCore.QCoreApplication.translate('', 'адрес места нахождения'),
                  'Unstructured Name': PyQt5.QtCore.QCoreApplication.translate('', 'неструктурированное имя')}
        try:
            return fields[fieldname]
        except KeyError:
            return fieldname

    def aboutProgram(self):
        text1 = PyQt5.QtCore.QCoreApplication.translate('', '<br>2019г. Борис Макаренко<br>УИТ ФССП России')
        text2 = PyQt5.QtCore.QCoreApplication.translate('', "<br>E-mail: <a href=mailto:makarenko@fssprus.ru'>makarenko@fssprus.ru</a>")
        text3 = PyQt5.QtCore.QCoreApplication.translate('', "<br> <a href='mailto:bmakarenko90@gmail.com'>bmakarenko90@gmail.com</a><br>")
        text4 = PyQt5.QtCore.QCoreApplication.translate('', '<br>2022-2023г. Владлен Мурылев<br>ООО "РЕД СОФТ"')
        text5 = PyQt5.QtCore.QCoreApplication.translate('', "<br>E-mail: <a href='mailto:redos.support@red-soft.ru'>redos.support@red-soft.ru</a><br>")
        text6 = PyQt5.QtCore.QCoreApplication.translate('', "<a href='http://opensource.org/licenses/MIT'>Лицензия MIT</a>")
        QtWidgets.QMessageBox().about(self, PyQt5.QtCore.QCoreApplication.translate('', "О программе"),
                                  f"<b>gost-crypto-gui {VERSION}</b><br>"
                                  f"{text1}{text2}{text3}{text4}{text5}{text6}"
                                      )

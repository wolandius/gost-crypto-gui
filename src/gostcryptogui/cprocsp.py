#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (c) 2018 Борис Макаренко
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

Copyright (c) 2018 Boris Makarenko
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
import os
import platform
import shutil
import subprocess
import re
import PyQt5
from PyQt5.QtCore import QCoreApplication



def nongui(fun):
    """Decorator running the function in non-gui thread while
    processing the gui events."""
    from multiprocessing.pool import ThreadPool
    from PyQt5.QtWidgets import QApplication

    def wrap(*args, **kwargs):
        pool = ThreadPool(processes=1)
        async_ = pool.apply_async(fun, args, kwargs)
        while not async_.ready():
            async_.wait(0.01)
            QApplication.processEvents()
        return async_.get()

    return wrap

# Класс CryptoPro предназнаечен для выполнения криптографических операций над файлами средствами КриптоПро CSP

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

class CryptoPro:
    arch = str

    # В конструкторе класса производится проверка текущей архитектуры и доступность
    # исполняемых файлов Крипто Про
    def __init__(self):
        if platform.machine() == 'x86_64':
            self.arch = 'amd64'
        elif platform.machine() == 'i686':
            self.arch = 'ia32'
        elif  platform.machine() == 'e2k':
            self.arch = 'e2k64'
        elif  platform.machine() == 'aarch64':
            self.arch = 'aarch64'
        else:
            raise Exception(PyQt5.QtCore.QCoreApplication.translate('','Текущая архитектура %s не поддерживается') % platform.machine())
        if not os.path.exists('/opt/cprocsp/bin/%s/certmgr' % self.arch) or not os.path.exists('/opt/cprocsp/bin/%s/cryptcp' % self.arch):
            raise Exception(PyQt5.QtCore.QCoreApplication.translate('','СКЗИ Крипто Про CSP или некоторые его компоненты не установлены.'))
        # КОСТЫЛЬ: Создаем временную директорию для хранения отсоединенных подписей
        if not os.path.exists('/tmp/gost-crypto-gui'):
            os.makedirs('/tmp/gost-crypto-gui')

    def get_cspversion(self):
        csptest = subprocess.Popen(['/opt/cprocsp/bin/%s/csptest' % self.arch, '-keyset', '-verifycontext'],
                                   stdout=subprocess.PIPE)
        temp_output = csptest.communicate()[0].decode('utf-8')
        output = temp_output.split('\n')[0]
        r = re.search(r'v([0-9.]*[0-9]+)\ (.+)\ Release Ver\:([0-9.]*[0-9]+)\ OS\:([a-zA-z]+)', output)
        return r.group(1), r.group(2), r.group(3), r.group(4)

    # Метод error_description принимает код ошибки и возвращает её описание. Если такой ошибки в словаре нет,
    # то код ошибки возвращается обратно
    @staticmethod
    def error_description(error):
        errors = {'0x20000064': PyQt5.QtCore.QCoreApplication.translate('', 'Мало памяти'),
                  '0x20000065': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось открыть файл'),
                  '0x20000066': PyQt5.QtCore.QCoreApplication.translate('', 'Операция отменена пользователем'),
                  '0x20000067': PyQt5.QtCore.QCoreApplication.translate('', 'Некорректное преобразование BASE64'),
                  '0x20000068': PyQt5.QtCore.QCoreApplication.translate('', 'Если указан параметр -help, то других быть не должно'),
                  '0x200000c8': PyQt5.QtCore.QCoreApplication.translate('', 'Указан лишний файл'),
                  '0x200000c9': PyQt5.QtCore.QCoreApplication.translate('', 'Указан неизвестный ключ'),
                  '0x200000ca': PyQt5.QtCore.QCoreApplication.translate('', 'Указана лишняя команда'),
                  '0x200000cb': PyQt5.QtCore.QCoreApplication.translate('', 'Для ключа не указан параметр'),
                  '0x200000cc': PyQt5.QtCore.QCoreApplication.translate('', 'Не указана команда'),
                  '0x200000cd': PyQt5.QtCore.QCoreApplication.translate('', 'Не указан необходимый ключ'),
                  '0x200000ce': PyQt5.QtCore.QCoreApplication.translate('', 'Указан неверный ключ'),
                  '0x200000cf': PyQt5.QtCore.QCoreApplication.translate('', 'Параметром ключа -q должно быть натуральное число'),
                  '0x200000d0': PyQt5.QtCore.QCoreApplication.translate('', 'Не указан входной файл'),
                  '0x200000d1': PyQt5.QtCore.QCoreApplication.translate('', 'Не указан выходной файл'),
                  '0x200000d2': PyQt5.QtCore.QCoreApplication.translate('', 'Команда не использует параметр с именем файла'),
                  '0x200000d3': PyQt5.QtCore.QCoreApplication.translate('', 'Не указан  файл сообщения'),
                  '0x2000012c': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось открыть хранилище сертификатов:'),
                  '0x2000012d': PyQt5.QtCore.QCoreApplication.translate('', 'Сертификаты не найдены'),
                  '0x2000012e': PyQt5.QtCore.QCoreApplication.translate('', 'Найдено более одного сертификата (ключ -1)'),
                  '0x2000012f': PyQt5.QtCore.QCoreApplication.translate('', 'Команда подразумевает использование только одного сертификата'),
                  '0x20000130': PyQt5.QtCore.QCoreApplication.translate('', 'Неверно указан номер'),
                  '0x20000131': PyQt5.QtCore.QCoreApplication.translate('', 'Нет используемых сертификатов'),
                  '0x20000132': PyQt5.QtCore.QCoreApplication.translate('', 'Данный сертификат не может применяться для этой операции'),
                  '0x20000133': PyQt5.QtCore.QCoreApplication.translate('', 'Цепочка сертификатов не проверена. Либо сертификат был отозван или срок действия истек.'),
                  '0x20000134': PyQt5.QtCore.QCoreApplication.translate('', 'Криптопровайдер, поддерживающий необходимый алгоритм не найден'),
                  '0x20000135': PyQt5.QtCore.QCoreApplication.translate('', 'Неудачный ввод пароля ключевого контейнера'),
                  '0x20000136': PyQt5.QtCore.QCoreApplication.translate('', 'Ошибка связи с закрытым ключом'),
                  '0x20000190': PyQt5.QtCore.QCoreApplication.translate('', 'Не указана маска файлов'),
                  '0x20000191': PyQt5.QtCore.QCoreApplication.translate('', 'Указаны несколько масок файлов'),
                  '0x20000192': PyQt5.QtCore.QCoreApplication.translate('', 'Файлы не найдены'),
                  '0x20000193': PyQt5.QtCore.QCoreApplication.translate('', 'Задана неверная маска'),
                  '0x20000194': PyQt5.QtCore.QCoreApplication.translate('', 'Неверный хеш'),
                  '0x200001f4': PyQt5.QtCore.QCoreApplication.translate('', 'Ключ -start указан, а выходной файл нет'),
                  '0x200001f5': PyQt5.QtCore.QCoreApplication.translate('', 'Содержимое файла - не подписанное сообщение'),
                  '0x200001f6': PyQt5.QtCore.QCoreApplication.translate('', 'Неизвестный алгоритм подписи'),
                  '0x200001f7': PyQt5.QtCore.QCoreApplication.translate('', 'Сертификат автора подписи не найден'),
                  '0x200001f8': PyQt5.QtCore.QCoreApplication.translate('', 'Подпись не найдена'),
                  '0x200001f9': PyQt5.QtCore.QCoreApplication.translate('', 'Подпись не верна'),
                  '0x20000200': PyQt5.QtCore.QCoreApplication.translate('', 'Штамп времени не верен'),
                  '0x20000258': PyQt5.QtCore.QCoreApplication.translate('', 'Содержимое файла - не зашифрованное сообщение'),
                  '0x20000259': PyQt5.QtCore.QCoreApplication.translate('', 'Неизвестный алгоритм шифрования'),
                  '0x2000025a': PyQt5.QtCore.QCoreApplication.translate('', 'Не найден сертификат с соответствующим секретным ключом'),
                  '0x200002bc': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось инициализировать cOM'),
                  '0x200002bd': PyQt5.QtCore.QCoreApplication.translate('', 'Контейнеры не найдены'),
                  '0x200002be': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось получить ответ от сервера'),
                  '0x200002bf': PyQt5.QtCore.QCoreApplication.translate('', 'Сертификат не найден в ответе сервера'),
                  '0x200002c0': PyQt5.QtCore.QCoreApplication.translate('', 'Файл не содержит идентификатор запроса:'),
                  '0x200002c1': PyQt5.QtCore.QCoreApplication.translate('', 'Некорректный адрес ЦС'),
                  '0x200002c2': PyQt5.QtCore.QCoreApplication.translate('', 'Получен неверный cookie'),
                  '0x20000320': PyQt5.QtCore.QCoreApplication.translate('', 'Серийный номер содержит недопустимое количество символов'),
                  '0x20000321': PyQt5.QtCore.QCoreApplication.translate('', 'Неверный код продукта'),
                  '0x20000322': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось проверить серийный номер'),
                  '0x20000323': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось сохранить серийный номер'),
                  '0x20000324': PyQt5.QtCore.QCoreApplication.translate('', 'Не удалось загрузить серийный номер'),
                  '0x20000325': PyQt5.QtCore.QCoreApplication.translate('', 'Лицензия просрочена'),
                  '0x0000065b': PyQt5.QtCore.QCoreApplication.translate('', 'Отсутствует лицензия КриптоПро CSP')}
        try:
            return errors[error]
        except KeyError:
            return error

    # TODO Показывать алгоритмы подписи и открытого ключа
    # Генератор get_store_certs выдает найденные в заданном хранилище сертификаты в виде словарей
    def get_store_certs(self, store=None, crt_file=None):
        if crt_file:
            certmgr = subprocess.Popen(['/opt/cprocsp/bin/%s/certmgr' % self.arch, '-list', '-file', crt_file],
                                       stdout=subprocess.PIPE)
        elif store:
            certmgr = subprocess.Popen(['/opt/cprocsp/bin/%s/certmgr' % self.arch, '-list', '-store', store],
                                   stdout=subprocess.PIPE)
        else:
            pass
        output = certmgr.communicate()[0]
        cert_dict = self.create_certs_dict(output.decode('utf-8'))
        for k in cert_dict:
            single_cert_dict = self.create_single_cert_dict(cert_dict[k])
            cert_keys = list(single_cert_dict.keys())
            issuerKey = list(filter(lambda v: re.match(r'Issuer|Издатель', v), cert_keys))
            subjectKey = list(filter(lambda v: re.match(r'Subject|Субъект', v), cert_keys))
            SerialKey = list(filter(lambda v: re.match(r'Serial|Серийный номер', v), cert_keys))
            SHA1Key= list(filter(lambda v: re.match(r'SHA1 Hash|Хэш SHA1|SHA1 отпечаток', v), cert_keys))
            BeforeKey = list(filter(lambda v: re.match(r'Not valid before|Выдан', v), cert_keys))
            AfterKey = list(filter(lambda v: re.match(r'Not valid after|Истекает', v), cert_keys))
            PrivateKey = list(filter(lambda v: re.match(r'PrivateKey Link|Ссылка на ключ', v), cert_keys))

            issuerDN = self.create_dict_from_strk(single_cert_dict[issuerKey[0]])
            issuerCN = issuerDN['CN'].strip()
            subjectDN = self.create_dict_from_strk(single_cert_dict[subjectKey[0]])
            subjectCN = subjectDN['CN'].strip()
            secretKey = single_cert_dict[PrivateKey[0]].strip()
            serial = single_cert_dict[SerialKey[0]].strip()
            thumbprint = single_cert_dict[SHA1Key[0]].strip()
            notValidBefore = re.sub("UTC", "", single_cert_dict[BeforeKey[0]]).strip()
            notValidAfter = re.sub("UTC", "", single_cert_dict[AfterKey[0]]).strip()

            yield dict(issuerDN=issuerDN, issuerCN=issuerCN, subjectDN=subjectDN, subjectCN=subjectCN,
                       secretKey=secretKey, serial=serial, thumbprint=thumbprint, notValidBefore=notValidBefore,
                       notValidAfter=notValidAfter)


    def create_certs_dict(self, strk):
        strk_keys = re.findall("\d+-{7}\n", strk.strip(), re.MULTILINE + re.DOTALL)
        strk_list = re.split("\d+-{7}\n", strk.strip(), re.MULTILINE + re.DOTALL)[1:]
        new_dict = {}
        counter_keys = 0
        for i in range(0, len(strk_list)):
            temp_str = strk_list[i].strip()
            new_dict[strk_keys[counter_keys]] = temp_str if i != len(strk_list)-1 else re.split("\==.*\n", temp_str)[0]
            counter_keys += 1
        return new_dict

    def create_single_cert_dict(self, strk):
        if re.findall(r'(Назначение/EKU|Extended Key Usage)', strk.strip(), re.MULTILINE + re.DOTALL):
            parts = re.split(r'(Назначение/EKU|Extended Key Usage)', strk.strip(), re.MULTILINE + re.DOTALL)
            strk_keys1 = re.findall("^([A-Za-zА-Яа-я0-9 ]+?)\:", parts[0], re.MULTILINE + re.DOTALL)
            strk_rows = re.findall(r'^([A-Za-zА-Яа-я0-9 ]+?)\:(.+?)[\n].*?', parts[0], re.MULTILINE + re.DOTALL)
            keys_dict_count = {i[0].strip(): strk_keys1.count(i[0]) for i in strk_rows}
            new_dict = {}
            for k in keys_dict_count:
                new_dict[k] = [] if keys_dict_count[k] > 1 else ""
            for el in strk_rows:
                el0 = el[0].strip()
                if type(new_dict[el0]) is str:
                    new_dict[el0] = el[1]
                elif type(new_dict[el0]) is list:
                    new_dict[el0].append(el[1])
            strk_keys2 = parts[1]
            strk_rows2 = parts[2]
            strk_rows2 = re.sub(":", "", strk_rows2.strip()).split("\n")
            new_dict[strk_keys2] = []
            for k in strk_rows2:
                new_dict[strk_keys2].append(k.strip())
        else:
            strk_rows = re.findall(r'^([A-Za-zА-Яа-я0-9 ]+?)\:(.+?)[\n].*?', strk.strip(), re.MULTILINE + re.DOTALL)
            strk_keys = re.findall("^([A-Za-zА-Яа-я0-9 ]+?)\:", strk.strip(), re.MULTILINE + re.DOTALL)
            keys_dict_count = {i[0].strip(): strk_keys.count(i[0]) for i in strk_rows}
            new_dict = {}
            for k in keys_dict_count:
                new_dict[k] = [] if keys_dict_count[k] > 1 else ""
            for el in strk_rows:
                el0 = el[0].strip()
                if type(new_dict[el0]) is str:
                    new_dict[el0] = el[1]
                elif type(new_dict[el0]) is list:
                    new_dict[el0].append(el[1])
        return new_dict

    def create_dict_from_strk(self, strk):
        strk_keys = re.findall("([A-Za-z0-9\.]+?)=", strk.strip())

        strk_list = re.split("([A-Za-z0-9\.]+?)=", strk.strip())[1:]
        new_dict = {}
        counter_keys = 0
        for i in range(1, len(strk_list), 2):
            temp_str = strk_list[i].strip()
            new_dict[strk_keys[counter_keys]] = temp_str[:-1] if "," == temp_str[-1] else temp_str
            counter_keys += 1
        return new_dict


    # Метод sign выполняет операцию подписи заданного файла(filepath), при помощи заданного SHA-отпечатка
    # сертификата(thumbprint) и используя заданную кодировку(encoding): DER или BASE64
    # Путь до файла должен быть абсолютным. Подписанный файл сохраняется в той же директории с расширением '.sig'
    # Возвращает кортеж с результатом выполнения (True) и предупреждением(если имеется)
    # TODO Сделать возможность добавления подписи
    @nongui
    def sign(self, thumbprint, filepath, encoding, dettached=False):
        # Исправляем криптопрошные крокозябры
        # print(thumbprint, filepath, encoding, dettached)
        new_env = dict(os.environ)
        new_env['LANG'] = 'en_US.UTF-8'
        # new_env['timeout'] = '10'
        cryptcp_args = ['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-thumbprint', thumbprint, filepath]
        if dettached:
            cryptcp_args.insert(1, '-signf')
            cryptcp_args.insert(2, '-cert')
        else:
            cryptcp_args.insert(1, '-sign')
        if encoding == 'der':
            cryptcp_args.insert(-1, '-der')
        print(cryptcp_args)
        # cryptcp_args.insert(-1, '-nochain')
        # cryptcp_args.insert(-1, '-norev')
        cryptcp = subprocess.Popen(cryptcp_args, cwd=os.path.dirname(filepath), stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env)

        # Согласиться
        output, errors = cryptcp.communicate(b'Y\n')

        errorcode = re.search(r'(?:ErrorCode: |ReturnCode: )(?P<errorcode>\w+)', errors.decode('utf-8'),
                              re.MULTILINE + re.DOTALL).groupdict()['errorcode'] if errors is not None else \
            re.search(r'(?:ErrorCode: |ReturnCode: )(?P<errorcode>\w+)', output.decode('utf-8'),
                              re.MULTILINE + re.DOTALL).groupdict()['errorcode']
        # КОСТЫЛЬ переименовываем отсоединенные подписи из sgn в sig
        if dettached:
            try:
                os.rename(filepath+'.sgn', filepath+'.sig')
            except:
                pass
        if not int(errorcode, 0) == 0:
            raise Exception(self.error_description(errorcode))
        # Проверяем наличие в выводе сообщения об ошибке проверки цепочки сертификатов
        elif 'Certificate chain is not checked for this certificate' in output.decode('utf-8'):
            return True, self.error_description('0x20000133')
        else:
            return True, None

    # Метод verify проверяет подпись файла(filepath).
    # Если требуется при этом отсоединить подпись от файла, указываем параметр dettach=True
    # Возвращает кортеж, состоящий из словаря сертификата, булева значения
    # указывающего была ли проверена цепочка сертификатов или нет(True - была, False - нет) и
    # полный вывод запуска утилиты cryptcp для сохранения
    # TODO Сделать возможность проверки нескольких подписей в одном файле
    @nongui
    def verify(self, filepath, dettach=False):
        # Если это не файл подписи, проверяем лежащий рядом файл с расширением '.sig'
        if not filepath[-4:] == '.sig':
            filepath += '.sig'
            dettach = False
        # Исправляем криптопрошные крокозябры
        new_env = dict(os.environ)
        new_env['LANG'] = 'en_US.UTF-8'
        if dettach:
            cryptcp = subprocess.Popen(
                ['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-delsign', filepath],
                stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env, shell=False)
        else:
            cryptcp = subprocess.Popen(['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-verify', '-verall', filepath],
                                       stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env, shell=False)
        # Согласиться
        output, errors = cryptcp.communicate(b'Y\n')

        errorcode = re.search(r'(?:ErrorCode: |ReturnCode: )(?P<errorcode>\w+)', output.decode('utf-8'),
                              re.MULTILINE + re.DOTALL).groupdict()['errorcode']
        cert_info = self.get_store_certs(crt_file=filepath)

        # КОСТЫЛЬ если подпись оказалась отсоединенной, копируем её в tmp и проверяем при помощи -vsignf
        if errorcode == '0x00000057':
            tmpname=r'/tmp/gost-crypto-gui/'+filepath.split('/')[-1][:-3]+'sgn'
            shutil.copy(filepath, tmpname)
            cryptcp = subprocess.Popen(['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-vsignf',
                                        '-dir', '/tmp/gost-crypto-gui/', '-f', tmpname, filepath[:-4]],
                                       stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env, shell=False)

            output, errors = cryptcp.communicate(b'Y\nY\n')

            # output = cryptcp.stdout.read().decode('utf-8')
            cert_info = self.get_store_certs(crt_file=tmpname)

        chainisverified = ('The certificate revocation status or one of the certificates in the certificate chain is'
                           ' unknown.' not in output.decode('utf-8')) \
                          and ('Certificate chain is not checked for this certificate' not in output.decode('utf-8'))
        chainisrevoked = 'Trust for this certificate or one of the certificates in the certificate chain has' \
                         ' been revoked' in output.decode('utf-8')
        certisexpired = 'This certificate or one of the certificates in the certificate chain is not time valid.' in output.decode('utf-8')
        errorcode = re.search(r'(?:ErrorCode: |ReturnCode: )(?P<errorcode>\w+)', output.decode('utf-8'),
                              re.MULTILINE + re.DOTALL).groupdict()['errorcode']
        if not int(errorcode, 0) == 0:
            raise Exception(self.error_description(errorcode))
        else:
            return cert_info, chainisverified, chainisrevoked, certisexpired, output

    # Метод encrypt шифрует заданный файл(filepath), при помощи SHA-отпечатка сертификата
    #  или имени файла сертификата (thumbprint), и используя заданную кодировку(encoding): DER или BASE64
    # Путь до файла должен быть абсолютным. Зашифрованный файл сохраняется в той же директории с расширением '.enc'
    @nongui
    def encrypt(self, thumbprint, filepath, encoding, fileend):
        # Исправляем криптопрошные крокозябры
        new_env = dict(os.environ)
        new_env['LANG'] = 'en_US.UTF-8'

        if encoding == 'der':
            cryptcp = subprocess.Popen(['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-encr', '-der',
                                         '-f' if thumbprint[0] == '/' else '-thumbprint', thumbprint, filepath, filepath + fileend],
                                       stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env, shell=False)
        else:
            cryptcp = subprocess.Popen(
                ['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-encr', '-f' if thumbprint[0] == '/' else '-thumbprint', thumbprint, filepath,
                 filepath + fileend],
                stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env, shell=False)
        # Согласит
        output, errors = cryptcp.communicate(b'Y\n')
        # output = cryptcp.stdout.read().decode('utf-8')
        chainisverified = ('The certificate revocation status or one of the certificates in the certificate chain is'
                           ' unknown.' not in output.decode('utf-8')) \
                          and ('Certificate chain is not checked for this certificate' not in output.decode('utf-8'))
        chainisrevoked = 'Trust for this certificate or one of the certificates in the certificate chain has' \
                         ' been revoked' in output.decode('utf-8')
        certisexpired = 'This certificate or one of the certificates in the certificate chain is not time valid.' in output.decode('utf-8')
        errorcode = re.search(r'(?:ErrorCode: |ReturnCode: )(?P<errorcode>\w+)', output.decode('utf-8'),
                              re.MULTILINE + re.DOTALL).groupdict()['errorcode']
        if not int(errorcode, 0) == 0:
            raise Exception(self.error_description(errorcode))
        else:
            return True, chainisverified, chainisrevoked, certisexpired

    # Метод decrypt расшифровывает заданный файл(filepath) при помощи SHA-отпечатка сертификата(thumbprint)
    # Расшифрованный файл сохраняется в той же директории, лишаясь расширения '.enc'
    @nongui
    def decrypt(self, thumbprint, filepath):
        if not filepath[-4:] == '.enc':
            pass
        # Исправляем криптопрошные крокозябры
        new_env = dict(os.environ)
        new_env['LANG'] = 'en_US.UTF-8'

        cryptcp = subprocess.Popen(['/opt/cprocsp/bin/%s/cryptcp' % self.arch, '-decr',
                                    '-thumbprint', thumbprint, filepath, filepath[:-4]],
                                   stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=new_env, shell=False)
        # Согласит
        output, errors = cryptcp.communicate(b'Y\n')

        chainisverified = ('The certificate revocation status or one of the certificates in the certificate chain is'
                           ' unknown.' not in output.decode('utf-8')) \
                          and ('Certificate chain is not checked for this certificate' not in output.decode('utf-8'))
        chainisrevoked = 'Trust for this certificate or one of the certificates in the certificate chain has' \
                         ' been revoked' in output.decode('utf-8')
        certisexpired = 'This certificate or one of the certificates in the certificate chain is not time valid.' in output.decode('utf-8')
        errorcode = re.search(r'(?:ErrorCode: |ReturnCode: )(?P<errorcode>\w+)', output.decode('utf-8'),
                              re.MULTILINE + re.DOTALL).groupdict()['errorcode']
        if not int(errorcode, 0) == 0:
            raise Exception(self.error_description(errorcode))
        else:
            return True, chainisverified, chainisrevoked, certisexpired

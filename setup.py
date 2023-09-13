import sys

from setuptools import setup, find_packages
import pathlib
import os

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

data_files=[
                        ("share/applications/", ["data/gost-crypto-gui.desktop"]),
                        ("share/icons/hicolor/16x16/apps/",   ["pics/16x16/gost-crypto-gui.png"]),
                        ("share/icons/hicolor/24x24/apps/",   ["pics/24x24/gost-crypto-gui.png"]),
                        ("share/icons/hicolor/32x32/apps/",   ["pics/32x32/gost-crypto-gui.png"]),
                        ("share/icons/hicolor/48x48/apps/",   ["pics/48x48/gost-crypto-gui.png"]),
                        ("share/icons/hicolor/64x64/apps/",   ["pics/64x64/gost-crypto-gui.png"]),
                        ("share/icons/hicolor/128x128/apps/", ["pics/128x128/gost-crypto-gui.png"]),
                        ("share/mime/applications/", [
                                                        "data/x-extension-sgn.xml",
                                                        "data/x-extension-sig.xml",
                                                        "data/x-extension-enc.xml",
                                                     ]
                        ),
                        ("share/gostcryptogui/", [
                                                        "data/viewmultiresults.ui",
                                                        "data/mainwindow.ui",
                                                        "data/selectcert.ui",
                                                        "data/viewcert.ui",
                                                        "pics/encrypted.png",
                                                        "pics/signed.png",
                                                        "pics/emblem-nochain.png",
                                                        "pics/emblem-unverified.png",
                                                        "pics/emblem-verified.png",
                                                        "data/locales/GostCryptoGui-en_US.qm",
                                                     ]
                        ),


    ]

if "WITH_CAJA" in os.environ and os.environ['WITH_CAJA'] == "yes":
    data_files.append(("share/gostcryptogui/", ["data/locales/GostCryptoGui-en_US.qm"]))
    data_files.append(("share/caja-python/extensions/", [
                                                            "file-manager/caja/gost-crypto-gui-emblem.py",
                                                            "file-manager/caja/gost-crypto-gui-menu.py"
                                                          ]
                        ))
    data_files.append(("share/locale/en_US/LC_MESSAGES/", ["data/locales/en_US/LC_MESSAGES/gostcryptogui_caja.mo"]))
    data_files.append(("share/locale/ru/LC_MESSAGES/", ["data/locales/ru/LC_MESSAGES/gostcryptogui_caja.mo"]))



setup(
    name='gostcryptogui',
    version='2.1',
    description='A PyQt GUI for performing cryptographic operations over files using GOST algorithms',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://git.red-soft.biz/vladlen.murylyov/gost-crypto-gui',
    author=('Boris Makarenko', 'Vladlen Murylyov'),
    author_email=('bmakarenko90@gmail.com', 'redos.support@red-soft.ru'),
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Users",
        "Topic :: CRYPTO PRO GUI",
        "License :: OSI Approved :: MIT",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="cryptopro, gui",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    data_files=data_files,
    entry_points={
            "console_scripts": [
                "gost-crypto-gui=gostcryptogui:main",
            ],
    },
    project_urls={
            "Source": "http://git.red-soft.biz/vladlen.murylyov/gost-crypto-gui",
            "Bug Reports": "https://support.red-soft.ru/"
    },
)

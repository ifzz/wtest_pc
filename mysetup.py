#!/usr/bin/env python
# -*- coding: gbk -*-

from distutils.core import setup
import py2exe

#Ҫ�������������ļ�
includes = ["pymongo"]

options = {"py2exe":
           {"compressed": 1, #ѹ��
            "optimize": 2, #�Ż�
            "bundle_files": 2, #�����һ��exe      
            "includes": includes,
            "packages": ["pymongo"],
            #"dll_excludes": ["MSVCP90.dll"]
            }}

setup(
    version = "1.0.0",
    description = "wtest",
    name = "wtest",
    options = options,
    zipfile = None, #������library.zip�ļ�
    #console = [{"script": "interface.py", "icon_resources": [(1, "console.ico")]}], #����̨
    windows = [{"script": "interface.py", "icon_resources": [(1, "console.ico")]}], #�������
    data_files = [("", ["console.ico", "sslc.dll", "libeay32.dll"]), ("dictionary", "")], #��������ļ��б�
)
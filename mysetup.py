#!/usr/bin/env python
# -*- coding: gbk -*-

from distutils.core import setup
import py2exe

#要包含的其它库文件
includes = ["pymongo"]

options = {"py2exe":
           {"compressed": 1, #压缩
            "optimize": 2, #优化
            "bundle_files": 2, #打包成一个exe      
            "includes": includes,
            "packages": ["pymongo"],
            #"dll_excludes": ["MSVCP90.dll"]
            }}

setup(
    version = "1.0.0",
    description = "wtest",
    name = "wtest",
    options = options,
    zipfile = None, #不生成library.zip文件
    #console = [{"script": "interface.py", "icon_resources": [(1, "console.ico")]}], #控制台
    windows = [{"script": "interface.py", "icon_resources": [(1, "console.ico")]}], #界面程序
    data_files = [("", ["console.ico", "sslc.dll", "libeay32.dll"]), ("dictionary", "")], #打包拷贝文件列表
)
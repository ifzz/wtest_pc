#!/usr/bin/env python
# -*- coding: gbk -*-

import logging.handlers
import logging
import os.path
import time

def CreateLog(filename):
    # 创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件
    fh = logging.handlers.RotatingFileHandler(filename, mode='a', maxBytes=1024*1024, 
                                              backupCount=99, encoding=None, delay=0)
    fh.setLevel(logging.DEBUG)
    
    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
	
def MakeFuncLog():
    if not os.path.exists('log'):
        os.mkdir('log')
    filename = "log\\func.log"
    return filename

def MakeErrorLog():
    if not os.path.exists('log'):
        os.mkdir('log')    
    filename = "log\\error.log"
    return filename
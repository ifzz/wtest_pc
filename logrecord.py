#!/usr/bin/env python
# -*- coding: gbk -*-

import logging.handlers
import logging
import os.path
import time

def CreateLog(filename):
    # ����һ��logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # ����һ��handler������д����־�ļ�
    fh = logging.handlers.RotatingFileHandler(filename, mode='a', maxBytes=1024*1024, 
                                              backupCount=99, encoding=None, delay=0)
    fh.setLevel(logging.DEBUG)
    
    # �ٴ���һ��handler���������������̨
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # ����handler�������ʽ
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # ��logger���handler
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
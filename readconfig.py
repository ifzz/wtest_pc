#!/usr/bin/python34
#-*-coding:gbk-*-

import configparser


def readserver():
    '''��ȡ�����ļ�����ȡ��������֤���ȯ�����������IP��ַ������˶˿ں�'''
    config = configparser.ConfigParser()
    config.read('config.ini')
    qs_name = config.get('server', 'qs_name')
    server_ip = config.get('server', 'server_ip')
    server_port = config.getint('server', 'server_port')
    return (qs_name, server_ip, server_port)


def readparam():
    '''��ȡί���������'''
    wtparam = configparser.ConfigParser()
    wtparam.read('wtparam.ini')
    wtfunc = wtparam.sections()
    wtdict = dict()
    d = dict()
    
    for wf in wtfunc:
        try:
            for k, v in wtparam.items(wf):
                d[k] = v
            wtdict[wf] = d
            d = dict()
        except configparser.InterpolationSyntaxError as e:
            print("%s���ܺ����ֶ�ֵ��ȡ����" %wf, e)
            #logger.info("���ܺ�%s���ֶ�ֵ��ȡ����%s", wf, e)
    return wtdict
    

if __name__=='__main__':
    #��־��ʼ��
    (qs_name, server_ip, server_port) = readserver()
    print((qs_name, server_ip, server_port))
    wtdict = readparam()


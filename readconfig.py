#!/usr/bin/python34
#-*-coding:gbk-*-

import configparser


def readserver():
    '''读取配置文件，获取服务器的证书的券商名，服务端IP地址，服务端端口号'''
    config = configparser.ConfigParser()
    config.read('config.ini')
    qs_name = config.get('server', 'qs_name')
    server_ip = config.get('server', 'server_ip')
    server_port = config.getint('server', 'server_port')
    return (qs_name, server_ip, server_port)


def readparam():
    '''读取委托请求参数'''
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
            print("%s功能号中字段值读取错误：" %wf, e)
            #logger.info("功能号%s中字段值读取错误：%s", wf, e)
    return wtdict
    

if __name__=='__main__':
    #日志初始化
    (qs_name, server_ip, server_port) = readserver()
    print((qs_name, server_ip, server_port))
    wtdict = readparam()


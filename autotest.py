#!/usr/bin/python35
#-*-coding:gbk-*-

import readconfig
import os
import time
import ctypes
import struct
import sqlite3
import asyncio
import multiprocessing
from xml.dom.minidom import parseString,getDOMImplementation


guid = ''
''' 
    dict_node_list 字段列表
    dict_node_comment_list    字段描述列表
    zd_interpret_dic 字段描述字典
'''
dict_node_list=[]
dict_node_comment_list=[]
zd_interpret_dic={}

'''
    gn_list 功能列表
    gninterpret_list 功能描述列表
    zd_list 字段列表
    gn_interpret_dic 功能描述字典
    gn_zd_dic 功能字段字典
'''
gn_list=[]
gninterpret_list=[]
zd_list=[]
gn_interpret_dic={}
gn_zd_dic={}

'''
    request_gn_list        请求功能列表
    request_gn_interpret_list    请求功描述列表
    request_gn_zd_list        请求功能字段表
    
    answer_gn_list        应答功能列表
    answer_gn_interpret_list   应答功描述列表 
    answer_gn_zd_list            应答功能字段表
    
    request_gn_interpret_dict  请求功能描述字典
    request_gn_zd_dict        请求功能字段字典
    
    answer_gn_interpret_dict    应答功描述字典
    answer_gn_zd_dict        应答功能字段字典
'''
request_gn_list=[]
request_gn_interpret_list=[]
request_gn_zd_list=[]

answer_gn_list=[]
answer_gn_interpret_list=[]
answer_gn_zd_list=[]

request_gn_interpret_dict={}
request_gn_zd_dict={}

answer_gn_interpret_dict={}
answer_gn_zd_dict={}

'''读取配置文件信息'''
(qs_name,server_ip,server_port)=readconfig.readserver()

sslc_dll=ctypes.CDLL('sslc.dll')

'''定义包头结构'''
class CommPackInfo(ctypes.Structure):
    _fields_=[("crc32",ctypes.c_ulong),("compressed",ctypes.c_ubyte),("packtype",ctypes.c_ubyte),("cookie",ctypes.c_ulong),
              ("synid",ctypes.c_ulong),("rawlen",ctypes.c_ulong),("packlen",ctypes.c_ulong),("packdata",ctypes.c_char*0)]
    _pack_=1

'''初始化环境函数'''
wt_init=sslc_dll.DZH_DATA_Init
wt_init.restypes=ctypes.c_int

'''释放环境函数'''
wt_uninit=sslc_dll.DZH_DATA_Uninit
wt_uninit.argtypes=[ctypes.c_int]
wt_uninit.restypes=ctypes.c_void_p

'''处理服务端收过来的数据函数'''
wt_processdata=sslc_dll.DZH_DATA_ProcessServerData
wt_processdata.restypes=ctypes.c_int

'''清理缓冲函数'''
wt_clearbuffer=sslc_dll.DZH_DATA_FreeBuf
wt_clearbuffer.restypes=ctypes.c_void_p

'''获取错误函数'''
wt_getlasterr=sslc_dll.DZH_DATA_GetLastErr
wt_getlasterr.argtypes=[ctypes.c_int]
wt_getlasterr.restypes=ctypes.c_char_p

'''创建发送包函数'''
wt_createpacket=sslc_dll.DZH_DATA_CreatePackage
wt_createpacket.restypes=ctypes.c_int


@asyncio.coroutine
def shakehands(reader, writer):
    global h, p_send_data_buffer, send_len
    '''初始化,A,B协议认证'''   
    send_data_buffer=ctypes.create_string_buffer(b'\x00'*1024*1024)
    p_send_data_buffer=ctypes.pointer(send_data_buffer)
    send_len=ctypes.c_uint()
    c_qs_name=ctypes.c_char_p(qs_name.encode('gbk'))
    h=ctypes.c_int()
    h=wt_init(c_qs_name,ctypes.byref(p_send_data_buffer),ctypes.byref(send_len))
    
    if h==0:
        print("初始化sslc.dll失败")
    if send_len.value!=0:
        writer.write(p_send_data_buffer.contents[:send_len.value])
        yield from writer.drain()
        wt_clearbuffer(h,p_send_data_buffer)
    
    while(True):
        (recv_len,recv_serverdata)=yield from recv_data(reader)
        
        ctypes_recv_serverdata=ctypes.create_string_buffer(recv_serverdata)
        p_recv_serverdata=ctypes.pointer(ctypes_recv_serverdata)
        
        ret=wt_processdata(h,p_recv_serverdata,ctypes.byref(p_send_data_buffer),ctypes.byref(send_len))
        if ret==0:
            pass 
        elif ret==1:
            writer.write(p_send_data_buffer.contents[:send_len.value])
            yield from writer.drain()
            wt_clearbuffer(h,p_send_data_buffer)
            continue
        elif ret==2:
            if not os.path.exists('wtdictory.xml'):
                wtdict_file=open("wtdictory.xml",'w')
                wtdict_file.write(p_send_data_buffer.contents[:send_len.value].decode('GB2312'))
                wt_clearbuffer(h,p_send_data_buffer)
                wtdict_file.close()
            print("握手成功")
            break
        else:
            print("非法或校验通不过等信息")

         
'''接收不定长数据函数'''
@asyncio.coroutine
def recv_data(reader):
    total_len=0
    total_data=b''
    sock_data=b''
    recv_size=8192
    packhead_len=ctypes.sizeof(CommPackInfo)
    packhead_data=CommPackInfo()
    while True:
        sock_data=yield from reader.read(recv_size)
        if not sock_data:
            break
        else:
            total_data+=sock_data
            data_len=len(total_data)
        if data_len>packhead_len:
            tmpdata=struct.unpack("<LBBLLLL",total_data[:packhead_len])
            packhead_data.crc32=tmpdata[0]
            packhead_data.compressed=tmpdata[1]
            packhead_data.packtype=tmpdata[2]
            packhead_data.cookie=tmpdata[3]
            packhead_data.synid=tmpdata[4]
            packhead_data.rawlen=tmpdata[5]
            packhead_data.packlen=tmpdata[6]
            
            if data_len==packhead_len+packhead_data.packlen:
                total_len=data_len
                break
    return total_len,total_data


@asyncio.coroutine
def ABProtocol(loop):
    # Open a connection and write a few lines by using the StreamWriter object
    reader, writer = yield from asyncio.open_connection(server_ip, server_port, loop=loop)
        
    try:
        yield from shakehands(reader, writer)
        # Waiting time
        #yield from asyncio.sleep(5)
        return (reader, writer)
    except ConnectionResetError as e:
        writer.close()
        print(e)

      
@asyncio.coroutine
def ABCLogin():
    pass

@asyncio.coroutine
def CBuySell():
    pass

@asyncio.coroutine
def CInquire():
    pass


def pressure():
    while True:
        loop = asyncio.get_event_loop()
        tasks = [ABProtocol(loop) for i in range(500)]          
        loop.run_until_complete(asyncio.wait(tasks))


def readdict():
    wtdict_comment=open("wtdictory.xml").read().replace("GB2312","UTF-8",1)
    dom=parseString(wtdict_comment)
    root=dom.documentElement
    
    zd=root.getElementsByTagName("字典")
    index_code=root.getElementsByTagName("索引")
    
    for nodes in index_code:
        for node in nodes.childNodes:
            if node.nodeType == node.TEXT_NODE:
                dict_node_list.append(node.data)
    
    index_desc=root.getElementsByTagName("字段说明")        
    for nodes in index_desc :
        for node in nodes.childNodes:
            if node.nodeType == node.TEXT_NODE:
                dict_node_comment_list.append(node.data.strip('\t'))
    
    global zd_interpret_dic 
    zd_interpret_dic=dict(list(zip(dict_node_list,dict_node_comment_list)))

    gn_nodes=root.getElementsByTagName("func")
    for gn_node in gn_nodes:
        gn_list.append(gn_node.getAttribute("id"))
        gninterpret_list.append(gn_node.getAttribute("name").strip('\t'))
        tmp_zds=[]
        for node in gn_node.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                zd=node.childNodes[0].data
                tmp_zds.append(zd)
        zd_list.append(sorted(set(tmp_zds),key=tmp_zds.index))
    global gn_interpret_dic
    global gn_zd_dic   
    gn_interpret_dic=dict(list(zip(gn_list,gninterpret_list)))
    gn_zd_dic=dict(list(zip(gn_list,zd_list)))
    
    for i in gn_list:
        if (gn_interpret_dic[i].find("应答"))<0:
            request_gn_list.append(i)
            request_gn_interpret_list.append(gn_interpret_dic[i])
            request_gn_zd_list.append(gn_zd_dic[i])
        else:
            answer_gn_list.append(i)
            answer_gn_interpret_list.append(gn_interpret_dic[i])
            answer_gn_zd_list.append(gn_zd_dic[i])
            
    global request_gn_interpret_dict,request_gn_zd_dict, answer_gn_interpret_dict,answer_gn_zd_dict
           
    request_gn_interpret_dict=dict(list(zip(request_gn_list,request_gn_interpret_list)))
    request_gn_zd_dict=dict(list(zip(request_gn_list,request_gn_zd_list)))
    
    answer_gn_interpret_dict=dict(list(zip(answer_gn_list,answer_gn_interpret_list)))
    answer_gn_zd_dict=dict(list(zip(answer_gn_list,answer_gn_zd_list)))


def write_requestdbf():
    if os.path.isfile("request.db"):
        return
    request_conn= sqlite3.connect('request.db')
    request_cur= request_conn.cursor()
    
    for i in request_gn_list:
        tempstr=str(i)+request_gn_interpret_dict[i]
        request_cur.execute("create table '%s'(时间 text)"%tempstr)
        for zd in request_gn_zd_dict[i]:
            try:
                tempzdstr=str(zd)+zd_interpret_dic[zd]
                request_cur.execute("alter table '%s' add '%s' text"%(tempstr,tempzdstr))
            except sqlite3.OperationalError as e:
                print("Write request.db sqlite3.OperationalError:", e)
                continue
            except KeyError as e:
                print("Write request.db KeyError:", e)
                tempzdstr=str(zd)+"无描述"
                request_cur.execute("alter table '%s' add '%s' text"%(tempstr,tempzdstr))
                continue        
                 
    request_conn.commit()
    request_cur.close()
    request_conn.close()


def write_answerdbf():
    if os.path.isfile("answer.db"):
        return
    answer_conn= sqlite3.connect('answer.db')
    answer_cur= answer_conn.cursor()
    
    for i in answer_gn_list:
        tempstr=str(i)+answer_gn_interpret_dict[i]
        answer_cur.execute("create table '%s'(时间 text)"%tempstr)
        for zd in answer_gn_zd_dict[i]:
            try:
                tempzdstr=str(zd)+zd_interpret_dic[zd]
                answer_cur.execute("alter table '%s' add '%s' text"%(tempstr,tempzdstr))
            except sqlite3.OperationalError as e:
                print("Write answer.db sqlite3.OperationalError:", e)
                continue
            except KeyError as e:
                print("Write answer.db KeyError:", e)
                tempzdstr=str(zd)+"无描述"
                answer_cur.execute("alter table '%s' add '%s' text"%(tempstr,tempzdstr))
                continue
    answer_cur.execute("create table logerr(时间 text,gn text,err_flag test,err text)")
    answer_conn.commit()
    answer_cur.close()
    answer_conn.close()
    

def write_err_log(err_record):
    answer_conn= sqlite3.connect('answer.db')
    answer_cur= answer_conn.cursor()
    answer_cur.execute("insert into logerr values(?,?,?,?)",err_record) 
    print("收到错误数据")
    answer_conn.commit()
    answer_cur.close()
    answer_conn.close()

   
def write_log(str_time,yd_gn,rec_dict):
    if rec_dict=={}:
        return
    answer_conn= sqlite3.connect('answer.db')
    answer_cur= answer_conn.cursor()
    tablename=str(yd_gn)+answer_gn_interpret_dict[yd_gn]
    
    keys_list=[]
    values_list=[]
    keys_list.append('时间')
    values_list.append(str_time)
    
    for key in list(rec_dict.keys()):
        keys_list.append(key+zd_interpret_dic[key])
        values_list.append(rec_dict[key])
        
    insert_data=("insert into '%s'%s values%s"%(tablename,tuple(keys_list),tuple(values_list)))
    answer_cur.execute(insert_data)
    
    '''
    insert_time=("insert into '%s'(时间 ) values('%s')"%(tablename,str_time))
    answer_cur.execute(insert_time)
    
    for key in rec_dict.keys():
        insert_zd=("update '%s' set '%s'='%s' where 时间='%s'"%(tablename,key+zd_interpret_dic[key],rec_dict[key],str_time)) 
        answer_cur.execute(insert_zd)
    '''
    
    answer_conn.commit()
    answer_cur.close()
    answer_conn.close()
    return
    

def parse_string(data):
    str_time=time.strftime("%Y %m %d %H:%M:%S")
    yd_gn_index_start=data.find('\x0121004=')+len('\x0121004=')
    yd_gn_index_end=data.find("\x01",yd_gn_index_start)
    yd_gn=data[yd_gn_index_start:yd_gn_index_end]
    
    err_find=data.find('\x0121008=')
    
    if err_find>=0:
        err_index_flag_start=err_find+len('\x0121008=')
        err_index_flag_end=data.find("\x01",err_index_flag_start)
        err_flag=data[err_index_flag_start:err_index_flag_end]     
        err_index_msg_start=data.find('\x0121009=')+len('\x0121009=')
        err_index_msg_end=data.find("\x01",err_index_msg_start)
        err_msg=data[err_index_msg_start:err_index_msg_end]
        err_record=(str_time,yd_gn,err_flag,err_msg)
        write_err_log(err_record)
    else:
        global guid
        if (data.find("\x0121010="))>=0:
            guid_index_start=data.find("\x0121010=")+len("\x0121010=")
            guid_index_end=data.find("\x01",guid_index_start)
            guid=data[guid_index_start:guid_index_end]
                    
        records_index_start=data.find("\x0121000=")+len("\x0121000=")
        records_index_end=data.find("\x01",records_index_start)
        records=int(data[records_index_start:records_index_end])
        num=data[data.find("21002=")+6]
        
        for i in range(int(num), int(num)+records):
            yd_index_record_start=data.find("\x0121002=%s\x01"%i)+len("\x0121002=%s\x01"%i)
            yd_index_record_end=data.find("\x0121003=%s"%i)
            yd_record=data[yd_index_record_start:yd_index_record_end]
                   
            rec=yd_record.split("\x01")
            pair_list=[]
            for i in rec:
                pair_list.append(i.split("="))
           
            rec_dict={}
            for i in range(len(pair_list)):
                try:
                    if pair_list[i][0] not in answer_gn_zd_dict[yd_gn]:
                        print(("%s字段没有在应答的%s功能字典中"%(pair_list[i][0]+zd_interpret_dic[pair_list[i][0]],
                                                                yd_gn+answer_gn_interpret_dict[yd_gn])))
                    else:
                        rec_dict.update(dict({pair_list[i][0]:pair_list[i][1]}))
                except KeyError as e:
                    print('Parse string KeyError:', e)
            
            write_log(str_time,yd_gn,rec_dict)
        print("处理成功返回")

 
def unpack_data(h, recv_serverdata):
    ctypes_recv_serverdata=ctypes.create_string_buffer(recv_serverdata)
    p_recv_serverdata=ctypes.pointer(ctypes_recv_serverdata)
    
    unpack_buffer=ctypes.create_string_buffer(b'\000'*1024*1024)
    p_unpack_buffer=ctypes.pointer(unpack_buffer)
    unpack_len=ctypes.c_uint()
    ret=wt_processdata(h,p_recv_serverdata,ctypes.byref(p_unpack_buffer),ctypes.byref(unpack_len))
    if ret==0:
        str_data=p_unpack_buffer.contents[:unpack_len.value].decode('gb2312')
        wt_clearbuffer(h,p_unpack_buffer)
        return str_data
    else:
        print("解包出错！")
        return
        

@asyncio.coroutine
def pack_send_data(reader, writer, data):
    ret=wt_createpacket(h,0,0,ctypes.c_char_p(data.encode('gbk')),len(data.encode('gbk')),
                        ctypes.byref(p_send_data_buffer),ctypes.byref(send_len))
    if ret==-1:
        print("创建数据包失败")
        return
    else:
        writer.write(p_send_data_buffer.contents[:send_len.value])
        yield from writer.drain()
        wt_clearbuffer(h,p_send_data_buffer)
        (recv_len,recv_serverdata)=yield from recv_data(reader)
        return recv_serverdata

    
def singletest(reader, writer, choice):
    global guid
    request_conn= sqlite3.connect('request.db')
    request_cur= request_conn.cursor()
    tablename=choice+request_gn_interpret_dict[choice]
    rows=request_cur.execute("select * from '%s'"%tablename)
    for row in rows:
        request_data=''.join("8=DZH1.0\x0121004=%s\x0121010=%s"%(choice,guid))
        for i in range(len(row)-1):
            if row[i+1]==None:
                request_data=request_data+("\x01%s=%s"%(request_gn_zd_dict[choice][i],''))
            else:
                request_data=request_data+("\x01%s=%s"%(request_gn_zd_dict[choice][i],row[i+1]))
        loop = asyncio.get_event_loop()
        recv_serverdata = loop.run_until_complete(pack_send_data(reader, writer, request_data))
        str_data = unpack_data(h, recv_serverdata)
        parse_string(str_data)      

def autotest(reader, writer):
    for gn in request_gn_list:
        singletest(reader, writer, gn)
    print("全部功能测试完成")
    

def show_sub_menu(reader, writer):  
    while(True):
        while(True):
            try:
                choice=input("请输入功能号:").strip()[:5]
            except(EOFError,KeyboardInterrupt,IndexError):
                choice='88888'
            if choice not in request_gn_list and choice!='88888':
                print("输入的功能号无效，请重新输入：")
            else:
                break
        if choice=='88888':
            return
        else:
            singletest(reader, writer, choice)

    
def showmenu(reader, writer):
    promotd='''
提示：请在输入数据库中填入数据后，选择功能测试：
1:单功能测试
2:自动全功能测试
3:压力测试
4:退出测试
------------------------------------------------------
'''
    while(True):
        while(True):
            try:
                print(("-"*60))
                print(promotd)
                choice=input("请选择：").strip()[0]
            except(EOFError,KeyboardInterrupt,IndexError):
                choice='4'
            if choice not in '1234':
                print("无效的选择，请重新选择：")
            else:
                break
        if choice=='1':
            show_sub_menu(reader, writer)
        elif choice=='2':
            autotest(reader, writer)
        elif choice=='3':
            pressure()
        else:
            break
        

if __name__ == '__main__':
    #建立socket连接和AB握手
    loop = asyncio.get_event_loop()
    reader, writer = loop.run_until_complete(ABProtocol(loop))
    #loop.close()    
    
    readdict()
    write_answerdbf()
    write_requestdbf()
    showmenu(reader, writer)
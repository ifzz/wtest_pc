#!/usr/bin/python34
#-*-coding:gbk-*-


import os
import time
import json
import ctypes
import struct
import dbinit
import socket
import asyncio
import pymongo
import config
import collections
from xml.dom.minidom import parseString,getDOMImplementation


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


class Func():
    def __init__(self, server_ip, server_port, qs_id):
        '''功能处理类'''
        self.server_ip = server_ip
        self.server_port = server_port
        self.qs_id = qs_id
        self.client = pymongo.MongoClient(host='10.15.108.89', port=27017)
        self.guid = ''
        self.h = None
        self.p_send_data_buffer = None
        self.send_len = None
        self.reader = None
        self.writer = None
        self.recv_serverdata = None
        self.recv_len = None
        
        ''' 
            self.dict_node_list 字段列表
            self.dict_node_comment_list    字段描述列表
            self.zd_interpret_dic 字段描述字典
        '''
        self.dict_node_list=[]
        self.dict_node_comment_list=[]
        self.zd_interpret_dic={}
        
        '''
            self.gn_list 功能列表
            self.gninterpret_list 功能描述列表
            self.zd_list 字段列表
            self.gn_interpret_dic 功能描述字典
            self.gn_zd_dic 功能字段字典
        '''
        self.gn_list=[]
        self.gninterpret_list=[]
        self.zd_list=[]
        self.gn_interpret_dic={}
        self.gn_zd_dic={}
        
        '''
            self.request_gn_list        请求功能列表
            self.request_gn_interpret_list    请求功描述列表
            self.request_gn_zd_list        请求功能字段表
            
            self.answer_gn_list        应答功能列表
            self.answer_gn_interpret_list   应答功描述列表 
            self.answer_gn_zd_list            应答功能字段表
            
            self.request_gn_interpret_dict  请求功能描述字典
            self.request_gn_zd_dict        请求功能字段字典
            
            self.answer_gn_interpret_dict    应答功描述字典
            self.answer_gn_zd_dict        应答功能字段字典
        '''
        self.request_gn_list=[]
        self.request_gn_interpret_list=[]
        self.request_gn_zd_list=[]
        
        self.answer_gn_list=[]
        self.answer_gn_interpret_list=[]
        self.answer_gn_zd_list=[]
        
        self.request_gn_interpret_dict={}
        self.request_gn_zd_dict={}
        
        self.answer_gn_interpret_dict={}
        self.answer_gn_zd_dict={}        
        
    @asyncio.coroutine
    def shakehands(self):
        '''初始化,A,B协议认证'''   
        send_data_buffer=ctypes.create_string_buffer(b'\x00'*1024*1024)
        self.p_send_data_buffer=ctypes.pointer(send_data_buffer)
        self.send_len=ctypes.c_uint()
        c_qs_name=ctypes.c_char_p(self.qs_id.encode('gbk'))
        self.h=ctypes.c_int()
        self.h=wt_init(c_qs_name,ctypes.byref(self.p_send_data_buffer),ctypes.byref(self.send_len))
        
        if self.h==0:
            print("初始化sslc.dll失败")
        if self.send_len.value!=0:
            self.writer.write(self.p_send_data_buffer.contents[:self.send_len.value])
            yield from self.writer.drain()
            wt_clearbuffer(self.h,self.p_send_data_buffer)
        
        while(True):
            (self.recv_len,self.recv_serverdata)=yield from self.recv_data()
            
            ctypes_recv_serverdata=ctypes.create_string_buffer(self.recv_serverdata)
            p_recv_serverdata=ctypes.pointer(ctypes_recv_serverdata)
            
            ret=wt_processdata(self.h,p_recv_serverdata,ctypes.byref(self.p_send_data_buffer),ctypes.byref(self.send_len))
            if ret==0:
                pass 
            elif ret==1:
                self.writer.write(self.p_send_data_buffer.contents[:self.send_len.value])
                yield from self.writer.drain()
                wt_clearbuffer(self.h,self.p_send_data_buffer)
                continue
            elif ret==2:
                wtdict_file=open("dictionary\\"+self.qs_id+".xml",'w')
                wtdict_file.write(self.p_send_data_buffer.contents[:self.send_len.value].decode('GB2312'))
                wt_clearbuffer(self.h,self.p_send_data_buffer)
                wtdict_file.close()
                print("握手成功")
                break
            else:
                print("非法或校验通不过等信息")
                break
    
             
    '''接收不定长数据函数'''
    @asyncio.coroutine
    def recv_data(self):
        total_len=0
        total_data=b''
        sock_data=b''
        recv_size=8192
        packhead_len=ctypes.sizeof(CommPackInfo)
        packhead_data=CommPackInfo()
        while True:
            sock_data=yield from self.reader.read(recv_size)
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
    def ABProtocol(self, loop):
        # Open a connection and write a few lines by using the StreamWriter object
        self.reader, self.writer = yield from asyncio.open_connection(self.server_ip, self.server_port, loop=loop)
            
        try:
            yield from self.shakehands()
            # Waiting time
            #yield from asyncio.sleep(5)
        except ConnectionResetError as e:
            self.writer.close()
            print(e)
        
        
    def readdict(self):
        try:
            wtdict_comment=open("dictionary\\"+self.qs_id+".xml").read().replace("GB2312","UTF-8",1)
        except FileNotFoundError:
            return
        dom=parseString(wtdict_comment)
        root=dom.documentElement
            
        zd=root.getElementsByTagName("字典")
        index_code=root.getElementsByTagName("索引")
            
        #for nodes in index_code:
        #    for node in nodes.childNodes:
        #        if node.nodeType == node.TEXT_NODE:
        #            self.dict_node_list.append(node.data)
        self.dict_node_list = [node.data for nodes in index_code for node in nodes.childNodes if node.nodeType == node.TEXT_NODE]
            
        index_desc=root.getElementsByTagName("字段说明")        
        #for nodes in index_desc :
        #    for node in nodes.childNodes:
        #        if node.nodeType == node.TEXT_NODE:
        #            self.dict_node_comment_list.append(node.data.strip('\t'))
        self.dict_node_comment_list = [node.data.strip('\t') for nodes in index_desc for node in nodes.childNodes 
                                  if node.nodeType == node.TEXT_NODE]
               
        self.zd_interpret_dic=collections.OrderedDict(list(zip(self.dict_node_list,self.dict_node_comment_list)))
        
        gn_nodes=root.getElementsByTagName("func")
        for gn_node in gn_nodes:
            self.gn_list.append(gn_node.getAttribute("id"))
            self.gninterpret_list.append(gn_node.getAttribute("name").strip('\t'))
            tmp_zds=[]
            for node in gn_node.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    zd=node.childNodes[0].data
                    tmp_zds.append(zd)
            self.zd_list.append(sorted(set(tmp_zds),key=tmp_zds.index))
                     
        self.gn_interpret_dic=collections.OrderedDict(list(zip(self.gn_list,self.gninterpret_list)))
        self.gn_zd_dic=collections.OrderedDict(list(zip(self.gn_list,self.zd_list)))
        
        self.gn_list.sort()
        for i in self.gn_list:      
            if int(i) % 2 == 0:    
                self.request_gn_list.append(i)
                self.request_gn_interpret_list.append(self.gn_interpret_dic[i])
                self.request_gn_zd_list.append(self.gn_zd_dic[i])
            else:
                self.answer_gn_list.append(i)
                self.answer_gn_interpret_list.append(self.gn_interpret_dic[i])
                self.answer_gn_zd_list.append(self.gn_zd_dic[i])
               
        self.request_gn_interpret_dict=collections.OrderedDict(list(zip(self.request_gn_list,self.request_gn_interpret_list)))
        self.request_gn_zd_dict=collections.OrderedDict(list(zip(self.request_gn_list,self.request_gn_zd_list)))
        
        self.answer_gn_interpret_dict=collections.OrderedDict(list(zip(self.answer_gn_list,self.answer_gn_interpret_list)))
        self.answer_gn_zd_dict=collections.OrderedDict(list(zip(self.answer_gn_list,self.answer_gn_zd_list)))
        
    
    def write_err_log(self, err_record):
        print("收到错误数据")
        try:
            func = err_record['21004'] + self.request_gn_interpret_dict[err_record['21004']]
        except KeyError:
            func = err_record['21004']
        db_commontrade = self.client[self.qs_id+'_应答错误']
        db_commontrade[func].insert_one(err_record)
     
       
    def write_log(self, yd_gn, rec_list):
        print("处理成功返回")
        if rec_list==[]:
            return
        try:
            func = yd_gn + self.answer_gn_interpret_dict[yd_gn]
        except KeyError:
            func = yd_gn 
        db_commontrade = self.client[self.qs_id+'_应答']
        db_commontrade[func].insert_one(rec_list)
        
    
    def parse_string(self, data):
        #str_time=time.strftime("%Y %m %d %self.h:%M:%S")
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
            err_record=collections.OrderedDict({'21004':yd_gn, '21008':err_flag, '21009':err_msg})
            self.write_err_log(err_record)
            return
        else:
            if (data.find("\x0121010="))>=0:
                guid_index_start=data.find("\x0121010=")+len("\x0121010=")
                guid_index_end=data.find("\x01",guid_index_start)
                self.guid=data[guid_index_start:guid_index_end]
                        
            records_index_start=data.find("\x0121000=")+len("\x0121000=")
            records_index_end=data.find("\x01",records_index_start)
            records=int(data[records_index_start:records_index_end])
            num=data[data.find("21002=")+6]
            
            rec_list = []
            for i in range(int(num), int(num)+records):
                rec_dict=collections.OrderedDict()
                if (data.find("\x0121002=%s\x01"%i) == -1) or (data.find("\x0121003=%s"%i) == -1):
                    break
                yd_index_record_start=data.find("\x0121002=%s\x01"%i)+len("\x0121002=%s\x01"%i)
                yd_index_record_end=data.find("\x0121003=%s"%i)
                yd_record=data[yd_index_record_start:yd_index_record_end]
                           
                rec=yd_record.split("\x01")
                pair_list=[]
                for i in rec:
                    pair_list.append(i.split("="))
                   
                
                for i in range(len(pair_list)):
                    try:
                        if pair_list[i][0] not in self.answer_gn_zd_dict[yd_gn]:
                            print(("%s字段没有在应答的%s功能字典中"%(pair_list[i][0]+self.zd_interpret_dic[pair_list[i][0]],
                                                                    yd_gn+self.answer_gn_interpret_dict[yd_gn])))
                        else:
                            rec_dict.update(dict({pair_list[i][0]:pair_list[i][1]}))
                    except KeyError as e:
                        print('Parse string KeyError:', e)
                rec_list.append(rec_dict)
            self.ckeck_result()
            self.write_log(yd_gn, collections.OrderedDict({"列表":rec_list}))
            return rec_list
     
     
    def write_json(self):
        request_fdict=collections.OrderedDict()    #请求全部功能+字段描述字典，具体内容查看wtparam.json
        if not os.path.exists("dictionary"):
            os.mkdir("dictionary")
        js=open("dictionary\\"+self.qs_id+"_请求字典"+".json", mode='w')
        for i in self.request_gn_list:
            function_chinese=str(i)+' '+self.request_gn_interpret_dict[i]
            field_chinese = map(lambda zd:str(zd)+' '+self.zd_interpret_dic[zd], self.request_gn_zd_dict[i])
            request_fdict[function_chinese]=[collections.OrderedDict().fromkeys(field_chinese, '')]
            
        for k1 in request_fdict:
            for num in range(0, len(request_fdict[k1])):
                field_dict = request_fdict[k1][num].keys()
                if "1202 版本号" not in field_dict:
                    request_fdict[k1][num]["1202 版本号"] = ""
                if "6129 客户端细分" not in field_dict:
                    request_fdict[k1][num]["6129 客户端细分"] = ""
                if "6130 UDID" not in field_dict:
                    request_fdict[k1][num]["6130 UDID"] = ""
                if "6131 IMEI" not in field_dict:
                    request_fdict[k1][num]["6131 IMEI"] = ""
            
        js.write(json.dumps(request_fdict, ensure_ascii=False, indent=4))
        js.close()           
        request_fdk = list(request_fdict.keys())   #请求功能号+中文描述 ['11100客户检验', '11908基金委托查询', ...]
    
        answer_fdict=collections.OrderedDict()    #应答全部功能+字段描述字典，具体内容查看wtparam.json
        js=open("dictionary\\"+self.qs_id+"_应答字典"+".json", mode='w')
        for i in self.answer_gn_list:
            try:
                function_chinese=str(i)+' '+self.answer_gn_interpret_dict[i]
                field_chinese = map(lambda zd:str(zd)+' '+self.zd_interpret_dic[zd], self.answer_gn_zd_dict[i])
                answer_fdict[function_chinese]=[collections.OrderedDict().fromkeys(field_chinese, '')]
            except KeyError as e:
                print("{0}：{1} 缺少中文描述".format(function_chinese, e))      
        js.write(json.dumps(answer_fdict, ensure_ascii=False, indent=4))
        js.close()           
        answer_fdk = list(answer_fdict.keys())   #应答功能号+中文描述 ['11100客户检验', '11908基金委托查询', ...]
        
        
    def ckeck_result(self):
        pass
        
        
    def generate_report(self):
        pass
        
         
    def unpack_data(self):
        ctypes_recv_serverdata=ctypes.create_string_buffer(self.recv_serverdata)
        p_recv_serverdata=ctypes.pointer(ctypes_recv_serverdata)
            
        unpack_buffer=ctypes.create_string_buffer(b'\000'*1024*1024)
        p_unpack_buffer=ctypes.pointer(unpack_buffer)
        unpack_len=ctypes.c_uint()
        ret=wt_processdata(self.h,p_recv_serverdata,ctypes.byref(p_unpack_buffer),ctypes.byref(unpack_len))
        if ret==0:
            str_data=p_unpack_buffer.contents[:unpack_len.value].decode('gb2312')
            wt_clearbuffer(self.h,p_unpack_buffer)
            print(str_data)
            return str_data
        else:
            print("解包出错！")
            return
            
    
    @asyncio.coroutine
    def pack_send_data(self, data):
        ret=wt_createpacket(self.h,0,0,ctypes.c_char_p(data.encode('gbk')),len(data.encode('gbk')),
                            ctypes.byref(self.p_send_data_buffer),ctypes.byref(self.send_len))
        if ret==-1:
            print("创建数据包失败")
            return
        else:
            self.writer.write(self.p_send_data_buffer.contents[:self.send_len.value])
            yield from self.writer.drain()
            wt_clearbuffer(self.h,self.p_send_data_buffer)
            (self.recv_len,self.recv_serverdata)=yield from self.recv_data()
            return self.recv_serverdata    
    
        
    def singletest(self, choice):
        db_commontrade = self.client[self.qs_id]
        rows = db_commontrade[choice + self.request_gn_interpret_dict.get(choice)].find()
        
        for row in rows:
            row.pop('_id')
            request_data = ''.join("8=DZH1.0\x0121004=%s\x0121010=%s"%(choice,self.guid))
            for k in row.keys():
                request_data = request_data + '\x01' + k[:4] + '=' + row[k]
            print(request_data)
            loop = asyncio.get_event_loop()
            self.recv_serverdata = loop.run_until_complete(self.pack_send_data(request_data))
            str_data = self.unpack_data()
            self.parse_string(str_data)
       
        
    def autotest(self):
        for gn in dbinit.common:
            self.singletest(gn[:5])
        print("全部功能测试完成")
    

def show_sub_menu(obj):  
    while(True):
        while(True):
            try:
                choice=input("请输入功能号:").strip()[:5]
            except(EOFError,KeyboardInterrupt,IndexError):
                choice='88888'
            if choice not in obj.request_gn_list and choice!='88888':
                print("输入的功能号无效，请重新输入：")
            else:
                break
        if choice=='88888':
            return
        else:
            obj.singletest(choice)

    
def showmenu(obj):
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
                choice='3'
            if choice not in '123':
                print("无效的选择，请重新选择：")
            else:
                break
        if choice=='1':
            show_sub_menu(obj)
        elif choice=='2':
            obj.autotest()
        else:
            break
        

if __name__ == '__main__':
    _, server_ip, server_port, qs_id = config.readbackup()
    func_object = Func(server_ip, server_port, qs_id)
    #建立socket连接和AB握手
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func_object.ABProtocol(loop))
    #loop.close()    
    
    func_object.readdict()
    func_object.write_json()
    showmenu(func_object)
#!/usr/bin/python35
#-*-coding:gbk-*-


import os
import json
import ctypes
import struct
import dbinit
import socket
import config
import pymongo
import collections
import xml.dom.minidom


sslc_dll=ctypes.CDLL('sslc.dll')

'''�����ͷ�ṹ'''
class CommPackInfo(ctypes.Structure):
    _fields_=[("crc32",ctypes.c_ulong),("compressed",ctypes.c_ubyte),("packtype",ctypes.c_ubyte),("cookie",ctypes.c_ulong),
              ("synid",ctypes.c_ulong),("rawlen",ctypes.c_ulong),("packlen",ctypes.c_ulong),("packdata",ctypes.c_char*0)]
    _pack_=1

'''��ʼ����������'''
wt_init=sslc_dll.DZH_DATA_Init
wt_init.restypes=ctypes.c_int

'''�ͷŻ�������'''
wt_uninit=sslc_dll.DZH_DATA_Uninit
wt_uninit.argtypes=[ctypes.c_int]
wt_uninit.restypes=ctypes.c_void_p

'''���������չ��������ݺ���'''
wt_processdata=sslc_dll.DZH_DATA_ProcessServerData
wt_processdata.restypes=ctypes.c_int

'''�����庯��'''
wt_clearbuffer=sslc_dll.DZH_DATA_FreeBuf
wt_clearbuffer.restypes=ctypes.c_void_p

'''��ȡ������'''
wt_getlasterr=sslc_dll.DZH_DATA_GetLastErr
wt_getlasterr.argtypes=[ctypes.c_int]
wt_getlasterr.restypes=ctypes.c_char_p

'''�������Ͱ�����'''
wt_createpacket=sslc_dll.DZH_DATA_CreatePackage
wt_createpacket.restypes=ctypes.c_int


class Func:
    def __init__(self, mongo_object, server_ip, server_port, qs_id):
        '''���ܴ�����'''
        self.mongo_object = mongo_object
        self.server_ip = server_ip
        self.server_port = server_port
        self.qs_id = qs_id
        self.guid = ''
        self.h = None
        self.p_send_data_buffer = None
        self.send_len = None
        self.reader = None
        self.writer = None
        self.recv_serverdata = None
        self.recv_len = None
        
        ''' 
            self.dict_node_list �ֶ��б�
            self.dict_node_comment_list    �ֶ������б�
            self.zd_interpret_dic �ֶ������ֵ�
        '''
        self.dict_node_list=[]
        self.dict_node_comment_list=[]
        self.zd_interpret_dic={}
        
        '''
            self.gn_list �����б�
            self.gninterpret_list ���������б�
            self.zd_list �ֶ��б�
            self.gn_interpret_dic ���������ֵ�
            self.gn_zd_dic �����ֶ��ֵ�
        '''
        self.gn_list=[]
        self.gninterpret_list=[]
        self.zd_list=[]
        self.gn_interpret_dic={}
        self.gn_zd_dic={}
        
        '''
            self.request_gn_list        �������б�
            self.request_gn_interpret_list    ���������б�
            self.request_gn_zd_list        �������ֶα�
            
            self.answer_gn_list        Ӧ�����б�
            self.answer_gn_interpret_list   Ӧ�������б� 
            self.answer_gn_zd_list            Ӧ�����ֶα�
            
            self.request_gn_interpret_dict  �����������ֵ�
            self.request_gn_zd_dict        �������ֶ��ֵ�
            
            self.answer_gn_interpret_dict    Ӧ�������ֵ�
            self.answer_gn_zd_dict        Ӧ�����ֶ��ֵ�
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
        
        
    def create_sokect(self, second):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, int(self.server_port)))
        if second > 0:
            self.client_socket.settimeout(second)
        else:
            print('Use the default timeout -1.')
        return self.shakehands()
        
    def shakehands(self):
        '''��ʼ��,A,BЭ����֤'''
        send_data_buffer=ctypes.create_string_buffer(b'\x00'*1024*1024)
        self.p_send_data_buffer=ctypes.pointer(send_data_buffer)
        self.send_len=ctypes.c_uint()
        c_qs_name=ctypes.c_char_p(self.qs_id.encode('gbk'))
        self.h=ctypes.c_int()
        self.h=wt_init(c_qs_name,ctypes.byref(self.p_send_data_buffer),ctypes.byref(self.send_len))
        
        if self.h==0:
            print("��ʼ��sslc.dllʧ��")
        if self.send_len.value!=0:
            self.client_socket.send(self.p_send_data_buffer.contents[:self.send_len.value])
            wt_clearbuffer(self.h,self.p_send_data_buffer)
        
        while(True):
            (self.recv_len,self.recv_serverdata)=self.recv_data()
            
            ctypes_recv_serverdata=ctypes.create_string_buffer(self.recv_serverdata)
            p_recv_serverdata=ctypes.pointer(ctypes_recv_serverdata)
            
            ret=wt_processdata(self.h,p_recv_serverdata,ctypes.byref(self.p_send_data_buffer),ctypes.byref(self.send_len))
            if ret==0:
                pass 
            elif ret==1:
                self.client_socket.send(self.p_send_data_buffer.contents[:self.send_len.value])
                wt_clearbuffer(self.h,self.p_send_data_buffer)
                continue
            elif ret==2:
                with open("dictionary\\"+self.qs_id+".xml", 'w') as wtdict_file:
                    wtdict_file.write(self.p_send_data_buffer.contents[:self.send_len.value].decode('GB2312'))
                wt_clearbuffer(self.h,self.p_send_data_buffer)
                return True
            else:
                return False
    
             
    '''���ղ��������ݺ���'''
    def recv_data(self):
        total_len=0
        total_data=b''
        sock_data=b''
        recv_size=8192
        packhead_len=ctypes.sizeof(CommPackInfo)
        packhead_data=CommPackInfo()
        while True:
            sock_data=self.client_socket.recv(recv_size)
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
        
        
    def readdict(self):
        try:
            fxml = open("dictionary\\"+self.qs_id+".xml", 'r')
            wtdict_comment=fxml.read().replace("GB2312","UTF-8",1)
        except FileNotFoundError:
            return
        else:
            fxml.close()
            
        dom=xml.dom.minidom.parseString(wtdict_comment)
        root=dom.documentElement
            
        index_code=root.getElementsByTagName("����")
        self.dict_node_list = [node.data for nodes in index_code for node in nodes.childNodes 
                               if node.nodeType == node.TEXT_NODE]
            
        index_desc=root.getElementsByTagName("�ֶ�˵��")        
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
        print("�յ���������")
        try:
            func = err_record['21004'] + ' ' + self.request_gn_interpret_dict[err_record['21004']]
        except KeyError:
            func = err_record['21004']
        db_commontrade = self.mongo_object.client[self.qs_id+'Ӧ��_����']
        db_commontrade[func].insert_one(err_record)
     
       
    def write_log(self, yd_gn, rec_list):
        print("����ɹ�����")
        if rec_list==[]:
            return
        try:
            func = yd_gn + ' ' + self.answer_gn_interpret_dict[yd_gn]
        except KeyError:
            func = yd_gn 
        db_commontrade = self.mongo_object.client[self.qs_id+'Ӧ��']
        db_commontrade[func].insert_one(rec_list)
        
    
    def parse_string(self, data):
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
                            print(("%s�ֶ�û����Ӧ���%s�����ֵ���"%(pair_list[i][0]+self.zd_interpret_dic[pair_list[i][0]],
                                                                    yd_gn+self.answer_gn_interpret_dict[yd_gn])))
                        else:
                            rec_dict.update(dict({pair_list[i][0]:pair_list[i][1]}))
                    except KeyError as e:
                        print('Parse string KeyError:', e)
                rec_list.append(rec_dict)
            self.ckeck_result()
            self.write_log(yd_gn, collections.OrderedDict({"array":rec_list}))
            return rec_list
     
     
    def write_json(self):
        request_fdict=collections.OrderedDict()    #����ȫ������+�ֶ������ֵ䣬�������ݲ鿴wtparam.json
        if not os.path.exists("dictionary"):
            os.mkdir("dictionary")

        for i in self.request_gn_list:
            function_chinese=str(i)+' '+self.request_gn_interpret_dict[i]
            field_chinese = map(lambda zd:str(zd)+' '+self.zd_interpret_dic[zd], self.request_gn_zd_dict[i])
            request_fdict[function_chinese]=[collections.OrderedDict().fromkeys(field_chinese, '')]
            
        for k1 in request_fdict:
            for num in range(0, len(request_fdict[k1])):
                field_dict = request_fdict[k1][num].keys()
                if "1202 �汾��" not in field_dict:
                    request_fdict[k1][num]["1202 �汾��"] = ""
                if "6130 UDID" not in field_dict:
                    request_fdict[k1][num]["6130 UDID"] = ""
                if "6131 IMEI" not in field_dict:
                    request_fdict[k1][num]["6131 IMEI"] = ""
                    
        with open("dictionary\\"+self.qs_id+"_�����ֵ�.json", mode='w', encoding='utf�\8') as js:        
            json.dump(request_fdict, js, ensure_ascii=False, indent=4)
            
        request_fdk = list(request_fdict.keys())   #�����ܺ�+�������� ['11100�ͻ�����', '11908����ί�в�ѯ', ...]   
        answer_fdict=collections.OrderedDict()    #Ӧ��ȫ������+�ֶ������ֵ䣬�������ݲ鿴wtparam.json

        for i in self.answer_gn_list:
            try:
                function_chinese=str(i)+' '+self.answer_gn_interpret_dict[i]
                field_chinese = map(lambda zd:str(zd)+' '+self.zd_interpret_dic[zd], self.answer_gn_zd_dict[i])
                answer_fdict[function_chinese]=[collections.OrderedDict().fromkeys(field_chinese, '')]
            except KeyError as e:
                print("{0}��{1} ȱ����������".format(function_chinese, e))
                
        with open("dictionary\\"+self.qs_id+"_Ӧ���ֵ�.json", mode='w', encoding='utf�\8') as js:
            json.dump(answer_fdict, js, ensure_ascii=False, indent=4)
       
        answer_fdk = list(answer_fdict.keys())   #Ӧ���ܺ�+�������� ['11100�ͻ�����', '11908����ί�в�ѯ', ...]
        
        
    def ckeck_result(self):
        pass
        
         
    def unpack_data(self):
        ctypes_recv_serverdata=ctypes.create_string_buffer(self.recv_serverdata)
        p_recv_serverdata=ctypes.pointer(ctypes_recv_serverdata)
            
        unpack_buffer=ctypes.create_string_buffer(b'\000'*1024*1024)
        p_unpack_buffer=ctypes.pointer(unpack_buffer)
        unpack_len=ctypes.c_uint()
        ret=wt_processdata(self.h,p_recv_serverdata,ctypes.byref(p_unpack_buffer),ctypes.byref(unpack_len))
        if ret==0:
            str_data=p_unpack_buffer.contents[:unpack_len.value].decode('gbk')
            wt_clearbuffer(self.h,p_unpack_buffer)
            print(str_data)
            return str_data
        else:
            print("�������")
            return
            
    
    def pack_send_data(self, data):
        ret=wt_createpacket(self.h,0,0,ctypes.c_char_p(data.encode('gbk')),len(data.encode('gbk')),
                            ctypes.byref(self.p_send_data_buffer),ctypes.byref(self.send_len))
        if ret==-1:
            print("�������ݰ�ʧ��")
            return
        else:
            self.client_socket.send(self.p_send_data_buffer.contents[:self.send_len.value])
            wt_clearbuffer(self.h,self.p_send_data_buffer)
            (self.recv_len,self.recv_serverdata)=self.recv_data()
            return self.recv_serverdata    
    
        
    def singletest(self, choice):
        db_commontrade = self.mongo_object.client[self.qs_id]
        rows = db_commontrade[choice + ' ' + self.request_gn_interpret_dict.get(choice)].find()
        
        for row in rows:          
            request_data = ''.join("8=DZH1.0\x0121004=%s\x0121010=%s"%(choice,self.guid))
            for d in row['array']:
                t = list(d.items())[0]
                request_data += '\x01' + t[0][:4] + '=' + t[1]
            print(request_data)
            self.recv_serverdata = self.pack_send_data(request_data)
            str_data = self.unpack_data()
            self.parse_string(str_data)
       
        
    def autotest(self):
        self.mongo_object.db_init()
        for document in self.mongo_object.case:
            self.singletest(document['_id'][:5])
        print("ȫ�����ܲ������")
    

def show_sub_menu(obj):  
    while(True):
        while(True):
            try:
                choice=input("�����빦�ܺ�:").strip()[:5]
            except(EOFError,KeyboardInterrupt,IndexError):
                choice='88888'
            if choice not in obj.request_gn_list and choice!='88888':
                print("����Ĺ��ܺ���Ч�����������룺")
            else:
                break
        if choice=='88888':
            return
        else:
            obj.singletest(choice)

    
def showmenu(obj):
    promotd='''
��ʾ�������������ݿ����������ݺ�ѡ���ܲ��ԣ�
1:�����ܲ���
2:�Զ�������
3:�˳�����
------------------------------------------------------
'''
    while(True):
        while(True):
            try:
                print(("-"*60))
                print(promotd)
                choice=input("��ѡ��").strip()[0]
            except(EOFError,KeyboardInterrupt,IndexError):
                choice='3'
            if choice not in '123':
                print("��Ч��ѡ��������ѡ��")
            else:
                break
        if choice=='1':
            show_sub_menu(obj)
        elif choice=='2':
            obj.autotest()
        else:
            break
        

if __name__ == '__main__':
    current_scheme, server_ip, server_port, qs_id = config.readbackup()
    mongo_object = dbinit.Mongo(current_scheme)
    func_object = Func(mongo_object, server_ip, server_port, qs_id)
    
    #����socket���Ӻ�AB����
    stauts = func_object.create_sokect(10)
    if stauts:
        print('����������ֳɹ�')
        func_object.readdict()
        func_object.write_json()
        showmenu(func_object)
    else:
        print("�Ƿ���У��ͨ��������Ϣ")
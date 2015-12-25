#!/usr/bin/python34
#-*-coding:gbk-*-

import os
import json
import config
import pymongo
import autotest
import collections


common = ['11100�ͻ�У��',
          '11154�ɶ���ѯ',
          '11102��ѯ����',
          '11104�ʽ����',
          '11146�ɷݲ�ѯ',
          '11106�޸�����',
          '11108�޸��ʽ�����',
          '11130��ѯ������Ϣ',
          '11126�������',
          '11122��֤ת��',
          '11124������ˮ',
          '11110���������',
          '11132�ɳ�����ѯ',
          '11116��ͨ��Ʊί��',
          '12014�м�ί��',
          '11114ί�г���',
          '11134����ί�в�ѯ',
          '11136��ʷί�в�ѯ',
          '11140���ճɽ���ѯ',
          '11142��ʷ�ɽ���ѯ',
          '11150�ʽ���ˮ',
          '11152���',
          '12052�ͻ����ϲ�ѯ',
          '11900����ʽ����ί��',
          '11902����ί�г���',
          '11904����ת��',
          '11906����ݶ��ѯ',
          '11908����ί�в�ѯ',
          '11910���������Ϣ��ѯ',
          '11912����ɽ���ѯ',
          '11914����ֺ�',
          '11916��������',
          '11918�����ʽ��ʺſ���',
          '11924��ѯ����˾����',
          '11926��ѯ�����ʺ�',
          '12184�ʵ�������',
          '12186�ʵ����ύ',
          '12282�ʵ�����Ϣ']

credit = []


class Mongo:
    def __init__(self, current_scheme):
        self.current_scheme = current_scheme
        self.client = pymongo.MongoClient(host='10.15.108.89', port=27017)
        self.db = self.client[self.current_scheme]        
    
    def common_init(self):
        js = open("dictionary\\" + self.current_scheme + "_�����ֵ�" + ".json", mode='r')
        request_fdict = json.loads(js.read(), object_pairs_hook=collections.OrderedDict)
        js.close()
        
        common_matchdict = collections.OrderedDict()
        for k in common:
            common_matchdict[k] = request_fdict.get(k)  
    
        js = open("dictionary\\" + self.current_scheme + ".json", mode='w')
        js.write(json.dumps(common_matchdict, ensure_ascii=False, indent=4))
        js.close()
            
    
    def mongodb_init(self):
        js = open("dictionary\\" + self.current_scheme + '_' + "��ʼ��" + ".json", mode='r')
        common_fdict = json.loads(js.read(), object_pairs_hook=collections.OrderedDict)
        js.close()
        
        for i in common:
            self.db[i].insert_many(common_fdict[i])
    
        
    def db_init(self):
        for collection in self.db.collection_names():
            print(self.db[collection].find({"_id":"1"}))
            
        
    def db_add(self):
        pass
    
    
    def db_del(self):
        pass


if __name__ == '__main__':
    mongo_object = Mongo('����֤ȯ')
    #mongo_object.mongodb_init()
    mongo_object.db_init()

#!/usr/bin/python34
#-*-coding:gbk-*-

import os
import json
import config
import pymongo
import autotest
import collections


common = ['11100客户校验',
          '11154股东查询',
          '11102查询行情',
          '11104资金余额',
          '11146股份查询',
          '11106修改密码',
          '11108修改资金密码',
          '11130查询银行信息',
          '11126银行余额',
          '11122银证转帐',
          '11124银行流水',
          '11110计算可买数',
          '11132可撤单查询',
          '11116普通股票委托',
          '12014市价委托',
          '11114委托撤单',
          '11134当日委托查询',
          '11136历史委托查询',
          '11140当日成交查询',
          '11142历史成交查询',
          '11150资金流水',
          '11152交割单',
          '12052客户资料查询',
          '11900开放式基金委托',
          '11902基金委托撤单',
          '11904基金转换',
          '11906基金份额查询',
          '11908基金委托查询',
          '11910基金相关信息查询',
          '11912基金成交查询',
          '11914基金分红',
          '11916查基金代码',
          '11918基金资金帐号开户',
          '11924查询基金公司代码',
          '11926查询基金帐号',
          '12184适当性试题',
          '12186适当性提交',
          '12282适当性信息']

credit = []


class Mongo:
    def __init__(self, current_scheme):
        self.current_scheme = current_scheme
        self.client = pymongo.MongoClient(host='10.15.108.89', port=27017)
        if self.current_scheme == '':
            self.db = self.client['未初始化券商']
        else:
            self.db = self.client[self.current_scheme]
        self.case = []
    
    def common_init(self):
        js = open("dictionary\\" + self.current_scheme + "_请求字典" + ".json", mode='r')
        request_fdict = json.loads(js.read(), object_pairs_hook=collections.OrderedDict)
        js.close()
        
        common_matchdict = collections.OrderedDict()
        for k in common:
            common_matchdict[k] = request_fdict.get(k)  
    
        js = open("dictionary\\" + self.current_scheme + ".json", mode='w')
        js.write(json.dumps(common_matchdict, ensure_ascii=False, indent=4))
        js.close()
            
    
    def mongodb_init(self):
        js = open("dictionary\\" + self.current_scheme + '_' + "初始化" + ".json", mode='r')
        common_fdict = json.loads(js.read(), object_pairs_hook=collections.OrderedDict)
        js.close()
        
        for i in common:
            self.db[i].insert_many(common_fdict[i])
    
        
    def db_init(self):
        collections = self.db.collection_names()
        if 'system.indexes' in collections:
            collections.remove('system.indexes')
            
        for collection in collections:
            self.case += list(self.db[collection].find())
            
            
    def db_find(self, collection, _id):
        return list(self.db[collection].find({'_id': _id}))[0]
            
        
    def db_add(self, collection, _id, document):
        self.db[collection].find_one_and_update({'_id': _id},
                                                {'$set': document},
                                                upsert=True)
    
    
    def db_del(self, collection, _id):
        self.db[collection].remove({"_id": _id})


if __name__ == '__main__':
    mongo_object = Mongo('华信证券')
    #mongo_object.mongodb_init()
    mongo_object.db_init()

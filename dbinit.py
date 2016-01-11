#!/usr/bin/python34
#-*-coding:gbk-*-

import json
import pymongo
import collections


class Mongo:
    def __init__(self, current_scheme):
        self.current_scheme = current_scheme
        self.client = pymongo.MongoClient(host='10.15.108.89', port=27017)
        if self.current_scheme == '':
            self.db = self.client['未初始化券商']
        else:
            self.db = self.client[self.current_scheme]
        self.case = []
    
        
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


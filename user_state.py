#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 20:10:16 2019

@author: toocool
"""

from pymongo import MongoClient
import urllib.parse
import datetime

#資料庫連接

# =============================================================================
# =============================================================================
# =============================================================================
# name_id='陳泰良'
# u_id='U1a447107797cfe0a2e2c8443df084569'
# u_state='command'
# # =============================================================================
# =============================================================================
# =============================================================================

def write(name_id, u_id, u_state): 
    client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client['UserStateDB']
    coll = db[u_id]
    
    user_data=list(coll.find())
    if len(user_data)==0 :
        coll.insert({'nameid': name_id,
                  'uid': u_id,
                  'state':u_state,
                  'date_info': datetime.datetime.utcnow()
                  })
    else:
        coll.delete_many({'uid': u_id})
        coll.insert({'nameid': name_id,
                  'uid': u_id,
                  'state':u_state,
                  'date_info': datetime.datetime.utcnow()
                  })
        
                  
    
#----------------------------儲存使用者的股票--------------------------
def read(u_id): 
    
    client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client['UserStateDB']
    coll = db[u_id]
    user_data=list(coll.find())
    
    if len(user_data)==0 :
        S1='no user state!'
        return(S1)
    else:
        S2=user_data[0]['state']
        return(S2)
    
    

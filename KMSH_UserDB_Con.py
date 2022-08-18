#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2019-07-07

@author: toocool chen
"""
from linebot.models import *
from pymongo import MongoClient
#import urllib.parse
import datetime


#uid='U1a447107797cfe0a2e2c8443df084569'
#lang='日'
#lang='中'
#nameid='toocool'
###############################################################################
#                           LineBot股票機器人mongoDB#                            #
###############################################################################
# 要讀取授權的Authentication Database認證資料庫
Authdb='Med-Bot'
sitdb='Taiwan_hospital_data'
#資料庫連接函式

client = MongoClient('mongodb+srv://toocoolchen:migo2000@cluster0.hywy3.mongodb.net/?retryWrites=true&w=majority')
#client = MongoClient("mongodb://stockrobot:tp6w94xu;6@cluster1-shard-00-00.yujl6.gcp.mongodb.net:27017,cluster1-shard-00-01.yujl6.gcp.mongodb.net:27017,cluster1-shard-00-02.yujl6.gcp.mongodb.net:27017/KMSH-bot?ssl=true&replicaSet=atlas-y6ihm4-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client[Authdb]
hs_DB = client[sitdb]
client.close()

#----------------------------判斷使用者使否為新使用者--------------------------
def find_user(uid):
    collect = db['lineuser']
    cel=list(collect.find())
    
    ans=False
    for i in cel:
        if uid == i['uid']:
            ans = True
    return ans

#-----------------------儲存使用者line uid 與 line 暱稱與此設使用者初始狀態------
def write_user(nameid, uid):  
    collect = db['lineuser']
    collect.insert_one({'nameid': nameid,
                    'uid': uid,
                    'tr_mode':'N',
                    'lang':'中',
                    's1':'',
                    's2':'',
                    's3':'',
                    'trans_func':'N',
                    'my_hospital': [],
                    'date_info': datetime.datetime.utcnow()
                    })
    
#--------------------------設為中文翻譯外語狀態---------------------------------
def set_trmode(uid,lang):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
    
    #uid='泰良'
    #test_dic={ 'uid':'7777',
    #          'nameid':'toocool'
    #          }
    #collect.insert_one(test_dic)
    
    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid':uid},{'$set':{'tr_mode':'Y','lang':lang}})
            
    return ans  
#-----------------------------設為外語翻譯中文狀態-------------------------------------
def set_trmode_r(uid,lang):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
        
    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid':uid},{'$set':{'tr_mode':'R','lang':lang}})
            
    return ans 
#------------------------------設為進入診斷推薦狀態---------------------------------
def set_trmode_d(uid,lang):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
        
    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid':uid},{'$set':{'tr_mode':'D','lang':lang,'s1':'','s2':'','s3':''}})            
    return ans

# -----------------------------設為導航狀態---------------------------------
def set_trmode_m(uid, lang):
    collect = db['lineuser']
    cel = list(collect.find())
    ans = True

    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid': uid}, {'$set': {'tr_mode': 'M', 'lang': lang}})

    return ans

#-----------------------------設為一般狀態---------------------------------
def dis_trmode(uid,lang):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
    
    for i in cel:
        if uid == i['uid']:
             collect.update_one({'uid':uid},{'$set':{'tr_mode':'N','lang':lang}})
            
    return ans

#------------------------------取得此用者狀態--------------------------------
def get_trmode(uid):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=''
    
    for i in cel:
        if i['uid'] == uid:            
             ans=i['tr_mode'] 
             lang=i['lang']
             trans_func=i['trans_func']             
    return ans,lang,trans_func
#------------------------------設定使用者s1症狀--------------------------------
def set_s1(uid,s1):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
        
    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid':uid},{'$set':{'s1':s1}})            
    return ans 
#------------------------------設定使用者s2症狀--------------------------------
def set_s2(uid,s2):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
        
    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid':uid},{'$set':{'s2':s2}})            
    return ans
#------------------------------設定使用者s3症狀--------------------------------
def set_s3(uid,s3):  
    collect = db['lineuser']
    cel=list(collect.find())
    ans=True
        
    for i in cel:
        if uid == i['uid']:
            collect.update_one({'uid':uid},{'$set':{'s3':s3}})            
    return ans

#------------------------------醫院資料庫--------------------------------
def District_hp_db(): #地區
    cellection = hs_DB['District_hp']
    return cellection

def Regional_hp_db(): #區域
    cellection = hs_DB['Regional_hp']
    return cellection

def clinic_hp_db(): #診所
    cellection = hs_DB['clinic_hp']
    return cellection

def medicine_hp_db(): #醫學中心
    cellection = hs_DB['medicine_hp']
    return cellection
    # for i in cellection.find():
    #   print(i['地 址 '])

def pharmacy_hp_db(): #藥局
    cellection = hs_DB['pharmacy_hp']
    return cellection

#========================================
#透過user_Id取得使用者資料物件
#========================================
def get_user_data(user_Id):
    cellection = db['lineuser']
    return cellection.find_one({'uid': user_Id})

#========================================
#新增我的醫院(用arry的方式)
#========================================
def add_my_Hospital(user_Id,hs_Name,current_db_type):
    cellection = db['lineuser']
    origin_data = get_user_data(user_Id)
    my_hospital = origin_data["my_hospital"]

    for item in my_hospital:
        if hs_Name in item["name"]:
            message = TextSendMessage(text="已有此筆醫院")
            return message

    if hs_Name not in my_hospital and len(my_hospital) <5 :
        my_hospital.append({
            "name": hs_Name,
            "db": current_db_type
        })
        cellection.find_one_and_update(
            {'uid':user_Id},
            {"$set":
                {"my_hospital": my_hospital}
            }, upsert=True
        )
        message = TextSendMessage(text="加入成功")
        return message

    else:
        message = TextSendMessage(text="已達儲存上限五筆")
        return message

#========================================
#讀取我的醫院
#user_Id 帶入 get_data 函式取得使用者資料
#my_hospital:使用者醫院陣列中的資料
#hs_DB[i["db"]:透過迴圈取得使用者db名稱對應醫院的db名稱 ex i["db"] = District_hp
#obj: 透過使用者醫院名稱對應醫院資料(字典)
#obj.update 在字典後加入使用者資料庫，之後帶入reply_Hospital做判斷db用
#========================================
def read_my_Hospital(user_Id):
    def get_hsData(i):
        cellection = hs_DB[i["db"].split("_db")[0]]
        obj = cellection.find_one({"醫事機構名稱": i["name"]})
        obj.update({"db_type": i["db"]})
        return obj
    origin_data = get_user_data(user_Id)
    my_hospital = origin_data["my_hospital"]
    result_arr = []
    for i in my_hospital:
        result_arr.append(get_hsData(i))
    return result_arr

#========================================
#刪除我的醫院
#user_Id 帶入 get_data 函式取得使用者資料
#my_hospital:使用者醫院陣列中的資料
#使用 python 迴圈字典方法 enumerate 讀取要刪除的醫院名稱在字典中的位置
#find_one_and_update : 為 mongo api ，找到指定名稱後修改值
#========================================
def del_my_Hospital(user_Id,hs_Name):
    cellection = db['lineuser']
    origin_data = get_user_data(user_Id)
    my_hospital = origin_data["my_hospital"]

    for idx_i, val_i in enumerate(my_hospital):
        if val_i["name"] == hs_Name:
            del my_hospital[idx_i]

    cellection.find_one_and_update(
        {'uid': user_Id},
        {"$set":
             {"my_hospital": my_hospital}
         }, upsert=True
    )
    message = TextSendMessage(text="移除成功")
    return message
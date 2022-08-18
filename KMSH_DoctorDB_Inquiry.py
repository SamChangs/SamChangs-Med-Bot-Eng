# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 13:31:39 2019

@author: toocool chen
"""
from pymongo import MongoClient
#doc_name='郭昭宏'
client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')

def response(doc_name):
    
    doctor_info=[]        
    Authdb='KMSH-bot'
    db = client[Authdb]
    collid='DoctorInfo'
    coll = db[collid]    
    doctor_query = list(coll.find({'c_name':doc_name}))
        
    if len(doctor_query)> 0 :                    
        doctor_info =  doctor_query
    
    return doctor_info

def intro(doc_name):
    
    doctor_info=[]    
    Authdb='KMSH-bot'
    db = client[Authdb]
    collid='DoctorIntro'
    coll = db[collid]    
    doctor_query = list(coll.find({'c_name':doc_name}))
        
    if len(doctor_query)> 0 :                    
        doctor_info =  doctor_query
    
    return doctor_info    
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 09:07:58 2020

@author: toocool
"""

import requests
import json

def ans(origal_url):    
    #origal_url="https://www.kmsh.org.tw/online/HPRREG.asp?txtRegDate=2020/09/18&txtNoon=1&txtDeptNo=0109&txtDocNo=890080&txtT=400&txtDocName=陳煌麒&txtDeptName=胸腔內科"
    data ={ "url" : origal_url }
    data_json = json.dumps(data)
    headers = {'Content-type': 'application/json', 'reurl-api-key': '4070ff49d794e331145e3b663c974755ecd3b738939f04df8a38b58d65165567c4f5d6'}
    
    response = requests.post('https://api.reurl.cc/shorten', data=data_json, headers=headers)
    if response.status_code == 200:       
        response_dic = response.json()
        short_url=response_dic['short_url'] 
    else:   
        short_url=''        
    return(short_url)


# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 19:13:05 2020

@author: toocool
"""
import requests, uuid

subscription_key ='f00b47cb4fae401aafb146a4b06945c9'
endpoint = 'https://api.cognitive.microsofttranslator.com'
path = '/translate?api-version=3.0'

#英語
def en(trans_message):
        
    params = '&to=en'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#日本
def ja(trans_message):
    
    params = '&to=ja'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
        
    return(tran_text)

#越南    
def vi(trans_message):
    
    params = '&to=vi'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]   
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#印尼
def id(trans_message):
        
    params = '&to=id'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#泰文
def th(trans_message):
    
    params = '&to=th'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#韓文
def ko(trans_message):
    
    params = '&to=ko'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#法文
def fr(trans_message):
    
    params = '&to=fr'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#德文
def de(trans_message):
    
    params = '&to=de'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#西班牙語
def es(trans_message):
     
    params = '&to=es'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)


def ZhHant(trans_message):
       
    params = '&to=zh-Hant'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#印度官方
def hi(trans_message):
    
    params = '&to=hi'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#菲律賓
def fil(trans_message):
    

    params = '&to=fil'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

# 馬來文
def ms(trans_message):
    
    params = '&to=ms'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

# 沙烏地阿拉伯
def ar(trans_message):
    

    params = '&to=ar'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#義大利
def it(trans_message):
    
    params = '&to=it'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)    
#俄羅斯
def ru(trans_message):
    
    params = '&to=ru'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#波蘭
def pl(trans_message):
    
    params = '&to=pl'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#葡萄牙
def pt(trans_message):
    
    params = '&to=pt-pt'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#荷蘭
def nl(trans_message):
    
    params = '&to=nl'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#瑞典
def sv(trans_message):
    
    params = '&to=sv'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#捷克
def cs(trans_message):    
    params = '&to=cs'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#孟加拉語
def bn(trans_message):    
    params = '&to=bn'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#希臘
def el(trans_message):    
    params = '&to=el'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#愛爾蘭
def ga(trans_message):    
    params = '&to=ga'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 
#挪威
def nb(trans_message):    
    params = '&to=nb'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#土耳其
def tr(trans_message):    
    params = '&to=tr'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 

#烏克蘭
def uk(trans_message):    
    params = '&to=uk'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text) 

#匈牙利
def hu(trans_message):    
    params = '&to=hu'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#海地
def ht(trans_message):    
    params = '&to=ht'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#芬蘭
def fi(trans_message):    
    params = '&to=fi'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#丹麥
def da(trans_message):    
    params = '&to=da'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#波斯語(伊朗)
def fa(trans_message):    
    params = '&to=fa'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)

#羅馬尼亞
def ro(trans_message):    
    params = '&to=ro'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#希伯來
def he(trans_message):    
    params = '&to=he'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
#巴西
def br(trans_message):    
    params = '&to=pt-br'
    constructed_url = endpoint + path + params    
    headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'eastasia',
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
        }
    body=[{
        'text':trans_message
        }]    
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    #type(response)
    tran_reponse=response[0]
    tran_info=tran_reponse['translations'][0]
    tran_text=tran_info['text']
    
    return(tran_text)
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 19:13:05 2020

@author: toocool
"""
import requests 
import http.client
from xml.etree import ElementTree
import os
from os import listdir
from os.path import isfile, isdir, join
from ftplib import FTP
#from os import walk

#------------------設定連線的 AZURE伺服器的資料 
apiKey ='b9752f97633d44e5a81821c194d5d7d4'   #需申請AZURE的API服務
AccessTokenHost = "southeastasia.api.cognitive.microsoft.com"   #需設定AZURE的雲端服務中心:southeastasia(此案例)
base_url = 'https://southeastasia.tts.speech.microsoft.com/'   #需設定AZURE的雲端服務中心:southeastasia(此案例)
#------------------設定連線的FTP伺服器的資料 (連結到WWW網站)
ftp_url ='waws-prod-hk1-015.ftp.azurewebsites.windows.net'
ftp_user ='private20170925\$private20170925'
ftp_passwd='hdx7cD0zoubpJJP9PpfuPClJch6jFXgxNa19FKix3Lf5jGsdpJSElr2SqTyw'

#英文--------------------------------------------------------------------------
def en(uid,trans_tts):
    voice_code='en-US' #設定語音合成語言種類
    voice_code_name='en-US-AriaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)
#中文-台灣-----------------------------------------------------------------------------------------------
def zh(uid,trans_tts):
    voice_code='zh-TW' #設定語音合成語言種類
    voice_code_name='zh-TW-HsiaoYuNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)

#日本
def ja(uid,trans_tts):
    voice_code='ja-JP' #設定語音合成語言種類
    voice_code_name='ja-JP-NanamiNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)    
#韓國  
def ko(uid,trans_tts):
    voice_code='ko-KR' #設定語音合成語言種類
    voice_code_name='ko-KR-SunHiNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   

#越南    
def vn(uid,trans_tts):
    voice_code='vi-VN' #設定語音合成語言種類
    voice_code_name='vi-VN-HoaiMyNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   
#馬來西亞
def ms(uid,trans_tts):
    voice_code='ms-MY' #設定語音合成語言種類
    voice_code_name='ms-MY-YasminNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   

#印尼
def id(uid,trans_tts):
    voice_code='id-ID' #設定語音合成語言種類
    voice_code_name='id-ID-ArdiNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)       

#泰國
def th(uid,trans_tts):
    voice_code='th-TH' #設定語音合成語言種類
    voice_code_name='th-TH-AcharaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)       

#印度    
def hi(uid,trans_tts):
    voice_code='hi-IN' #設定語音合成語言種類
    voice_code_name='hi-IN-SwaraNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   

         
#阿拉伯
def ar(uid,trans_tts):
    voice_code='ar-SA' #設定語音合成語言種類
    voice_code_name='ar-SA-ZariyahNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   

#土耳其
    
def tr(uid,trans_tts):
    voice_code='tr-TR' #設定語音合成語言種類
    voice_code_name='tr-TR-EmelNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   
#希伯來(以色列)
def he(uid,trans_tts):
    voice_code='he-IL' #設定語音合成語言種類
    voice_code_name='he-IL-HilaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)
#法語
def fr(uid,trans_tts):
    voice_code='fr-FR' #設定語音合成語言種類
    voice_code_name='fr-FR-DeniseNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)
#德語
def de(uid,trans_tts):
    voice_code='de-DE' #設定語音合成語言種類
    voice_code_name='de-DE-KatjaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
#西班牙語
def es(uid,trans_tts):
    voice_code='es-ES' #設定語音合成語言種類
    voice_code_name='es-ES-ElviraNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url) 

#葡萄牙語
def pt(uid,trans_tts):
    voice_code='pt-PT' #設定語音合成語言種類
    voice_code_name='pt-PT-FernandaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)    

#義大利語
def it(uid,trans_tts):
    voice_code='it-IT' #設定語音合成語言種類
    voice_code_name='it-IT-IsabellaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
# 希臘
def gr(uid,trans_tts):
    voice_code='el-GR' #設定語音合成語言種類
    voice_code_name='el-GR-AthinaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
  
#匈牙利    
def hu(uid,trans_tts):
    voice_code='hu-HU' #設定語音合成語言種類
    voice_code_name='hu-HU-NoemiNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)     
#波蘭
def pl(uid,trans_tts):
    voice_code='pl-PL' #設定語音合成語言種類
    voice_code_name='pl-PL-ZofiaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url) 

#丹麥
def dk(uid,trans_tts):
    voice_code='da-DK' #設定語音合成語言種類
    voice_code_name='da-DK-ChristelNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)    

#荷蘭
def nl(uid,trans_tts):
    voice_code='nl-NL' #設定語音合成語言種類
    voice_code_name='nl-NL-ColetteNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)     

#瑞典
def se(uid,trans_tts):
    voice_code='sv-SE' #設定語音合成語言種類
    voice_code_name='sv-SE-HilleviNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url) 
#芬蘭
def fi(uid,trans_tts):
    voice_code='fi-FI' #設定語音合成語言種類
    voice_code_name='fi-FI-NooraNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)   
#挪威
def no(uid,trans_tts):
    voice_code='nb-NO' #設定語音合成語言種類
    voice_code_name='nb-NO-IselinNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
#俄羅斯
def ru(uid,trans_tts):
    voice_code='ru-RU' #設定語音合成語言種類
    voice_code_name='ru-RU-DariyaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)
#捷克
def cz(uid,trans_tts):
    voice_code='cs-CZ' #設定語音合成語言種類
    voice_code_name='cs-CZ-VlastaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
#羅馬尼亞
def ro(uid,trans_tts):
    voice_code='ro-RO' #設定語音合成語言種類
    voice_code_name='ro-RO-AlinaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url) 
   
#保加利亞
def bg(uid,trans_tts):
    voice_code='bg-BG' #設定語音合成語言種類
    voice_code_name='bg-BG-KalinaNeural'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
#巴西
def br(uid,trans_tts):
    voice_code='pt-BR' #設定語音合成語言種類
    voice_code_name='pt-BR-HeloisaRUS'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url)  
#斯洛伐克
def sk(uid,trans_tts):
    voice_code='sk-SK' #設定語音合成語言種類
    voice_code_name='sk-SK-Filip'        
    params = ""
    headers = {"Ocp-Apim-Subscription-Key": apiKey}        
    path = "/sts/v1.0/issueToken"
    #print ("Connect to server to get the Access Token")
    conn = http.client.HTTPSConnection(AccessTokenHost)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    #print(response.status, response.reason)    
    data = response.read()
    conn.close()
    accesstoken = data.decode("UTF-8")
    #print ("Access Token: " + accesstoken)               
    ##----------------------設定要使用語音合成AZURE 雲端中心的網址與參數   
    path2 = 'cognitiveservices/v1'
    constructed_url = base_url + path2   
    ##-----------------------設定傳送到AZURE雲端中心API的參數
    headers = {
        'Authorization': 'Bearer ' + accesstoken,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3', #設定傳魂音效格視為mp3
        'User-Agent': 'TTSForPython'
    }    
    ##設定合成語音的文字傳送XML的內容與設定合成的語言
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    voice = ElementTree.SubElement(xml_body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', voice_code)
    # voice.set('gender', 'Female')
    voice.set('name', voice_code_name) # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
    voice.text = trans_tts
    body = ElementTree.tostring(xml_body)
    
    #傳回合成的的語音
    response = requests.post(constructed_url, headers=headers, data=body)   
    ####################################################################
    ##將傳回的語音檔寫入作目錄，並用FTP上傳到WWW網站，傳回合成語音網址給使用者
    if response.status_code == 200:
        with open(uid+'.mp3', 'wb') as audio:    # 參考 with open('sample-' + self.timestr + '.wav', 'wb') as audio:       
            audio.write(response.content) #將檔案寫入目前所在工作目錄 # response.content 是傳回的MP3檔案            
            # Working_Directory = os.getcwd()
            # print(Working_Directory) #HEROKU預設工作目錄為/app
            
            # mypath = '/app'            
            # for root, dirs, files in walk(mypath):
            #     print("路徑：", root)
            #     print("   目錄：", dirs)
            #     print("   檔案：", files)            
            # for root, dirs, files in walk(mypath):
            #     for f in files:
            #         fullpath = join(root, f)
            #         print(fullpath)                                                            
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                                  
            #print("Status code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")                        
            #-----------FTP到AZURE之WWW網站            
            ftp = FTP(ftp_url)
            ftp.login(user=ftp_user, passwd=ftp_passwd)           
            ftp.cwd('\site\wwwroot')
            #pwd_path = ftp.pwd()
            #print("FTP當前路徑:", pwd_path)            
            localfile = '/app/'+ uid + '.mp3'  #找到語音合成檔在在HEROKU中的位置，預設工作目錄為/app
            f = open(localfile, 'rb')
            ftp.storbinary('STOR %s' % os.path.basename(localfile), f) #上傳VOICE檔案
            ftp.quit    #FTP離線
            #設定語音網址
            voice_url='https://private20170925.azurewebsites.net/'+ uid + '.mp3'  
            
            os.remove(localfile)
            # files = listdir(mypath)
            # # 以迴圈處理
            # for f in files:
            #   # 產生檔案的絕對路徑
            #   fullpath = join(mypath, f)
            #   # 判斷 fullpath 是檔案還是資料夾
            #   if isfile(fullpath):
            #     print("檔案：", f)
            #   elif isdir(fullpath):
            #     print("資料夾：", f)                  
            # print(files)                               
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
        voice_url=''

    return(voice_url) 
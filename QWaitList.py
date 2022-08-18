# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 23:37:13 2020

@author: toocool
"""
from bs4 import BeautifulSoup
import requests
import re
import time

def answer(Qdept):
    #Qdept= '' input ('輸入欲查詢的候診科別:')
    #Dr_name= input ('輸入欲查詢醫生姓名，或看診科別名稱:')
    
    #Qdept='型外'
    #-------早上:1，下午:2，夜診，3。-------#
    
#---------------抓取雲端伺服器的時間美國--------------
    seconds = time.time()
    result = time.localtime(seconds)
    
    #now_hr=str(result.tm_hour)
    
#------------轉換判斷台灣小時時間，取得網頁查詢時段網址-----------  
    now_hr = str((result.tm_hour + 8 ) % 24) #轉24小時時刻       
    Qnow_period_url=''
    
    now_hr_dig = (result.tm_hour + 8) %24 + (result.tm_min / 60)
        
    if now_hr_dig >= 18:
        Qnow_period_url='&tonow=1900'
        Qnow_period='[夜 診]'
        
    elif now_hr_dig >= 13.5 :             
        Qnow_period_url='&tonow=1400'
        Qnow_period='[下午診]'
       
    else:
        Qnow_period_url='&tonow=0900'  
        Qnow_period='[上午診]'
#-------------時間轉文字-------------------    
    if result.tm_min < 10 :
        now_mn_str='0'+str(result.tm_min)
    else:
        now_mn_str= str(result.tm_min)
        
    if result.tm_sec < 10 :
        now_sec_str='0'+str(result.tm_sec)
    else:
        now_sec_str= str(result.tm_sec)    
        
    if int(now_hr) < 10:        
       now_hr_str= '0' + now_hr
    else:
       now_hr_str=str(now_hr) 
       
    Query_time_tw='查詢時間:' + now_hr_str + ':'+ now_mn_str + ':' + now_sec_str
# url ='http://www.kmsh.org.tw/pro/opdlights_data.asp?typeno=1&tonow=1400'
#------------抓取看診進度網址-------    
    url ='http://www.kmsh.org.tw/pro/opdlights_data.asp?typeno=1'+Qnow_period_url
    r = requests.get(url)
    line_mark0='*************************\n'
    line_mark='-------------------------\n'
        
    if now_hr_dig >= 8.5 :
        
        if r.status_code == requests.codes.ok: #網站可以回應爬蟲之資訊
            # 以 BeautifulSoup 解析 HTML 程式碼
            soup = BeautifulSoup(r.text,'html.parser',from_encoding='utf8')    
            tag_b_amount  = len(soup.find_all('b'))
            #print(soup.find_all('b'))
               
        #建立目前各科門診進度資訊LIST
            WaitInfo_list=[]
            WaitInfo_Date=soup.find_all('b')[0].get_text()+'年'+soup.find_all('b')[1].get_text()+'月'+soup.find_all('b')[2].get_text()+'日'
            Hos_title='小港醫院目前各門診看診進度:'
            WaitInfo_Date = Hos_title +'\n('+ WaitInfo_Date + Qnow_period +')\n' + Query_time_tw +'\n'+ line_mark0
            i=3
            while i < tag_b_amount: # i=96
                WaitInfo=''
                Dept=soup.find_all('b')[i].get_text()
                Doc_Name=soup.find_all('b')[i+1].get_text()
                Wait_N=soup.find_all('b')[i+2].get_text() 
                  
                if Wait_N=='休診':
                    Wait_N=soup.find_all('b')[i+2].get_text()[0:3]
                    i=i+1  #將休診後的等待數字移除
                    if Doc_Name == '侯明鋒':
                        i=i-1
                elif Wait_N=='代':
                    Doc_Name=Doc_Name+'(代)'
                    Wait_N = soup.find_all('b')[i+3].get_text()
                    Wait_N=re.sub('\r','',Wait_N)
                    Wait_N=re.sub('\t','',Wait_N)
                    Wait_N=re.sub('\n','',Wait_N)
                    i=i+1
                    if Wait_N=='休診':
                        i=i+1                        
                elif Doc_Name=='侯明鋒' :
                    i=i-1
                    Wait_N='先報到先看診!'                
                else:    
                    Wait_N=soup.find_all('b')[i+2].get_text()
                    Wait_N=re.sub('\r','',Wait_N)
                    Wait_N=re.sub('\t','',Wait_N)
                    Wait_N=re.sub('\n','',Wait_N)
                
                WaitInfo ='['+ Dept+']\n醫師:'+Doc_Name+'。看診號:'+Wait_N 
                WaitInfo_list.append(WaitInfo)
                i=i+3
               
        #用爬蟲找到的所有科別看診進度資訊，建立回應給使用者之資訊    
            All_DeptWait_Info=''
            if len(WaitInfo_list)>0:  
                for j in WaitInfo_list:
                    All_DeptWait_Info= All_DeptWait_Info + j + '\n' + line_mark  
                All_DeptWait_Info= WaitInfo_Date + All_DeptWait_Info 
            else: #找不到任何科別看診資訊，代表當天沒開門診
                All_DeptWait_Info= WaitInfo_Date + '\n目前時段無任何看診科別。'                
       #要查詢某科別看診進度---------------------------------------------- 
       #根據查詢的科別字串，Qdept_str，在當天之看診資訊串列，尋找看診進度資訊
       #當len(Qdept_str) = 0，代表不查詢特定科別，顯示所有當天的看診進度資訊 
            #Qdept=''
            if Qdept != '' :    
                count=0
                Dept_Wait_Info=''
                i=0
                while i <len(WaitInfo_list):
                    if WaitInfo_list[i].find(Qdept) !=-1:
                        Dept_Wait_Info= Dept_Wait_Info + WaitInfo_list[i] + '\n'+ line_mark
                        count=count+1
                    i=i+1
        #判斷是否找到查詢的看診科別    
                if count > 0: #代表找到查詢的科別看診進度資訊      
                    Response_Info= WaitInfo_Date+ '您要找的科別，目前看診號如下:\n' + line_mark + Dept_Wait_Info 
                else:
                    Response_Info='目前小港醫院的看診時段找不到您要查詢的科別:\n['+ Qdept +']科(門診)\n' + '-------------------------\n請您再確認查詢的看診科別!或是查詢"全部看診進度"!'
            else:
                Response_Info = All_DeptWait_Info
        else: 
            Response_Info='!!!看診進度網站維修中!!! \n'
    else :
        Response_Info='親愛的小港醫院病友!凌晨~早上8:30時間不提供門診看診號碼查詢!祝大家有個美夢。早上8:30以後才開始服務喔!'
    
    return(Response_Info)

# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 23:37:13 2020

@author: toocool
"""

import time

def avaiable():
       
#---------------抓取雲端伺服器的時間美國--------------
    clinic_time=False
    seconds = time.time()
    result = time.localtime(seconds)    
    #now_hr=str(result.tm_hour)    
#------------轉換判斷台灣小時時間，取得網頁查詢時段網址-----------                
    now_hr_dig = (result.tm_hour + 8) %24 + (result.tm_min / 60)  
    now_wk=result.tm_wday
    
    if  now_wk != 6:
        if now_wk == 5:
            if now_hr_dig >= 8.5 and now_hr_dig <= 12:
                clinic_time=True                
        else:
            if now_hr_dig >= 8.5 and now_hr_dig <= 12.5:
                clinic_time=True
            if now_hr_dig >= 13.5 and now_hr_dig <= 18:
                clinic_time=True                
            if now_hr_dig >= 18 and now_hr_dig <= 21:
                clinic_time=True  
                
    return(clinic_time)

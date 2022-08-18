# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 15:22:26 2020

@author:toocool
"""
import time

def get():
    seconds = time.time()
    result = time.localtime(seconds)
    year_now=result.tm_year
    year_tw=year_now-1911
    month_now=result.tm_mon
    
    month_now_str=''
    if month_now < 10:
        month_now_str='0'+ str(month_now)
    else:
        month_now_str = str(month_now)
        
    clinic_book='https://www.kmsh.org.tw/outpatient_doc/' + str(year_tw)+ month_now_str +'.pdf'
    
    return(clinic_book)

def hnews():
    seconds = time.time()
    result = time.localtime(seconds)
    year_now=result.tm_year
    year_tw=year_now-1911
    month_now=result.tm_mon
    
    month_now_str=''
    if month_now < 10:
        month_now_str='0'+ str(month_now)
    else:
        month_now_str = str(month_now)
        
    health_journal='http://www.kmhk.org.tw/news/New_Folder/' + str(year_tw)+ month_now_str +'健康衛教新知.pdf'
    
    return(health_journal)
    
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 11:47:55 2021

@author: wenzao
"""
import pandas as pd

#url_KMSH='http://www.kmsh.org.tw/pro/search_data2.asp?pno=244&dept_code=0400' 

def Find(url_KMSH):
#url1='http://www.kmsh.org.tw/pro/search_data2.asp?'    
#url_KMSH =url1 + 'pno=' + pno + '&dept_code='+ dept_code   
    
    getdata=pd.read_html(url_KMSH,header=None)   
    len_DF=len(getdata)  
    i=0
    j=0
    DF_str=''
    target_str=''
    for i in range(len_DF):
        str_getdata=getdata[i]                
        for j in str_getdata:       
            DF_str=str(str_getdata.iloc[0,j])
            if DF_str.find('上午診')!=-1 and DF_str.find('下午診')!=-1 and DF_str.find('夜診')!=-1 :
                target_str= DF_str  
                #print(target_str)
                #print(i)
                #print(j)
                break           
        break
    return(target_str)
        
                                        

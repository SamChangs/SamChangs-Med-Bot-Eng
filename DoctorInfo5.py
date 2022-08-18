# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:54:33 2020

@author: toocool
"""
import Bitly_Call
import Reurl_Call

# ##############################################################################
# #                    可看診日期之線上掛號網址看診產生模組
# ##############################################################################
# # ------------------------小港醫院線上掛號號所需參數----------------------------

def reg_url(RegDate,Noon,DeptNo,DocNo,DocName,DeptName):
    
    # Doc_No='840049'
    # Dept_No='0101'
    # Doc_Name='郭昭宏'
    # Dept_Name='胃腸內科(1)'
        
    # Dept_No='0109'    
    # Doc_No='890080'
    # Doc_Name='陳煌麒'
    # Dept_Name='胸腔內科'
        
    Rig_T='&txtT=400'
    Noon=str(Noon)
    #------------------------ 小港醫院線上掛號號所需參數----------------------------    
    Rig_web='https://www.kmsh.org.tw/online/HPRREG.asp?'
    Rig_Date='txtRegDate=' + RegDate
    Rig_Period='&txtNoon=' + Noon
    Rig_Dept='&txtDeptNo='+ DeptNo
    Rig_Doc_id='&txtDocNo='+DocNo
    Rig_T='&txtT=400'
    Rig_DocName='&txtDocName='+DocName
    Rig_DeptName='&txtDeptName='+DeptName
    Full_Rig_site=Rig_web+Rig_Date+Rig_Period+Rig_Dept+Rig_Doc_id+Rig_T+Rig_DocName+Rig_DeptName

    #將掛號網址轉換成短網址，呼叫短網址服務 
    # Full_Rig_site="https://www.kmsh.org.tw/online/HPRREG.asp?txtRegDate=2020/09/23&txtNoon=1&txtDeptNo=0109&txtDocNo=890080&txtT=400&txtDocName=陳煌麒&txtDeptName=胸腔內科"          
    # 
    ################################################################
    FRS_Short_Addr=Bitly_Call.ans(Full_Rig_site)
    
    if FRS_Short_Addr != '':  # 國外短網址服務 bitly.com ，1000筆/月     
        Reg_Avaiable_info ='網址->\n'+ FRS_Short_Addr 
    else: # 國外短網址服務 bitly.com，超載，則使用國內 (reurl.cc)進行短網址功能，速度變慢#假如國內短網址服務(reurl.cc)沒有超載 100次/小時，則使用(reurl.cc) 
        FRS_Short_Addr= Reurl_Call.ans(Full_Rig_site)
        Reg_Avaiable_info ='網址->\n'+ FRS_Short_Addr
        
    return(Reg_Avaiable_info)

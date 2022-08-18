# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 18:03:45 2020

@author: toocool
"""
     #Doc_Name='洪志興'
def get_docid(Doc_Name):
    
    doctor_db=[
           {'c_name':'郭昭宏','pno':'158','dept_code':'0100','DeptNo':'0101','DocNo':'840049'},           
           {'c_name':'陳煌麒','pno':'176','dept_code':'0100','DeptNo':'0109','DocNo':'890080'},
           {'c_name':'陳俊鴻','pno':'389','dept_code':'1000','DeptNo':'1001','DocNo':'900044'},
           {'c_name':'洪志興','pno':'244','dept_code':'0400','DeptNo':'0401','DocNo':'940269'},
           {'c_name':'李書欣','pno':'570','dept_code':'0200','DeptNo':'0270','DocNo':'830170'},
           
            ]
    
    doc_info=[]
    for i in  doctor_db:
        if i['c_name']==Doc_Name:
            doc_info = i            
            break
       
    return(doc_info)
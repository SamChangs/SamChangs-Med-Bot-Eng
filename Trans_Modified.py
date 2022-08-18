# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 22:44:32 2020

@author: wenzao
"""
#user_message='你有拉肚子嗎?'
def get(user_message):
    
    modified_message=user_message
    
    if user_message.find('拉肚子') != -1:
        modified_message = user_message.replace('拉肚子', '腹瀉')
    elif user_message.find('便當') != -1:
        modified_message = user_message.replace('便當', '餐盒')
    elif user_message.find('流鼻水') != -1:
        modified_message = user_message.replace('流鼻水', '流鼻涕')
    elif user_message.find('看') != -1 and user_message.find('科') != -1  :
        modified_message = user_message.replace('看', '掛號')    
    # elif user_message.find('廁所') != -1:
    #     modified_message = user_message.replace('廁所', '流鼻涕')    
    
    return modified_message    
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 19:41:55 2020

@author: wenzao
"""

import Azure_Translator #APP微軟翻譯使用Python模組

def results(user_message,lang_code):
    
    trans_message = user_message
    
    if len(trans_message) < 30:
        
        #判斷使用者想要翻譯的語言種類                            
        if lang_code=='英':            
            trans_message = Azure_Translator.en(trans_message)
                        
        elif lang_code=='日':            
            trans_message = Azure_Translator.ja(trans_message)
                        
        elif lang_code=='韓':            
            trans_message = Azure_Translator.ko(trans_message)
           
        elif lang_code=='法':            
            trans_message = Azure_Translator.fr(trans_message)
            
        elif lang_code=='德':            
            trans_message = Azure_Translator.de(trans_message)
            
        elif lang_code=='西':            
            trans_message = Azure_Translator.es(trans_message)
            
        elif lang_code=='越':            
            trans_message = Azure_Translator.vi(trans_message)
            
        elif lang_code=='印':            
            trans_message = Azure_Translator.id(trans_message)
            
        elif lang_code=='泰':            
            trans_message = Azure_Translator.th(trans_message) 
            
        elif lang_code=='度':
            trans_message = Azure_Translator.hi(trans_message)
        
        elif lang_code=='菲':
            trans_message = Azure_Translator.fil(trans_message)
        
        elif lang_code=='馬':
            trans_message = Azure_Translator.ms(trans_message)
        
        elif lang_code=='阿':
            trans_message = Azure_Translator.ar(trans_message) 

        elif lang_code=='俄':
            trans_message = Azure_Translator.ru(trans_message) 

        elif lang_code=='波':
            trans_message = Azure_Translator.pl(trans_message)             

        elif lang_code=='義':
            trans_message = Azure_Translator.it(trans_message)

        elif lang_code=='葡':
            trans_message = Azure_Translator.pt(trans_message)
            
        elif lang_code=='荷':
            trans_message = Azure_Translator.nl(trans_message) 
            
        elif lang_code=='瑞':
            trans_message = Azure_Translator.sv(trans_message)     
        
        elif lang_code=='捷':
            trans_message = Azure_Translator.cs(trans_message)
            
        elif lang_code=='孟':
            trans_message = Azure_Translator.bn(trans_message)
            
        elif lang_code=='希':
            trans_message = Azure_Translator.el(trans_message)

        elif lang_code=='愛':
            trans_message = Azure_Translator.ga(trans_message)

        elif lang_code=='挪':
            trans_message = Azure_Translator.nb(trans_message) 
            
        elif lang_code=='土':            
            trans_message = Azure_Translator.tr(trans_message)   
        
        elif lang_code=='烏':            
            trans_message = Azure_Translator.uk(trans_message) 
            
        elif lang_code=='匈':            
            trans_message = Azure_Translator.hu(trans_message)  

        elif lang_code=='海':            
            trans_message = Azure_Translator.ht(trans_message)

        elif lang_code=='芬':            
            trans_message = Azure_Translator.fi(trans_message) 

        elif lang_code=='丹':            
            trans_message = Azure_Translator.da(trans_message) 

        elif lang_code=='斯':            
            trans_message = Azure_Translator.fa(trans_message)

        elif lang_code=='羅':            
            trans_message = Azure_Translator.ro(trans_message)

        elif lang_code=='伯':            
            trans_message = Azure_Translator.he(trans_message) 
        
        elif lang_code=='巴':            
            trans_message = Azure_Translator.br(trans_message)             
            
        else:  #預設為英文英
            lang_code='英'
                                    
        response_info= trans_message                   
        #line_bot_api.push_message(uid, TextSendMessage(trans_message))
        #line_bot_api.push_message(uid, voice_message)
    else:
        #line_bot_api.push_message(uid, TextSendMessage('您要求的翻譯字數，超過我的翻譯能力限制(25字以內)!!!'))
        response_info='您要求的翻譯字數，超過我的翻譯能力限制(25字以內)!!!'
    return response_info   
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 14:26:36 2020

@author: wenzao
"""

from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
line_bot_api = LineBotApi('4ACf5tCKLKNRqvTCK6xo/j5i8su4xz8m7A4ZqU58ANNORVfrv7Da5BgPPs+9DVZQa6cROfZirs7NGmEgUp302oFohyPHnfF95InEln766mBRObcJT8xpI+d5dWsGSiXHyeYeE71c0VAmfOGXYR1ApQdB04t89/1O/w1cDnyilFU=')
#line_bot_api = LineBotApi('edFUkQybndZah161EJSfCNEhnNbwrS92WB2W8w+/uSZJiI+U+u5Ylfw7rBT32kplCQ3DahfN3+LdayHLDOMwJ0QSMZkHxRhdUo6A3Im9+R1xq3XuvB65DdH9dLUPSuiimB7cJA9G6qxdt+s8ZpjThQdB04t89/1O/w1cDnyilFU=')


######################### 胃腸內科 ###########################################
def send(uid):
       
    lang_menu = TextSendMessage(
        alt_text='喜歡的翻譯語言',
        quick_reply=QuickReply(
            items=[
# -----------------------------------------------------------------------------                    
                QuickReplyButton(                    
                    action = MessageAction(label='英(美)語',
                            text='翻譯英語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='日語',
                            text='翻譯日語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='越南語',
                            text='翻譯越南語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='泰語',
                            text='翻譯泰語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='印尼語',
                            text='翻譯印尼語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='馬來西亞語',
                            text='翻譯馬來西亞語')
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='印度語',
                            text='翻譯印度語')                                            
                ), 
                QuickReplyButton(                    
                    action = MessageAction(label='阿拉伯語',
                            text='翻譯阿拉伯語')                                            
                ), 
                QuickReplyButton(                    
                    action = MessageAction(label='韓語',
                            text='翻譯韓語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='法語',
                            text='翻譯法語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='德語',
                            text='翻譯德語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='西班牙語',
                            text='翻譯西班牙語')                       
                ),
                QuickReplyButton(                    
                    action = MessageAction(label='葡萄牙語',
                            text='翻譯葡萄牙語')                       
                ),                
#------------------------------------------------------------------------------                           
            ]
        )
                                                                   
    )

    #line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, lang_menu) 
    return 0
    

    

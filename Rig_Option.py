# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 00:43:05 2020

@author: toocool
"""
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
line_bot_api = LineBotApi('F5q3+1gA8yhn4TUrhfxY2g4izN0zK4fOc/6aHB8IDAuMMyXkRSLNKWeQctDL0LfUZtesB89QjNqoQeOSXKeOTfzxiX9wwn//CmU+1s1Ifa6avkuS4v7C7Zfbbov/i7H7Xm9vnz8b3Xrb9JN+okpL6gdB04t89/1O/w1cDnyilFU=')
#line_bot_api = LineBotApi('edFUkQybndZah161EJSfCNEhnNbwrS92WB2W8w+/uSZJiI+U+u5Ylfw7rBT32kplCQ3DahfN3+LdayHLDOMwJ0QSMZkHxRhdUo6A3Im9+R1xq3XuvB65DdH9dLUPSuiimB7cJA9G6qxdt+s8ZpjThQdB04t89/1O/w1cDnyilFU=')

def Ask(uid,dept):
    reg_info = TemplateSendMessage(
                    alt_text=dept,
                    template = ButtonsTemplate(                    
                        title='看診建議掛號科別:',
                        text= dept,
                        actions= [
                            MessageTemplateAction(
                                label=dept,
                                text=dept
                                ),
                            MessageTemplateAction(
                                label= 'Continue',
                                text= 'Medical Department Recommendation'
                                ),
                            MessageTemplateAction(
                                label= 'Leave consultation advice',
                                text= 'Leave the Medical Department'
                                ),
                        
                        ]
                    )
            )           
    line_bot_api.push_message(uid, reg_info)
   
    #line_bot_api.reply_message(event.reply_token,clinic_message)  
    return 0            
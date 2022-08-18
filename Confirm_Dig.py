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

def Ask(uid):
    confirm_template_message = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='是否離開[看診建議]功能，以使用其他各項資訊服務功能?',
                    actions=[
                        MessageAction(                            
                            label='看診建議',
                            text='看診建議'
                        ),
                        MessageAction(
                            label='離開看診',
                            text='離開看診'
                        )
                    ]
                )
            )
    line_bot_api.push_message(uid, confirm_template_message)
    #line_bot_api.reply_message(event.reply_token,clinic_message)  
    return 0            

def Qry(uid):
    confirm_template_message = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='您查詢的是[看診建議]功能的關鍵字!是否要使[看診建議]，以查詢身體症狀之建議看診科別?',
                    actions=[
                        MessageAction(                            
                            label='看診建議',
                            text='看診建議'
                        ),
                        MessageAction(
                            label='離開看診',
                            text='離開看診'
                        )
                    ]
                )
            )
    line_bot_api.push_message(uid, confirm_template_message)
    #line_bot_api.reply_message(event.reply_token,clinic_message)  
    return 0 

def Sit(uid):
    confirm_template_message = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='是否離開[搜尋醫院]功能，以使用其他各項資訊服務功能?',
                    actions=[
                        MessageAction(
                            label='醫院搜尋',
                            text='醫院搜尋'
                        ),
                        MessageAction(
                            label='離開搜尋',
                            text='離開搜尋'
                        )
                    ]
                )
            )
    line_bot_api.push_message(uid, confirm_template_message)
    #line_bot_api.reply_message(event.reply_token,clinic_message)
    return 0
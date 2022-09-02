# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 00:43:05 2020

@author: toocool
"""
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
line_bot_api = LineBotApi('Q65IelWgsFiWzJL7srk++OKbP70q9OzqVJXAY3+iXKOOb/E0tVZ2+xJxgrfdN0jbmYmcz2SQEQIFugb0WMmSYkbO3odUAhS/NSVKdmCK60lk6omrnKTWc34zfSjAwoHVCf9ebnmd62zjdFyfE9EWfwdB04t89/1O/w1cDnyilFU=')
#line_bot_api = LineBotApi('edFUkQybndZah161EJSfCNEhnNbwrS92WB2W8w+/uSZJiI+U+u5Ylfw7rBT32kplCQ3DahfN3+LdayHLDOMwJ0QSMZkHxRhdUo6A3Im9+R1xq3XuvB65DdH9dLUPSuiimB7cJA9G6qxdt+s8ZpjThQdB04t89/1O/w1cDnyilFU=')

def Ask(uid):
    confirm_template_message = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='Do you want to leave the [Continue] function to use other information service functions?',
                    actions=[
                        MessageAction(                            
                            label='Continue',
                            text='Medical Department Recommendation'
                        ),
                        MessageAction(
                            label='Leave',
                            text='Leave the Medical Department'
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
                    text='What you are looking for is the keyword of the [Diagnosis Suggestion] function! Do you want to use [Diagnosis Suggestion] to query the recommended medical department for physical symptoms?',
                    actions=[
                        MessageAction(                            
                            label='Continue',
                            text='Medical Department Recommendation'
                        ),
                        MessageAction(
                            label='Leave ',
                            text='Leave the Medical Department'
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
                    text='Whether to exit the [Hospital Search] function and use other information service functions?',
                    actions=[
                        MessageAction(
                            label='Hospital Search',
                            text='Hospital Search'
                        ),
                        MessageAction(
                            label='Leave Search',
                            text='Leave Search'
                        )
                    ]
                )
            )
    line_bot_api.push_message(uid, confirm_template_message)
    #line_bot_api.reply_message(event.reply_token,clinic_message)
    return 0
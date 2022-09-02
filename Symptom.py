# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 14:26:36 2020

@author: wenzao
"""

from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
line_bot_api = LineBotApi('Q65IelWgsFiWzJL7srk++OKbP70q9OzqVJXAY3+iXKOOb/E0tVZ2+xJxgrfdN0jbmYmcz2SQEQIFugb0WMmSYkbO3odUAhS/NSVKdmCK60lk6omrnKTWc34zfSjAwoHVCf9ebnmd62zjdFyfE9EWfwdB04t89/1O/w1cDnyilFU=')
#line_bot_api = LineBotApi('edFUkQybndZah161EJSfCNEhnNbwrS92WB2W8w+/uSZJiI+U+u5Ylfw7rBT32kplCQ3DahfN3+LdayHLDOMwJ0QSMZkHxRhdUo6A3Im9+R1xq3XuvB65DdH9dLUPSuiimB7cJA9G6qxdt+s8ZpjThQdB04t89/1O/w1cDnyilFU=')

######################### 胃腸內科 ###########################################
def Head(uid):
       
    sym_message = TemplateSendMessage(
        alt_text='Head Symptoms',
        template=CarouselTemplate(
            columns=[
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='Head Symptoms Menu-1/4',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='頭痛/頭暈/頭沉重',
                            text='H1'
                        ),
                        MessageTemplateAction(
                            label='吞嚥進食困難',
                            text='H2'
                        ),
                       MessageTemplateAction(
                            label='頸部變形/疼痛/麻木',
                            text='H3'
                        )                            
                    ]
                ),
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='Head Symptoms Menu-2/4',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='鞏膜泛黃',
                            text='H4'
                        ),
                        MessageTemplateAction(
                            label='青春痘/掉髮/皮膚黑斑',
                            text='H5'
                        ),
                       MessageTemplateAction(
                            label='頭部撞擊/後頸疼痛',
                            text='H6'
                        )                            
                    ]
                ),               
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='Head Symptoms Menu-3/4',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='喉嚨痛沙啞/聽力障礙/頸部腫塊',
                            text='H7'
                        ),
                        MessageTemplateAction(
                            label='視力模糊/眼睛乾澀/異物感',
                            text='H8'
                        ),
                       MessageTemplateAction(
                            label='眼睛有飛蚊/眼睛癢疼痛/眼睛癢',
                            text='H9'
                        )                            
                    ]
                ),
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='Head Symptoms Menu-4/4',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='牙齒敏感/酸痛/口臭黃牙',
                            text='H10'
                        ),
                        MessageTemplateAction(
                            label='牙齦紅腫/齒縫大',
                            text='H11'
                        ),
                       MessageTemplateAction(
                            label='口腔潰爛',
                            text='H12'
                        )                            
                    ]
                ),                                
#------------------------------------------------------------------------------
            ]
        )
    )
    #line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)    
    return 0
##############################################################################
def Head2(uid):
        
    sym_message = TemplateSendMessage(
        alt_text='頭頸部症狀2',
        template=CarouselTemplate(
            columns=[
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='頭頸部第二症狀選單-1/2',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='血壓高/暈倒',
                            text='H13'
                        ),
                        MessageTemplateAction(
                            label='發燒/紅疹/全身肌肉痛/關節痛',
                            text='H14'
                        ),
                       MessageTemplateAction(
                            label='耳鳴/鼻涕/喉嚨痛/聽力障礙',
                            text='H15'
                        )                            
                    ]
                ),
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='頭頸部第二症狀選單-2/2',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='頸部腫塊/聲音沙啞',
                            text='H16'
                        ),
                        MessageTemplateAction(
                            label='耳鳴/記憶力減退/嘴巴歪斜',
                            text='H17'
                        ),
                       MessageTemplateAction(
                            label='失眠/焦慮/抑鬱/恐慌/生氣',
                            text='H18'
                        )                            
                    ]
                ),               
# -----------------------------------------------------------------------------                    
            ]
        )
    )

    #line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)    
###############################################################################    
def Head3(uid):
        
    sym_message = TemplateSendMessage(
        alt_text='頭頸部症狀3',
        template=CarouselTemplate(
            columns=[
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='頭頸部第二症狀選單',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='上腹痛/腹脹/嘔吐',
                            text='H19'
                        ),
                        MessageTemplateAction(
                            label='胸口灼熱',
                            text='H20'
                        ),
                       MessageTemplateAction(
                            label='頸部痠痛麻/無力/緊繃',
                            text='H21'
                        )                            
                    ]
                ),               
# -----------------------------------------------------------------------------                    
            ]
        )
    )

    #line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)    

###############################################################################    
def Neck(uid):
    sym_message = TemplateSendMessage(
        alt_text='頸部症狀',
        template=CarouselTemplate(
            columns=[
# -----------------------------------------------------------------------------                    
                CarouselColumn(
                    #image_aspect_ratio='square',
                    #imageSize='contain',
                    #thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                    title='Neck Symptoms Menu',
                    text='Please select the symptoms you currently have, such as :  ',
                    actions=[
                        MessageTemplateAction(
                            label='後頸頭痛/頭部撞擊',
                            text='N1'
                        ),
                        MessageTemplateAction(
                            label='頸部變形/疼痛/麻木',
                            text='N2'
                        ),
                       MessageTemplateAction(
                            label='頸部腫塊',
                            text='N3'
                        )                            
                    ]
                ),               
# -----------------------------------------------------------------------------                    
            ]
        )
    )

    #line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)     
    
    
    

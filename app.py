# -*- coding: utf-8 -*-
# By Toocool Chen

from flask import Flask, request, abort	
from linebot import (LineBotApi, WebhookHandler, exceptions)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from local import *
import re

#import user_state
import QWaitList

#from bs4 import BeautifulSoup
#import pandas as pd  #爬取醫院網站使用
#from datetime import datetime

import clinic_time
import Short_Address  # 將醫生看診時間之掛號網址縮短時會用到
#import bitly_api      #Short_Address 模組短網址呼叫使用，Python 程式模組
#import requests, uuid # 連線微軟翻譯使用模組
import Azure_Translator #APP微軟翻譯使用Python模組
import Azure_Translator_Voice  #APP微軟翻譯使用Python模組
import cool_translate
import Trans_Modified

import Voice_Lang
import Lang_Check
import Lang_Menu
   
#import doc_jobstr
import DoctorInfo5
import DoctorCollection

import KMSH_UserDB_Con # 雲端資料庫KMSH-bot使用模組
import KMSH_DoctorDB_Inquiry # 雲端資料庫KMSH-bot使用模組


#from pymongo import MongoClient
from urllib.parse import quote #文字轉網頁模式
 
import time

import Clinic_Book

import Clinic_Dept #需要更改 LINE_BOT_API 之函式模組
import Symptom
import Confirm_Dig
import Rig_Option

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('F5q3+1gA8yhn4TUrhfxY2g4izN0zK4fOc/6aHB8IDAuMMyXkRSLNKWeQctDL0LfUZtesB89QjNqoQeOSXKeOTfzxiX9wwn//CmU+1s1Ifa6avkuS4v7C7Zfbbov/i7H7Xm9vnz8b3Xrb9JN+okpL6gdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('e1fb7aa93b285f73c7fd0b0329b26678')
# LINE BOT 開發者預設ID，以接收啟動信息 
line_bot_api.push_message('U1a447107797cfe0a2e2c8443df084569', TextSendMessage(text='OK,I am DR. Echo! May I help you? ｡^‿^｡'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
# ===========================================================
#               KMSH LINE BOT 主程式       
# ===========================================================

#-------------- 抓取使用者經緯度搜尋醫院-----------------------------------------
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(e):
    profile = line_bot_api.get_profile(e.source.user_id)
    uid = profile.user_id
    work_mode = KMSH_UserDB_Con.get_trmode(uid)
    lat = e.message.latitude
    long = e.message.longitude

    if work_mode[0] == 'M':
        message_inside = Type_of_visit([lat, long])

        line_bot_api.push_message(uid,message_inside)

# -------------- 加入或刪除使用者儲存的醫院、查詢使用者附近醫院 -----------------------------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id
    work_mode = KMSH_UserDB_Con.get_trmode(uid)

    if work_mode[0] == 'M':
        if "action=add" in event.postback.data:
            data = event.postback.data.split(",")
            hs_Name = data[2]
            current_db_type = data[1]
            message = KMSH_UserDB_Con.add_my_Hospital(uid, hs_Name, current_db_type)

            line_bot_api.reply_message(
                event.reply_token,
                message)

        if "action=del" in event.postback.data:
            data = event.postback.data.split(",")
            hs_Name = data[1]
            message = KMSH_UserDB_Con.del_my_Hospital(uid, hs_Name)

            line_bot_api.reply_message(
                event.reply_token,
                message)

        if "action=time" in event.postback.data:
            data = event.postback.data.split(",")
            hs_Name = data[1]
            Vs_time = data[2]
            message = hs_Name + "\n\n" + Visiting_Time(Vs_time)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text= message))

        if "action=search" in event.postback.data:
            data = event.postback.data.split(",") #["action=search", lan, long]
            lan = data[1]
            long = data[2]
            types = data[3]

            message = Search_address(float(lan), float(long), types)
            # print(message)
            line_bot_api.push_message(uid,message)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):  
  #-------------- 抓到Line@ USER 的資料-----------------------------------------
    profile = line_bot_api.get_profile(event.source.user_id)
    nameid = profile.display_name     #使用者名稱
    uid = profile.user_id             #使用者ID
#---- 如果這個使用者沒有紀錄的話，就將他的基本資料紀錄到使用者資料庫--------------
    if KMSH_UserDB_Con.find_user(uid)== False:
        KMSH_UserDB_Con.write_user(nameid,uid)
#--------------- 把使用者講的話資存下來 user_message--------------               
    user_message=str(event.message.text)     
#-----------------------------------------------------------
# line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))    
# uid='U1a447107797cfe0a2e2c8443df084569'
# user_message='我要印度文翻譯 今天天氣很好'  lang='度'   user_message='就醫建議' 
#----------------------使用者翻譯狀態檢查---預設不翻譯------------------------------- 

    work_mode = KMSH_UserDB_Con.get_trmode(uid)  #取得使用者進入的模式，如中翻外語，外語翻中文，就診推薦模式，等

############################# 中文翻成外語外語模式 #############################
    if work_mode[0] == 'Y' : #若使用者前一次的訊息有設定語言翻譯模式
    # 現在的訊息是接受到使用者想翻譯的訊息
        #-----------------------# 取消翻譯功能-----------------------
        if user_message.find('取消翻譯') != -1 or user_message.find('Quit') != -1 or user_message.find('quit') != -1:
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)
            Response_info = '好的!取消翻譯功能!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
       # user_message='我要翻譯韓語' user_message='我要波斯語翻譯'    #user_message='翻譯馬來西亞語' user_message='翻譯羅馬尼亞語'
        #----------------------變更翻譯語言種類--------------------------    
        elif user_message.find('翻譯') != -1 :  
            user_message=user_message.lstrip()             
            new_lang_code = Lang_Check.getcode(user_message)
            new_lang_name = Lang_Check.getname(new_lang_code)                       

            # #進行使用者翻譯模式設定    
            if len(new_lang_code)>0:                                                    
                pre_workmode = KMSH_UserDB_Con.get_trmode(uid)
                pre_lang_code = pre_workmode[1]                
                                
                if  new_lang_code != pre_lang_code:
                    KMSH_UserDB_Con.set_trmode(uid,new_lang_code) 
                    Response_info='(1)好的，切換['+new_lang_name +'翻譯]!\n(2)若要停止翻譯，請下[取消翻譯功能]、[Quit]、[quit]的文字命令!!\n(3)翻譯語音的合成要等耐心一下喔!大約需要6~8秒左右!'
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
                else:
                    Response_info='(1)您已經在['+new_lang_name+'翻譯]的功能中!\n(2)若要停止翻譯，請下[取消翻譯功能]、[Quit]、[quit]的文字命令!!\n(3)翻譯語音的合成要等耐心一下喔!大約需要6~8秒左右!'
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info)) 
                     
            else:
                Response_info='沒有您要求的語言翻譯功能!我只有英(美)、日、韓、法、德、西、葡、印度、印尼、越南、泰語、馬來西亞、阿拉伯語的翻譯!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
         #----------------------設定翻譯語言種類--------------------------
        # user_message='我要翻譯韓語' user_message='我要馬來西亞語翻譯'    #user_message='翻譯亞語'       
        elif user_message.find('外語選單') != -1: 
            lang_menu = TemplateSendMessage(
                alt_text='外語翻譯選單',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/FtA-p01ZiAP1eA-8WOTFAlU793Q4smX7OgGxjD0svgWKR-3nmiIwADfRqSezAQSPlaHOHP0FHayqz2Hu2i1zlazGeC0GuPgqwq_-IZhb7pNRgv8Nk-ePBe7GSTdPcr-zsS9mHaG6NQ=w600',
                            title='外語翻譯選單-1/10',
                            text='亞洲語系翻譯(1/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='英(美)語',
                                    text='翻譯英語'
                                ),
                                MessageTemplateAction(
                                    label='日語',
                                    text='翻譯日語'
                                ),
                                MessageTemplateAction(
                                    label='韓語',
                                    text='翻譯韓語'
                                )                            
                            ]
                        ),                        
    # -----------------------------------------------------------------------------
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/FKSRSGWwJttJXxWqGVQh1NK_B6Y0coj7zjIsfBw2zCLOXqyCoJdEc3p1QfrslhUH_vLJAch9duWwh_4qSJ2rQzYzMXVGqIp9RKmfdUVLTtNhhKwAtBDUw_m6hJthgssXy8mqYY9BvQ=w600',
                            title='外語翻譯選單-2/10',
                            text='亞洲語系翻譯(2/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='越南語',
                                    text='翻譯越南語'
                                ),
                                MessageTemplateAction(
                                    label='馬來西亞語',
                                    text='翻譯馬來西亞語'
                                ),
                                MessageTemplateAction(
                                    label='印尼語',
                                    text='翻譯印尼語'
                                )                            
                            ]
                        ), 
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/ii9yNKlFFIHKc8JS3Lp0xJJbbFVZxF-IIXAo9UgaUXBMzgmu2eR57Q8yfroKg084mRd-ooBLjvxwBeZRVdYRIDNqm6gW2bDOyUFVT6zD9h4GOu0lMjux1QfeGiUblBNs1Lahwffjjw=w600',
                            title='外語翻譯選單-3/10',
                            text='亞洲語系翻譯(3/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='泰語',
                                    text='翻譯泰語'
                                ),
                                MessageTemplateAction(
                                    label='印度語',
                                    text='翻譯印度語'
                                ),
                                MessageTemplateAction(
                                    label='阿拉伯語',
                                    text='翻譯阿拉伯語'
                                )                            
                            ]
                        ),
    # -----------------------------------------------------------------------------
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/Dg7oaQ7DqWg9VKjb0jlIJIoEeWXsxMnj5LBUU_Go3kyf2M64LYYjtKW03hTiibqyvhX-GO-ApNWR0M_4htARzptPyNBKvreuxwaP_4yt2xsc_-jD7mbd-J_vXBDjxDV4leZLMuujeQ=w600',
                            title='外語翻譯選單-4/10',
                            text='歐亞洲語系翻譯(4/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='希伯來語(以色列)',
                                    text='翻譯希伯來語'
                                ),
                                MessageTemplateAction(
                                    label='土耳其語',
                                    text='翻譯土耳其語'
                                ),
                                MessageTemplateAction(
                                    label='保加利亞語',
                                    text='翻譯保加利亞語'
                                )                            
                            ]
                        ), 
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/lYYC3KONJ-r8MPuO6NlR92JQocBqioz6d4L_IJMfcWVuZ54IT4jnOGrRB4Nbfm-B-eolh5ijP7tuJCIdPprH3VGf_6zcuDyWrWJGqS5maLxdyyRLaOy3TcKoOlDc3mSE3g599ANr2Q=w600',
                            title='外語翻譯選單-5/10',
                            text='歐洲語系翻譯(1/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='英(美)語',
                                    text='翻譯英語'
                                ),
                                MessageTemplateAction(
                                    label='法語',
                                    text='翻譯法語'
                                ),
                                MessageTemplateAction(
                                    label='德語',
                                    text='翻譯德語'
                                )                            
                            ]
                        ),
    #-----------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/EboLBmHXVpQlk3hrpdHZlLEzjnGGAvjuCGsI32si5ekjX-t6CcUWe6AX1o0lElKvj4pfKLINxMKDzaWFFjliDHMzgTk35M1ShkRlT0S8CrUctVVAHC51Y0zFgVlmRMcdp_U4lC8kgw=w600',
                            title='外語翻譯選單-6/10',
                            text='歐洲語系翻譯(2/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='西班牙語',
                                    text='翻譯西班牙語'
                                ),
                                MessageTemplateAction(
                                    label='葡萄牙語',
                                    text='翻譯葡萄牙語'
                                ),
                                MessageTemplateAction(
                                    label='葡萄牙語(巴西)',
                                    text='翻譯巴西語'
                                )                            
                            ]
                        ),                                          
    #------------------------------------------------------------------------------
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/_rparADUnbJJnpb65H7ayhR1AGVm3NWNbDBZiyjnnzxZP6kgvWe4Umhbom9n4ux9IqLJw4f11FTNuSqiWEtGgUvCpPKztQPqWHVPdRJw3QuLfT7eDEo6oFNZCRES9HCeVESSGC3Dpw=w600',
                            title='外語翻譯選單-7/10',
                            text='歐洲語系翻譯(3/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='義大利語',
                                    text='翻譯希臘語'
                                ),
                                MessageTemplateAction(
                                    label='希臘語',
                                    text='翻譯希臘語'
                                ),
                                MessageTemplateAction(
                                    label='匈牙利語',
                                    text='翻譯匈牙利語'
                                )                            
                            ]
                        ),                        
     
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/5ihsLofivptsynCymdVOH4mVJSU_BVkkCV3G9FuDVRbB-94f11bxTYiWJ9FinDcFkuHZbfgaPbdDEwaprd9eLsoZWV6i6er0zklomk035VXUwke0mCjtK2Ljm6pBd_1YRx3vkvvQ_A=w600',
                            title='外語翻譯選單-8/10',
                            text='歐洲語系翻譯(4/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='波蘭語',
                                    text='翻譯波蘭語'
                                ),
                                MessageTemplateAction(
                                    label='丹麥語',
                                    text='翻譯丹麥語'
                                ),
                                MessageTemplateAction(
                                    label='荷蘭語',
                                    text='翻譯荷蘭語'
                                )                            
                            ]
                        ),
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/-2lYj7IxjNABSjyP-YhmFakXpuWuI-1sxc6Bms2vH2qHXcLs6nM_OTW9caDURCwcteDgP72jn-naFj074hyP5GvLXWXRekkPwAZDfIaNyP76QjOz7a96i90WrZy93BExUFEOOQxjgA=w600',
                            title='外語翻譯選單-9/10',
                            text='歐洲語系翻譯(5/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='瑞典語',
                                    text='翻譯瑞典語'
                                ),
                                MessageTemplateAction(
                                    label='芬蘭語',
                                    text='翻譯芬蘭語'
                                ),
                                MessageTemplateAction(
                                    label='挪威語',
                                    text='翻譯挪威語'
                                )                            
                            ]
                        ),                    
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/ixYCUmAcRByFRZtPSmljEScE3rFss1BqiflLUUX4UHqHwOTlIuzREIG3WzH2D-ltmWgxUnnaKL7urxLOngzoPcXxmiUKrDBOiTMJtnybrsJQuifwY84YitAFrA1RfOoQ-V5x0GRTFw=w600',
                            title='外語翻譯選單-10/10',
                            text='歐洲語系翻譯(6/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='俄羅斯語',
                                    text='翻譯俄羅斯語'
                                ),
                                MessageTemplateAction(
                                    label='捷克語',
                                    text='翻譯捷克語'
                                ),
                                MessageTemplateAction(
                                    label='羅馬尼亞語',
                                    text='翻譯羅馬尼亞語'
                                )                            
                            ]
                        )  
    #------------------------------------------------------------------------------                    
                    ]
                )
            )         # 結束MESSAGE-TemplateSendMessage             
                                    
            line_bot_api.reply_message(event.reply_token,lang_menu)
            # line_bot_api.push_message(uid, care_message)        
            return 0
                    
     #------------------------在使用者先前設定語言的翻譯模式下進行翻譯--------------------------------       
        else:  
            lang_code= work_mode[1]
            user_message=user_message.lstrip() 
            message_modified=Trans_Modified.get(user_message)
            trans_message = cool_translate.results(message_modified,lang_code)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(trans_message)) #先回覆翻譯訊息
            
            vlang_code = Lang_Check.getvoicecode(lang_code) #取得GOOGLE語音訊碼
            voice_time=0.6*len(trans_message) #根據字元數計算時間長度
            if lang_code=='英' or lang_code=='美':
                voice_get_url=Azure_Translator_Voice.en(uid,trans_message)                
            elif lang_code=='日':  
                 voice_get_url=Azure_Translator_Voice.ja(uid,trans_message)
            elif lang_code=='韓':  
                 voice_get_url=Azure_Translator_Voice.ko(uid,trans_message) 
            elif lang_code=='法':  
                 voice_get_url=Azure_Translator_Voice.fr(uid,trans_message)  
            elif lang_code=='德':  
                 voice_get_url=Azure_Translator_Voice.de(uid,trans_message)
            elif lang_code=='西':  
                 voice_get_url=Azure_Translator_Voice.de(uid,trans_message)  
            elif lang_code=='葡':  
                 voice_get_url=Azure_Translator_Voice.pt(uid,trans_message)                  
            elif lang_code=='印':  
                 voice_get_url=Azure_Translator_Voice.id(uid,trans_message)
            elif lang_code=='泰':  
                 voice_get_url=Azure_Translator_Voice.th(uid,trans_message)
            elif lang_code=='越':  
                 voice_get_url=Azure_Translator_Voice.vn(uid,trans_message)
            elif lang_code=='度':  
                 voice_get_url=Azure_Translator_Voice.hi(uid,trans_message) 
            elif lang_code=='馬':  
                 voice_get_url=Azure_Translator_Voice.ms(uid,trans_message)
            elif lang_code=='阿':  
                 voice_get_url=Azure_Translator_Voice.ar(uid,trans_message)
            elif lang_code=='義':  
                 voice_get_url=Azure_Translator_Voice.it(uid,trans_message)  
            elif lang_code=='俄':  
                 voice_get_url=Azure_Translator_Voice.ru(uid,trans_message)
            elif lang_code=='波':  
                 voice_get_url=Azure_Translator_Voice.pl(uid,trans_message)
            elif lang_code=='葡':  
                 voice_get_url=Azure_Translator_Voice.pt(uid,trans_message)
            elif lang_code=='荷':  
                 voice_get_url=Azure_Translator_Voice.nl(uid,trans_message) 
            elif lang_code=='瑞':  
                 voice_get_url=Azure_Translator_Voice.se(uid,trans_message)    
            elif lang_code=='捷':  
                 voice_get_url=Azure_Translator_Voice.cz(uid,trans_message)
            elif lang_code=='希':  
                 voice_get_url=Azure_Translator_Voice.gr(uid,trans_message)
            elif lang_code=='挪':  
                 voice_get_url=Azure_Translator_Voice.no(uid,trans_message)
            elif lang_code=='土':  
                 voice_get_url=Azure_Translator_Voice.tr(uid,trans_message)
            elif lang_code=='匈':  
                 voice_get_url=Azure_Translator_Voice.hu(uid,trans_message) 
            elif lang_code=='芬':  
                 voice_get_url=Azure_Translator_Voice.fi(uid,trans_message)
            elif lang_code=='丹':  
                 voice_get_url=Azure_Translator_Voice.dk(uid,trans_message) 
            elif lang_code=='羅':  
                 voice_get_url=Azure_Translator_Voice.ro(uid,trans_message) 
            elif lang_code=='伯':  
                 voice_get_url=Azure_Translator_Voice.he(uid,trans_message) 
            elif lang_code=='巴':  
                 voice_get_url=Azure_Translator_Voice.br(uid,trans_message)
            elif lang_code=='保':  
                 voice_get_url=Azure_Translator_Voice.bg(uid,trans_message)                    
            else:
                voice_get_url='https://google-translate-proxy.herokuapp.com/api/tts?query='+quote(trans_message)+'&language='+vlang_code                 
            
            voice_message=AudioSendMessage(
                original_content_url = voice_get_url,
                duration=(int(voice_time)+1)*1000,
            )                        
            line_bot_api.push_message(uid, voice_message) 
                        
        return 0                      
###############################外語翻成中文模式#################################
    elif work_mode[0] == 'R' :
        
        lang=work_mode[1]
        trans_message=''
        
        if user_message.find('Quit') != -1 or user_message.find('quit') != -1 : 
            
            lang=work_mode[1] #取得使用者設定的語言種類
            
            if lang == 'en':
                Response_info = 'OK! Quit translation!'
            elif  lang == 'ja':
                Response_info = 'さて、あなたは[翻訳]機能を残しました'
            elif  lang == 'ko':
                Response_info = '알겠습니다. [번역] 기능을 종료하셨습니다' 
            elif  lang == 'fr':
                Response_info = 'Daccord, vous avez quitté la fonction [traduction]'
            elif  lang == 'de':
                Response_info = 'Okay, Sie haben die Funktion [Übersetzung] verlassen' 
            elif  lang == 'es':
                Response_info = 'De acuerdo, dejaste la función [traducción]' 
            elif  lang == 'id':
                Response_info = 'Oke, Anda telah keluar dari fungsi [terjemahan]'
            elif  lang == 'th':
                Response_info = 'โอเคคุณออกจากฟังก์ชัน [การแปล] แล้ว'
            elif  lang == 'vi':
                Response_info = 'Được rồi, bạn đã rời khỏi chức năng [dịch]'
            elif  lang == 'fil':
                Response_info = 'Okay, iniwan mo ang pagpapaandar ng [pagsasalin]'
            elif  lang == 'ms':
                Response_info = 'Baiklah, anda telah meninggalkan fungsi [terjemahan]'
            elif  lang == 'hi':
                Response_info = 'ठीक है, [अनुवाद] फ़ंक्शन को छोड़ दें' 
            else:
                Response_info = 'OK! Quit translation!'
                            
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消翻譯模式          
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
        else:            
            
            trans_message=Azure_Translator.ZhHant(user_message)  #取得中文翻譯
            line_bot_api.reply_message(event.reply_token, TextSendMessage(trans_message)) #翻譯訊息回復
            
            voice_time=0.6*len(trans_message)
            Azure_voice_url = Azure_Translator_Voice.zh(uid,trans_message)    #取得AZURE中文語音連接結果
            voice_message=AudioSendMessage(
                original_content_url = Azure_voice_url,
                duration=(int(voice_time)+1)*1000
            )                
            line_bot_api.push_message(uid, voice_message)  #語音回覆訊息  
            
            
        return 0        

################################## 就診推薦狀態模式 ###############################
    elif work_mode[0] == 'D' :
        
        line_mark='\n-------------------------\n'   
        if user_message.find('取消看診') != -1 or user_message.find('離開看診') != -1:
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)  
            Response_info='好的，離開[看診建議]功能!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
        elif  user_message.find('看診建議') != -1:
            lang ='中'
            KMSH_UserDB_Con.set_trmode_d(uid,lang)
            
            diagnosis_message = TemplateSendMessage(
            alt_text='看診建議功能',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        #image_aspect_ratio='square',
                        #imageSize='contain',
                        #thumbnail_image_url='',
                        title='看診建議功能，選單Ｉ',
                        text='請選擇您現在有不舒服狀況的身體部位，如下選單:',
                        actions=[
                            MessageTemplateAction(
                                label='頭部',
                                text='頭部症狀'
                            ),
                            MessageTemplateAction(
                                label='頸部',
                                text='頸部症狀'
                            ),
                            MessageTemplateAction(
                                label='手腳四肢',
                                text='四肢症狀'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        #image_aspect_ratio='square',
                        #imageSize='contain',
                        #thumbnail_image_url='',
                        title='看診建議功能，選單Ｉ',
                        text='請選擇您現在有不舒服狀況的身體部位，如下選單:',
                        actions=[
                            MessageTemplateAction(
                                label='上腹部',
                                text='上腹部症狀'
                            ),
                            MessageTemplateAction(
                                label='下腹部',
                                text='下腹部症狀'
                            ),
                            MessageTemplateAction(
                                label='全身/皮膚',
                                text='全身皮膚症狀'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                   ]
               )
            )
        
            imagemap_message = ImagemapSendMessage(
            base_url='https://lh3.googleusercontent.com/K8i-XYfunqUI_vPB1kM3piCg1G0oh3aOEMo34zOg3v0a1pUDqKfllfQiP1bIPCaWhmxb8J0sb3daOBnmjY-g7pyEqSOvqhXL9oSz3CzAiF_CLBNYCrFtNgbo6zSL1UUxylwStMWShg=w1040#',
            alt_text=' imagemap',
            base_size=BaseSize(height=1040, width=1040),
               actions=[
                MessageImagemapAction (
                    text='頭部症狀',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=320
                    )
                ),
                MessageImagemapAction (
                    text='頸部症狀',
                    area=ImagemapArea(
                        x=0, y=320, width=520, height=260
                    )
                ),
                MessageImagemapAction (
                    text='四肢症狀',
                    area=ImagemapArea(
                        x=0, y=580, width=520, height=460
                    )
                ),
                MessageImagemapAction(
                    text='全身皮膚症狀',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='上腹部症狀',
                    area=ImagemapArea(
                        x=520, y=320, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='下腹部症狀',
                    area=ImagemapArea(
                        x=520, y=640, width=520, height=400
                    )
                ),
        
                ]
            )        
            #line_bot_api.push_message(uid, diagnosis_message)
            line_bot_api.push_message(uid, imagemap_message)
                                                
############################### 頭部症狀判斷 #######################################
        elif  user_message.find('頭部症狀') != -1:
            Symptom.Head(uid) 
            
        elif  user_message == 'H1' :
            s1='H1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))             
            Symptom.Head2(uid)
        
        elif  user_message == 'H2' :
            s1='H2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H2:吞嚥進食困難]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))            
            Symptom.Head3(uid) 
       
        elif  user_message == 'H3' : 
            s1='H3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H3:頸部變形/疼痛/麻木]。'+ line_mark +'建議看診科別:[骨科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            reg_info = TemplateSendMessage(
                alt_text='看診建議掛號科別:',
                template = ButtonsTemplate(                    
                    title='看診建議掛號科別:',
                    text= '[骨科]',
                    actions= [
                        MessageTemplateAction(
                            label= '掛號骨科A',
                            text='掛號骨科A'
                            ),
                        MessageTemplateAction(
                            label= '掛號骨科B',
                            text='掛號骨科B'
                            ),
                        MessageTemplateAction(
                            label= '繼續使用看診建議',
                            text= '看診建議'
                            ),
                        MessageTemplateAction(
                            label= '離開看診建議',
                            text= '離開看診'
                            ),
                        
                    ]
                )
            )           
            line_bot_api.push_message(uid, reg_info)            
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                   
        elif  user_message == 'H4' : 
            s1='H4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H4:鞏膜泛黃]。'+ line_mark +'建議看診科別:[肝膽胰內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號肝膽胰內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                                          
        elif  user_message == 'H5' : 
            s1='H5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H5:青春痘/掉髮/皮膚黑斑]。'+ line_mark +'建議看診科別:[皮膚科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                     
        elif  user_message == 'H6' : 
            s1='H6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H6:頭部撞擊/後頸疼痛]。'+ line_mark +'建議看診科別:[腦神經外科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腦神經外科'
            Rig_Option.Ask(uid,rig_dept) 
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
            
        elif  user_message == 'H7' : 
            s1='H7'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H7:喉嚨痛沙啞/聽力障礙/頸部腫塊]。'+ line_mark +'建議看診科別:[耳鼻喉科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                        
        elif  user_message == 'H8' : 
            s1='H8'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H8:視力模糊/眼睛乾澀/異物感]。'+ line_mark +'建議看診科別:[眼科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號眼科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        

        elif  user_message == 'H9' : 
            s1='H9'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H9:眼睛有飛蚊/眼睛癢疼痛/眼睛癢]。'+ line_mark +'建議看診科別:[眼科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))  
            rig_dept='掛號眼科'
            Rig_Option.Ask(uid,rig_dept) 
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)              

        elif  user_message == 'H10' : 
            s1='H10'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H10:牙齒敏感/酸痛/口臭黃牙]。'+ line_mark +'建議看診科別:[牙科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號牙科一診'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)

        elif  user_message == 'H11' : 
            s1='H11'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H11:牙齦紅腫/齒縫大]。'+ line_mark +'建議看診科別:[牙科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號牙科一診'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)             
                        
        elif  user_message == 'H12' : 
            s1='H12'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[H12:口腔潰瘍/潰爛]。'+ line_mark +'建議看診科別:[耳鼻喉科/牙科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))                        
            reg_info = TemplateSendMessage(
                alt_text='看診建議掛號科別:',
                template = ButtonsTemplate(                    
                    title='看診建議掛號科別:',
                    text= '[耳鼻喉科/牙科]',
                    actions= [
                        MessageTemplateAction(
                            label= '掛號耳鼻喉科',
                            text='掛號耳鼻喉科'
                            ),
                        MessageTemplateAction(
                            label= '掛號牙科',
                            text='掛號牙科'
                            ),
                        MessageTemplateAction(
                            label= '繼續使用看診建議',
                            text= '看診建議'
                            ),
                        MessageTemplateAction(
                            label= '離開看診建議',
                            text= '離開看診'
                            ),
                        
                    ]
                )
            )           
            line_bot_api.push_message(uid, reg_info)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)            
#--------------------頭部症狀 H1頭痛/頭暈/頭沉重 之 第二種症狀----------------------------------------            
        elif  user_message == 'H13' : 
            s2='H13'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]、\n[H13:血壓高/暈倒]。'+ line_mark +'建議看診科別:[心臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                      
                        
        elif  user_message == 'H14' : 
            s2='H14'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]、\n[H14:發燒/紅疹/全身肌肉痛/關節痛]。'+ line_mark +'建議看診科別:[感染內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號感染內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                       
             
        elif  user_message == 'H15' : 
            s2='H15'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]、\n[H15:耳鳴/鼻涕/喉嚨痛/聽力障礙]。'+ line_mark +'建議看診科別:[耳鼻喉科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        
 
        elif  user_message == 'H16' : 
            s2='H16'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]、\n[H16:頸部腫塊/聲音沙啞]。'+ line_mark +'建議看診科別:[耳鼻喉科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                       
                        
        elif  user_message == 'H17' : 
            s2='H17'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]、\n[H17:耳鳴/記憶力減退/嘴巴歪斜]。'+ line_mark +'建議看診科別:[神經內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號神經內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        
             
        elif  user_message == 'H18' : 
            s2='H18'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H1:頭痛/頭暈/頭沉重]、\n[H18:失眠/焦慮/抑鬱/恐慌/生氣]。'+ line_mark +'建議看診科別:[精神科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號精神科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                             
#-------------------------頭部症狀 H2吞嚥進食困難 之 第二種症狀---------------------------------------  
        elif  user_message == 'H19' : 
            s2='H19'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H2:吞嚥進食困難]、\n[H19:上腹痛/腹脹/嘔吐]。'+ line_mark +'建議看診科別:[胃腸內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                      
            
        elif  user_message == 'H20' : 
            s2='H20'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H2:吞嚥進食困難]、\n[H20:胸口灼熱]。'+ line_mark +'建議看診科別:[胃腸內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        
            
        elif  user_message == 'H21' : 
            s2='H21'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[H2:吞嚥進食困難]、\n[H21:頸部痠痛麻/無力/緊繃]。'+ line_mark +'建議看診科別:[復健科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號復健科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                  
########################## 頸部症狀 ############################################
        elif  user_message.find('頸部症狀') != -1:
            Symptom.Neck(uid)
            
        elif  user_message == 'N1' : 
            s1='N1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[N1:後頸頭痛/頭部撞擊]。'+ line_mark +'建議看診科別:[腦神經外科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號腦神經外科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
            
        elif  user_message == 'N2' : 
            s1='N2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[N2:頸部變形/疼痛/麻木]。'+ line_mark +'建議看診科別:[骨科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            reg_info = TemplateSendMessage(
                alt_text='看診建議掛號科別:',
                template = ButtonsTemplate(                    
                    title='看診建議掛號科別:',
                    text= '[耳鼻喉科/牙科]',
                    actions= [
                        MessageTemplateAction(
                            label= '掛號骨科A',
                            text='掛號骨科A'
                            ),
                        MessageTemplateAction(
                            label= '掛號骨科B',
                            text='掛號骨科B'
                            ),
                        MessageTemplateAction(
                            label= '繼續使用看診建議',
                            text= '看診建議'
                            ),
                        MessageTemplateAction(
                            label= '離開看診建議',
                            text= '離開看診'
                            ),
                        
                    ]
                )
            )           
            line_bot_api.push_message(uid, reg_info)                                   
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
            
        elif  user_message == 'N3' : 
            s1='N3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[N3:頸部腫塊]。'+ line_mark +'建議看診科別:[耳鼻喉科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)            
################################# 上腹部症狀 ###################################                  
        elif  user_message.find('上腹部症狀') != -1:
            sym_message = TemplateSendMessage(
                alt_text='上腹部症狀',
                template=CarouselTemplate(
                    columns=[
    # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='上腹部症狀選單-1/2',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='上腹部疼痛',
                                    text='U1'
                                ),
                                MessageTemplateAction(
                                    label='胸痛/胸悶/喘/咳嗽',
                                    text='U2'
                                ),
                               MessageTemplateAction(
                                    label='活動不良/身體部位萎縮',
                                    text='U3'
                                )                            
                            ]
                        ),
    # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='上腹部症狀選單-2/2',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='身體部位部位變形/疼痛/無力',
                                    text='U4'
                                ),
                                MessageTemplateAction(
                                    label='心悸/雙手抖動/眼凸/口渴/多吃',
                                    text='U5'
                                ),
                               MessageTemplateAction(
                                    label='頸部變形/疼痛/麻木',
                                    text='U6'
                                )                            
                            ]
                        ),                        
   #----------------------------------------------------------------------------                 
                    ]
                )
            )            
            line_bot_api.reply_message(event.reply_token,sym_message)            
#-----------------------------------------------------------------------------            
        elif  user_message =='U1':
            s1='U1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='先前已選四肢症狀:[上腹部疼痛]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))             
            sym_message = TemplateSendMessage(
                alt_text='上腹部症狀-2',
                template=ButtonsTemplate(                                                
                        title='其他部位症狀選單',
                        text='請選擇您目前有的身體症狀群，如下:',
                        actions=[
                            MessageTemplateAction(
                                label='黃疸',
                                text='U7'
                            ),
                            MessageTemplateAction(
                                label='下腹部痛/腹瀉/便秘/嘔吐',
                                text='U8'
                            ),
                            MessageTemplateAction(
                                label='腹脹/胸口灼熱/黑便或血便',
                                text='U9'
                            ),
                                                       
                        ]
                )
            )            
            line_bot_api.push_message(uid, sym_message)           
#-----------------------------------------------------------------------------            
        elif  user_message == 'U2':
            s1='U2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='先前已選四肢症狀:[胸痛/胸悶/喘/咳嗽]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))            
            sym_message = TemplateSendMessage(
                alt_text='上腹部症狀-3',
                template=ButtonsTemplate(                                                
                        title='其他部位症狀選單',
                        text='請選擇您目前有的身體症狀群，如下:',
                        actions=[
                            MessageTemplateAction(
                                label='發燒/咳嗽有痰',
                                text='U10'
                            ),
                            MessageTemplateAction(
                                label='血壓高/暈倒/心悸',
                                text='U11'
                            ),                                
                                                                                                                                 
                        ]
                  )
            )            
            line_bot_api.push_message(uid, sym_message)  
#----------------------------------------------------------------------------            
        elif  user_message.find('U3') != -1:
            s1='U3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[U3:活動不良/身體部位萎縮]。'+ line_mark +'建議看診科別:[骨科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U4') != -1:
            s1='U4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[U4:身體部位部位變形/疼痛/無力]。'+ line_mark +'建議看診科別:[骨科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科A'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U5') != -1:
            s1='U5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[U5:心悸/雙手抖動/眼凸/口渴/多吃]。'+ line_mark +'建議看診科別:[內分泌科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號內分泌科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)  
        elif  user_message.find('U6') != -1:
            s1='U6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[U6:頸部變形/疼痛/麻木]。'+ line_mark +'建議看診科別:[骨科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科A'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U7') != -1:
            s2='U7'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[U1:上腹部疼痛]、\n[U7:黃疸]。'+ line_mark +'建議看診科別:[肝膽胰內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號肝膽胰內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)    
        elif  user_message.find('U8') != -1:
            s2='U8'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[U1:上腹部疼痛]、\n[U8:下腹部痛/腹瀉/便秘/嘔吐]。'+ line_mark +'建議看診科別:[胃腸內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)    
        elif  user_message.find('U9') != -1:
            s2='U9'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[U1:上腹部疼痛]、\n[U9:腹脹/胸口灼熱/黑便或血便]。'+ line_mark +'建議看診科別:[胃腸內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message.find('U10') != -1:
            s2='U10'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[U2:胸痛/胸悶/喘/咳嗽]、\n[U10:發燒/咳嗽有痰]。'+ line_mark +'建議看診科別:[胸腔內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胸腔內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U11') != -1:
            s2='U11'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[U2:胸痛/胸悶/喘/咳嗽]、\n[U11:血壓高/暈倒/心悸]。'+ line_mark +'建議看診科別:[心臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)               
############################### 下腹部症狀 ###################################
        elif  user_message.find('下腹部症狀') != -1:
            sym_message = TemplateSendMessage(
                alt_text='下腹部症狀',
                template=CarouselTemplate(
                    columns=[
    # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='下腹部症狀選單-1/2',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='下腹部疼痛/腹瀉/便秘',
                                    text='L1'
                                ),
                                MessageTemplateAction(
                                    label='泡泡尿/尿量減少',
                                    text='L2'
                                ),
                               MessageTemplateAction(
                                    label='陰道搔癢/分泌物多/陰道出血/經血過多',
                                    text='L3'
                                )                            
                            ]
                        ),
    # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='上腹部症狀選單-2/2',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='腰痛下背痛/血尿/頻尿/小便疼痛',
                                    text='L4'
                                ),
                                MessageTemplateAction(
                                    label='活動不良/萎縮變形/疼痛無力',
                                    text='L5'
                                ),
                               MessageTemplateAction(
                                    label='下腹部痠痛麻/無力/緊繃',
                                    text='L6'
                                )                            
                            ]
                        ),                        
   #----------------------------------------------------------------------------                 
                    ]
                )
            )            
            line_bot_api.reply_message(event.reply_token,sym_message) 
#----------------------------------------------------------------------------            
        elif  user_message =='L1':
            s1='L1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[L1:下腹部疼痛/腹瀉/便秘]。'+ line_mark +'建議看診科別:[胃腸內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L2':
            s1='L2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[L2:泡泡尿/尿量減少]。'+ line_mark +'建議看診科別:[腎臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腎臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L3':
            s1='L3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[L3:陰道搔癢/分泌物多/陰道出血/經血過多]。'+ line_mark +'建議看診科別:[婦產科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號婦產科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L4':
            s1='L4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[L4:腰痛下背痛/血尿/頻尿/小便疼痛]。'+ line_mark +'建議看診科別:[泌尿科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號泌尿科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='L5':
            s1='L5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[L5:活動不良/萎縮變形/疼痛無力]。'+ line_mark +'建議看診科別:[骨科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科A'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L6':
            s1='L6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[L6:下腹部痠痛麻/無力/緊繃]。'+ line_mark +'建議看診科別:[復健科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號復健科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)              

############################### 四肢症狀 ###################################
        elif  user_message.find('四肢症狀') != -1:
            sym_message = TemplateSendMessage(
                alt_text='四肢症狀',
                template = ButtonsTemplate(                                               
                            title='四肢症狀選單',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='小腿水腫/腳腫',
                                    text='LB1'
                                ),
                                MessageTemplateAction(
                                    label='行走困難/麻痺無力/痠痛',
                                    text='LB2'
                                ),                                                            
                                MessageTemplateAction(
                                    label='四肢痠痛麻/無力/緊繃',
                                    text='LB3'
                                ),
                                MessageTemplateAction(
                                    label='指甲問題',
                                    text='LB4'
                                ),                                                          
                            ]
                        )                        
                    
                )    
            line_bot_api.reply_message(event.reply_token,sym_message) 
   #--------------------------------------------------------------------------         
        elif  user_message=='LB1':
            s1='LB1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='先前已選四肢症狀:[小腿水腫/腳腫]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))            
            sym_message = TemplateSendMessage(
                alt_text='四肢症狀-2',
                template = ButtonsTemplate(                                               
                            title='四肢症狀-2選單',
                            text='請選擇您其他的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='血壓高/暈倒',
                                    text='LB5'
                                ),
                                MessageTemplateAction(
                                    label='心悸胸痛/胸悶/喘/咳嗽',
                                    text='LB6'
                                ),                                                            
                                MessageTemplateAction(
                                    label='全身水腫/泡泡尿/尿量減少',
                                    text='LB7'
                                ),
                                                                                         
                            ]
                        )                                            
                )                 
            line_bot_api.push_message(uid, sym_message)
            
#----------------------------------------------------------------------------            
        elif  user_message =='LB2':
            s1='LB2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[LB2:行走困難/麻痺無力/痠痛]。'+ line_mark +'建議看診科別:[神經內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號神經內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='LB3':
            s1='LB3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[LB3:四肢痠痛麻/無力/緊繃]。'+ line_mark +'建議看診科別:[神經內科/復健科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            reg_info = TemplateSendMessage(
                alt_text='看診建議掛號科別:',
                template = ButtonsTemplate(                    
                    title='看診建議掛號科別:',
                    text= '[神經內科/復健科]',
                    actions= [
                        MessageTemplateAction(
                            label= '掛號神經內科',
                            text='掛號神經內科'
                            ),
                        MessageTemplateAction(
                            label= '掛號復健科',
                            text='掛號復健科'
                            ),
                        MessageTemplateAction(
                            label= '繼續使用看診建議',
                            text= '看診建議'
                            ),
                        MessageTemplateAction(
                            label= '離開看診建議',
                            text= '離開看診'
                            )
                        
                    ]
                )
            )
            line_bot_api.push_message(uid, reg_info)
            #rig_dept='掛號復健科'
            #Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='LB4':
            s1='LB4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[LB4:指甲問題]。'+ line_mark +'建議看診科別:[皮膚科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)              
        elif  user_message =='LB5':
            s2='LB5'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[LB1:小腿水腫/腳腫]、\n[LB5:血壓高/暈倒]。'+ line_mark +'建議看診科別:[心臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)   
        elif  user_message =='LB6':
            s2='LB6'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[LB1:小腿水腫/腳腫]、\n[LB6:心悸胸痛/胸悶/喘/咳嗽]。'+ line_mark +'建議看診科別:[心臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='LB7':
            s2='LB7'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[LB1:小腿水腫/腳腫]、\n[LB7:全身水腫/泡泡尿/尿量減少]。'+ line_mark +'建議看診科別:[腎臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腎臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)               
##############################################################################
        elif  user_message.find('全身皮膚症狀') != -1:
            sym_message = TemplateSendMessage(
                alt_text='全身症狀',
                template=CarouselTemplate(
                    columns=[
    # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='全身姓症狀選單-1/3',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='發燒',
                                    text='A1'
                                ),
                                MessageTemplateAction(
                                    label='全身水腫/泡泡尿/尿量減少',
                                    text='A2'
                                ),
                               MessageTemplateAction(
                                    label='容易緊張/流汗/失眠',
                                    text='A3'
                                )                            
                            ]
                        ),
 # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='全身姓症狀選單-2/3',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='失眠/焦慮/恐慌/生氣',
                                    text='A4'
                                ),
                                MessageTemplateAction(
                                    label='青春痘/皮膚黑斑/免疫系統疾病',
                                    text='A5'
                                ),
                               MessageTemplateAction(
                                    label='皮膚傷口/皮膚癢/紅腫/緊繃',
                                    text='A6'
                                )                            
                            ]
                        ),
 # -----------------------------------------------------------------------------                    
                        CarouselColumn(                            
                            title='全身姓症狀選單-3/3',
                            text='請選擇您目前有的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='血壓高/暈倒',
                                    text='A7'
                                ),
                                MessageTemplateAction(
                                    label='黃疸',
                                    text='A8'
                                ),
                               MessageTemplateAction(
                                    label='身體痠痛麻/無力/緊繃',
                                    text='A9'
                                )                            
                            ]
                        ),                        
   #----------------------------------------------------------------------------                 
                    ]
                )
            )            
            line_bot_api.reply_message(event.reply_token,sym_message)            
#-----------------------------------------------------------------------------            
        elif  user_message=='A1':
            s1='A1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='先前已選全身症狀:[發燒]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))            
            sym_message = TemplateSendMessage(
                alt_text='全身症狀-2',
                template = ButtonsTemplate(                                               
                            title='全身症狀-2選單',
                            text='請選擇您其他的身體症狀群，如下:',
                            actions=[
                                MessageTemplateAction(
                                    label='胸痛悶/喘鳴聲/咳嗽有痰',
                                    text='A10'
                                ),
                                MessageTemplateAction(
                                    label='頭痛/紅疹/肌肉痠痛/關節痛',
                                    text='A11'
                                ),                                                            
                                MessageTemplateAction(
                                    label='頭痛暈/耳鳴/鼻涕/喉嚨痛',
                                    text='A12'
                                ),
                                                                                         
                            ]
                        )                                            
                )                 
            line_bot_api.push_message(uid, sym_message) 
#-----------------------------------------------------------------------------            
        elif  user_message =='A2':
            s1='A2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A2:全身水腫/泡泡尿/尿量減少]。'+ line_mark +'建議看診科別:[腎臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腎臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A3':
            s1='A3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A3:容易緊張/流汗/失眠]。'+ line_mark +'建議看診科別:[內分泌科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號內分泌科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A4':
            s1='A4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A4:失眠/焦慮/恐慌/生氣]。'+ line_mark +'建議看診科別:[精神科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號精神科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)  
        elif  user_message =='A5':
            s1='A5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A5:青春痘/皮膚黑斑/免疫系統疾病]。'+ line_mark +'建議看診科別:[皮膚科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A6':
            s1='A6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A6:皮膚傷口/皮膚癢/紅腫/緊繃]。'+ line_mark +'建議看診科別:[皮膚科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A7':
            s1='A7'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A7:血壓高/暈倒]。'+ line_mark +'建議看診科別:[心臟內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A8':
            s1='A8'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A8:黃疸]。'+ line_mark +'建議看診科別:[肝膽胰內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號肝膽胰內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A9':
            s1='A9'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='您先前已選症狀:\n[A9:身體痠痛麻/無力/緊繃]。'+ line_mark +'建議看診科別:[復健科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號復健科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A10':
            s2='A10'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[A1:發燒]、\n[A10:胸痛悶/喘鳴聲/咳嗽有痰]。'+ line_mark +'建議看診科別:[胸腔內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胸腔內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A11':
            s2='A11'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[A1:發燒]、\n[A11:頭痛/紅疹/肌肉痠痛/關節痛]。'+ line_mark +'建議看診科別:[感染內科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胸腔內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A12':
            s2='A12'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='您先前已選症狀:\n[A1:發燒]、\n[A12:頭痛暈/耳鳴/鼻涕/喉嚨痛]。'+ line_mark +'建議看診科別:[耳鼻喉科]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)             
##############################################################################

############################### 看診建議掛號推薦 ###############################            
        elif  user_message.find('掛號') != -1 and user_message.find('科') != -1 :
            if user_message.find('心臟內科') != -1:
                Clinic_Dept.Car(uid)
            elif user_message.find('肝膽胰內科') != -1:
                Clinic_Dept.Hep(uid)
            elif user_message.find('胃腸內科') != -1:
                Clinic_Dept.Gas(uid)
            elif user_message.find('胸腔內科') != -1:
                Clinic_Dept.Tho(uid)
            elif user_message.find('腎臟內科') != -1:
                Clinic_Dept.Nep(uid)
            elif user_message.find('感染內科') != -1:
                Clinic_Dept.Inf(uid)
            elif user_message.find('內分泌科') != -1:
                Clinic_Dept.End(uid)
            elif user_message.find('神經內科') != -1:
                Clinic_Dept.Neu(uid)
            elif user_message.find('婦產科') != -1:
                Clinic_Dept.Obs(uid)    
            elif user_message.find('眼科') != -1:
                Clinic_Dept.Oph(uid)
            elif user_message.find('耳鼻喉科') != -1:
                Clinic_Dept.Oto(uid)
            elif user_message.find('骨科') != -1:
                Clinic_Dept.Ort(uid) 
            elif user_message.find('泌尿科') != -1:
                Clinic_Dept.Uro(uid)  
            elif user_message.find('皮膚科') != -1:
                Clinic_Dept.Der(uid)
            elif user_message.find('精神科') != -1:
                Clinic_Dept.Psy(uid) 
            elif user_message.find('牙科一診') != -1:
                Clinic_Dept.Den(uid)
            elif user_message.find('復健科') != -1:
                Clinic_Dept.Reh(uid) 
            elif user_message.find('腦神經外科') != -1:
                Clinic_Dept.NeuSur(uid)
            else:
                Response_info='找不到您要掛號的科別! >_<'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
                Confirm_Dig.Ask(uid)                
        else:
            Response_info='無法了解您所選的的症狀，您目前處於[看診建議]功能中!，繼續使用或是離開此功能?'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
            Confirm_Dig.Ask(uid)
                    
        return 0

############################# 導航附近醫院模式 #############################
    if work_mode[0] == 'M':
        # -----------------------# 取消導航功能-----------------------
        if user_message.find('離開搜尋') != -1 or user_message.find('取消搜尋') != -1 or user_message.find('Quit') != -1 or user_message.find('quit') != -1:
            lang = '中'
            KMSH_UserDB_Con.dis_trmode(uid, lang)
            Response_info = '好的!取消醫院搜尋功能!'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))
        # user_message='我要翻譯韓語' user_message='我要波斯語翻譯'    #user_message='翻譯馬來西亞語' user_message='翻譯羅馬尼亞語'
        # ----------------------變更翻譯語言種類--------------------------
        elif user_message.find("醫院搜尋") != -1:
            Response_info = Quick_text()
            line_bot_api.reply_message(event.reply_token, Response_info)

        elif user_message.find('我的醫院') != -1:
            my_Hospital = KMSH_UserDB_Con.read_my_Hospital(uid)
            Response_info = reply_Hospital(my_Hospital)
            line_bot_api.reply_message(event.reply_token, Response_info)

        elif user_message.find('07') != -1:
            Response_info = '請點擊號碼撥號'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))

        else:
            Response_info = '您目前處於[醫院搜尋]功能中!，繼續使用或是離開此功能?'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))
            Confirm_Dig.Sit(uid)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))

#################################### 一般查詢狀態 ##############################
##     user_message='離開看診'    
    elif user_message.find('離開看診') !=-1:
        
        Response_info='您已經離開[看診建議]的功能!可以使用其他功能喔!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
    elif user_message.find('取消看診') !=-1:
        
        Response_info='您已經離開[看診建議]的功能!可以使用其他功能喔!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))    
         
    elif user_message.find('看診建議') !=-1:
        lang ='中'
        KMSH_UserDB_Con.set_trmode_d(uid,lang)
        
        Response_info='您已經進入[看診建議]的功能!\n若要離開此功能，請您輸入[離開看診建議]或是[取消看診建議]的文字命令喔!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
        
        diagnosis_message = TemplateSendMessage(
            alt_text='看診建議功能',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        #image_aspect_ratio='square',
                        #imageSize='contain',
                        #thumbnail_image_url='',
                        title='看診建議功能，選單Ｉ',
                        text='請選擇您現在有不舒服狀況的身體部位，如下選單:',
                        actions=[
                            MessageTemplateAction(
                                label='頭部',
                                text='頭部症狀'
                            ),
                            MessageTemplateAction(
                                label='頸部',
                                text='頸部症狀'
                            ),
                            MessageTemplateAction(
                                label='手腳四肢',
                                text='四肢症狀'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        #image_aspect_ratio='square',
                        #imageSize='contain',
                        #thumbnail_image_url='',
                        title='看診建議功能，選單ＩＩ',
                        text='請選擇您現在有不舒服狀況的身體部位，如下選單:',
                        actions=[
                            MessageTemplateAction(
                                label='上腹部',
                                text='上腹部症狀'
                            ),
                            MessageTemplateAction(
                                label='下腹部',
                                text='下腹部症狀'
                            ),
                            MessageTemplateAction(
                                label='全身/皮膚',
                                text='全身皮膚症狀'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        
        
        imagemap_message = ImagemapSendMessage(
            base_url='https://lh3.googleusercontent.com/K8i-XYfunqUI_vPB1kM3piCg1G0oh3aOEMo34zOg3v0a1pUDqKfllfQiP1bIPCaWhmxb8J0sb3daOBnmjY-g7pyEqSOvqhXL9oSz3CzAiF_CLBNYCrFtNgbo6zSL1UUxylwStMWShg=w1040#',
            alt_text=' imagemap',
            base_size=BaseSize(height=1040, width=1040),
               actions=[
                MessageImagemapAction (
                    text='頭部症狀',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=320
                    )
                ),
                MessageImagemapAction (
                    text='頸部症狀',
                    area=ImagemapArea(
                        x=0, y=320, width=520, height=260
                    )
                ),
                MessageImagemapAction (
                    text='四肢症狀',
                    area=ImagemapArea(
                        x=0, y=580, width=520, height=460
                    )
                ),
                MessageImagemapAction(
                    text='全身皮膚症狀',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='上腹部症狀',
                    area=ImagemapArea(
                        x=520, y=320, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='下腹部症狀',
                    area=ImagemapArea(
                        x=520, y=640, width=520, height=400
                    )
                ),
        
            ]
        )
        #line_bot_api.push_message(uid, diagnosis_message)
        line_bot_api.push_message(uid, imagemap_message)                                        
        return 0
###################################################################################    
  # user_message='我要翻譯韓語' user_message='我要馬來西亞語翻譯'    #user_message='翻譯亞語'       
    elif user_message.find('外語選單') != -1:
#         lang_menu = TemplateSendMessage(
#             alt_text='外語翻譯選單',
#             template=CarouselTemplate(
#                 columns=[
#                     CarouselColumn(
# #                        thumbnail_image_url='  ',
#                         title='外語翻譯選單-1/4',
#                         text='亞洲語系翻譯',
#                         actions=[
#                             MessageTemplateAction(
#                                 label='英(美)語',
#                                 text='翻譯英語'
#                             ),
#                             MessageTemplateAction(
#                                 label='日語',
#                                 text='翻譯日語'
#                             ),
#                             MessageTemplateAction(
#                                 label='韓語',
#                                 text='翻譯韓語'
#                             )                            
#                         ]
#                     ),        
# #------------------------------------------------------------------------------                    
#                     CarouselColumn(
# #                        thumbnail_image_url='   ',
#                         title='外語翻譯選單-2/4',
#                         text='歐洲語系翻譯',
#                         actions=[
#                             MessageTemplateAction(
#                                 label='西班牙語',
#                                 text='翻譯西班牙語'
#                             ),
#                             MessageTemplateAction(
#                                 label='法語',
#                                 text='翻譯法語'
#                             ),
#                             MessageTemplateAction(
#                                 label='德語',
#                                 text='翻譯德語'
#                             )                            
#                         ]
#                     ),
                    
# # -----------------------------------------------------------------------------
#                     CarouselColumn(
# #                        thumbnail_image_url='   ',
#                         title='外語翻譯選單-3/4',
#                         text='亞洲語系翻譯',
#                         actions=[
#                             MessageTemplateAction(
#                                 label='越南語',
#                                 text='翻譯越南語'
#                             ),
#                             MessageTemplateAction(
#                                 label='馬來西亞語',
#                                 text='翻譯馬來西亞語'
#                             ),
#                             MessageTemplateAction(
#                                 label='印尼語',
#                                 text='翻譯印尼語'
#                             )                            
#                         ]
#                     ), 
# #------------------------------------------------------------------------------                    
#                     CarouselColumn(
# #                        thumbnail_image_url='   ',
#                         title='外語翻譯選單-4/4',
#                         text='亞洲語系翻譯',
#                         actions=[
#                             MessageTemplateAction(
#                                 label='泰語',
#                                 text='翻譯泰語'
#                             ),
#                             MessageTemplateAction(
#                                 label='印度語',
#                                 text='翻譯印度語'
#                             ),
#                             MessageTemplateAction(
#                                 label='阿拉伯語',
#                                 text='翻譯阿拉伯語'
#                             )                            
#                         ]
#                     ), 
# #------------------------------------------------------------------------------                    
#                 ]
#             )
#         )         # 結束MESSAGE-TemplateSendMessage  
        lang_menu = TemplateSendMessage(
            alt_text='外語翻譯選單',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/FtA-p01ZiAP1eA-8WOTFAlU793Q4smX7OgGxjD0svgWKR-3nmiIwADfRqSezAQSPlaHOHP0FHayqz2Hu2i1zlazGeC0GuPgqwq_-IZhb7pNRgv8Nk-ePBe7GSTdPcr-zsS9mHaG6NQ=w600',
                        title='外語翻譯選單-1/10',
                        text='亞洲語系翻譯(1/4)',
                        actions=[
                            MessageTemplateAction(
                                label='英(美)語',
                                text='翻譯英語'
                            ),
                            MessageTemplateAction(
                                label='日語',
                                text='翻譯日語'
                            ),
                            MessageTemplateAction(
                                label='韓語',
                                text='翻譯韓語'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/FKSRSGWwJttJXxWqGVQh1NK_B6Y0coj7zjIsfBw2zCLOXqyCoJdEc3p1QfrslhUH_vLJAch9duWwh_4qSJ2rQzYzMXVGqIp9RKmfdUVLTtNhhKwAtBDUw_m6hJthgssXy8mqYY9BvQ=w600',
                        title='外語翻譯選單-2/10',
                        text='亞洲語系翻譯(2/4)',
                        actions=[
                            MessageTemplateAction(
                                label='越南語',
                                text='翻譯越南語'
                            ),
                            MessageTemplateAction(
                                label='馬來西亞語',
                                text='翻譯馬來西亞語'
                            ),
                            MessageTemplateAction(
                                label='印尼語',
                                text='翻譯印尼語'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/ii9yNKlFFIHKc8JS3Lp0xJJbbFVZxF-IIXAo9UgaUXBMzgmu2eR57Q8yfroKg084mRd-ooBLjvxwBeZRVdYRIDNqm6gW2bDOyUFVT6zD9h4GOu0lMjux1QfeGiUblBNs1Lahwffjjw=w6000',
                        title='外語翻譯選單-3/10',
                        text='亞洲語系翻譯(3/4)',
                        actions=[
                            MessageTemplateAction(
                                label='泰語',
                                text='翻譯泰語'
                            ),
                            MessageTemplateAction(
                                label='印度語',
                                text='翻譯印度語'
                            ),
                            MessageTemplateAction(
                                label='阿拉伯語',
                                text='翻譯阿拉伯語'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/Dg7oaQ7DqWg9VKjb0jlIJIoEeWXsxMnj5LBUU_Go3kyf2M64LYYjtKW03hTiibqyvhX-GO-ApNWR0M_4htARzptPyNBKvreuxwaP_4yt2xsc_-jD7mbd-J_vXBDjxDV4leZLMuujeQ=w600',
                        title='外語翻譯選單-4/10',
                        text='亞洲語系翻譯(4/4)',
                        actions=[
                            MessageTemplateAction(
                                label='希伯來語(以色列)',
                                text='翻譯希伯來語'
                            ),
                            MessageTemplateAction(
                                label='土耳其語',
                                text='翻譯土耳其語'
                            ),
                            MessageTemplateAction(
                                label='保加利亞',
                                text='翻譯保加利亞'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/lYYC3KONJ-r8MPuO6NlR92JQocBqioz6d4L_IJMfcWVuZ54IT4jnOGrRB4Nbfm-B-eolh5ijP7tuJCIdPprH3VGf_6zcuDyWrWJGqS5maLxdyyRLaOy3TcKoOlDc3mSE3g599ANr2Q=w600',
                        title='外語翻譯選單-5/10',
                        text='歐洲語系翻譯(1/6)',
                        actions=[
                            MessageTemplateAction(
                                label='英(美)語',
                                text='翻譯英語'
                            ),
                            MessageTemplateAction(
                                label='法語',
                                text='翻譯法語'
                            ),
                            MessageTemplateAction(
                                label='德語',
                                text='翻譯德語'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/EboLBmHXVpQlk3hrpdHZlLEzjnGGAvjuCGsI32si5ekjX-t6CcUWe6AX1o0lElKvj4pfKLINxMKDzaWFFjliDHMzgTk35M1ShkRlT0S8CrUctVVAHC51Y0zFgVlmRMcdp_U4lC8kgw=w600',
                        title='外語翻譯選單-6/10',
                        text='歐洲語系翻譯(2/6)',
                        actions=[
                            MessageTemplateAction(
                                label='西班牙語',
                                text='翻譯西班牙語'
                            ),
                            MessageTemplateAction(
                                label='葡萄牙語',
                                text='翻譯葡萄牙語'
                            ),
                            MessageTemplateAction(
                                label='葡萄牙語(巴西)',
                                text='翻譯巴西語'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/_rparADUnbJJnpb65H7ayhR1AGVm3NWNbDBZiyjnnzxZP6kgvWe4Umhbom9n4ux9IqLJw4f11FTNuSqiWEtGgUvCpPKztQPqWHVPdRJw3QuLfT7eDEo6oFNZCRES9HCeVESSGC3Dpw=w600',
                        title='外語翻譯選單-7/10',
                        text='歐洲語系翻譯(3/6)',
                        actions=[
                            MessageTemplateAction(
                                label='義大利語',
                                text='翻譯義大利語'
                            ),
                            MessageTemplateAction(
                                label='希臘語',
                                text='翻譯希臘語'
                            ),
                            MessageTemplateAction(
                                label='匈牙利語',
                                text='翻譯匈牙利語'
                            )                            
                        ]
                    ),                        
 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/5ihsLofivptsynCymdVOH4mVJSU_BVkkCV3G9FuDVRbB-94f11bxTYiWJ9FinDcFkuHZbfgaPbdDEwaprd9eLsoZWV6i6er0zklomk035VXUwke0mCjtK2Ljm6pBd_1YRx3vkvvQ_A=w600',
                        title='外語翻譯選單-8/10',
                        text='歐洲語系翻譯(4/6)',
                        actions=[
                            MessageTemplateAction(
                                label='波蘭語',
                                text='翻譯波蘭語'
                            ),
                            MessageTemplateAction(
                                label='丹麥語',
                                text='翻譯丹麥語'
                            ),
                            MessageTemplateAction(
                                label='荷蘭語',
                                text='翻譯荷蘭語'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/-2lYj7IxjNABSjyP-YhmFakXpuWuI-1sxc6Bms2vH2qHXcLs6nM_OTW9caDURCwcteDgP72jn-naFj074hyP5GvLXWXRekkPwAZDfIaNyP76QjOz7a96i90WrZy93BExUFEOOQxjgA=w600',
                        title='外語翻譯選單-9/10',
                        text='歐洲語系翻譯(5/6)',
                        actions=[
                            MessageTemplateAction(
                                label='瑞典語',
                                text='翻譯瑞典語'
                            ),
                            MessageTemplateAction(
                                label='芬蘭語',
                                text='翻譯芬蘭語'
                            ),
                            MessageTemplateAction(
                                label='挪威語',
                                text='翻譯挪威語'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/ixYCUmAcRByFRZtPSmljEScE3rFss1BqiflLUUX4UHqHwOTlIuzREIG3WzH2D-ltmWgxUnnaKL7urxLOngzoPcXxmiUKrDBOiTMJtnybrsJQuifwY84YitAFrA1RfOoQ-V5x0GRTFw=w600',
                        title='外語翻譯選單-10/10',
                        text='歐洲語系翻譯(6/6)',
                        actions=[
                            MessageTemplateAction(
                                label='俄羅斯語',
                                text='翻譯俄羅斯語'
                            ),
                            MessageTemplateAction(
                                label='捷克語',
                                text='翻譯捷克語'
                            ),
                            MessageTemplateAction(
                                label='羅馬尼亞語',
                                text='翻譯羅馬尼亞語'
                            )                            
                        ]
                    )  
#------------------------------------------------------------------------------                    
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage        

        line_bot_api.reply_message(event.reply_token,lang_menu)
        # line_bot_api.push_message(uid, care_message)        
        return 0
    

############################## 使用者設定中文翻譯成外語模式 ######################         
    elif user_message.find('翻譯') !=-1:                        
          
        work_mode = KMSH_UserDB_Con.get_trmode(uid)
        
        #----------------提供可翻譯語種檢查與語種編碼--------------------------import Lang_Check               
        if work_mode[2]=='Y':  #判斷是否有權限進行翻譯
            user_message=user_message.lstrip()
            lang_code = Lang_Check.getcode(user_message)
            lang_name = Lang_Check.getname(lang_code)        
                    
            #----------------------進行使用者翻譯模式設定----------------------------
            if len(lang_code)>0 : # 資料庫有想要翻譯的這種語言            
                KMSH_UserDB_Con.set_trmode(uid,lang_code)                 
                Response_info='(1)好的，['+ lang_name + '翻譯]功能啟動!之後您所輸入的文字將會翻譯成'+ lang_name +'\n(2)若要停止翻譯，請下[取消翻譯功能]、[Quit]、[quit]的文字命令!!\n(3)翻譯語音的合成要等耐心一下喔!大約需要6~8秒左右!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
            else:
                Response_info='沒有您要求的語言翻譯功能!我只有外語選單中的30種語言的翻譯!'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
        else:
             Response_info='您沒有語言翻譯功能的權限!!! >_< 請您與資訊室聯繫。'
             line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
        return 0
#----------------------------其他語言(英)翻成中文模組-------------------------        
    # user_message=' translation I want to say i am very smart'    
    elif user_message.find('translation') !=-1 or user_message.find('Translation') !=-1 :                 
        lang='en'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)         
        Response_info ='<1>You are now in the [translation] function! Anything you say in the InfoBot will be translated to Chinese.\n<2> To exit this [translation] function, please enter [quit] or [Quit]!\n'
        Response_info2='<3>The InfoBot provides Chinese translation in popular 53 languages around the world.\n<4>Please wait a few seconds (6-8) for receiving the voice translation file!'
        line_bot_api.push_message(uid, TextSendMessage(Response_info + Response_info2))       
        return 0         
            
#---------------------其他語言(日文)翻成中文模組-------------------------    
    # user_message='翻訳熱はありますか。'
    elif user_message.find('翻訳') !=-1: 
        lang='ja'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='これで[翻訳]関数に入りました！ この機能を終了するには、英語の単語[quit]または[Quit]を入力してください'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))       
        return 0        
#---------------------其他語言(韓文)翻成中文模組-------------------------
      # user_message='몸에 열이 있니?'   
    elif user_message.find('번역') !=-1:  
        lang='ko'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='이제 [번역] 기능에 있습니다! 이 기능을 종료하려면 영어 단어 [quit] 또는 [Quit]을 입력하십시오.'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))       
        return 0        
#---------------------其他語言(印尼文)翻成中文模組-------------------------    
    # user_message='Apakah kamu demam? '
    elif user_message.find('terjemahan') !=-1 or user_message.find('Terjemahan') !=-1:         
        lang='id'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='Anda sekarang dalam fungsi [terjemahan]! Untuk keluar dari fungsi ini, masukkan kata-kata dalam bahasa Inggris [quit] atau [Quit]'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))        
        return 0
 #---------------------其他語言(馬來西亞)翻成中文模組-------------------------         
    elif user_message.find('terjemahan') !=-1 or user_message.find('Terjemahan') !=-1:    
        lang='ms'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='Anda kini berada dalam fungsi [terjemahan]! Untuk menghentikan fungsi ini, sila masukkan perkataan Bahasa Inggeris [quit] atau [Quit]' 
        line_bot_api.push_message(uid, TextSendMessage(Response_info))   
        return 0
#---------------------其他語言(泰文)翻成中文模組-------------------------    
    # user_message=' แปลคุณมีไข้ไหม? '
    elif user_message.find('แปล') !=-1:         
        lang='th'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='ตอนนี้คุณอยู่ในฟังก์ชัน [แปล]! หากต้องการออกจากฟังก์ชันนี้โปรดป้อนคำภาษาอังกฤษ [quit] หรือ [Quit]'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))        
        return 0        
#---------------------其他語言(越南文)翻成中文模組-------------------------    
     # user_message='Dịch Anh có sốt không? '
    elif user_message.find('Dịch') !=-1 or user_message.find('dịch') !=-1:        
        lang='vi'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='Bây giờ bạn đang ở trong chức năng [dịch]! Để thoát khỏi chức năng này, vui lòng nhập các từ tiếng Anh [quit] hoặc [Quit]'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))        
        return 0 
#---------------------其他語言(菲律賓)翻成中文模組------------------------- 
     # user_message='May lagnat ka ba?'        
    elif user_message.find('pagsasalin') !=-1 or user_message.find('Pagsasalin') !=-1:        
        lang='fil'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='Nasa function ka na ngayon ng [pagsasalin]! Upang umalis sa pagpapaandar na ito, mangyaring maglagay ng mga salitang Ingles [quit] o [Quit]'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))        
        return 0        
#---------------------其他語言(法文)翻成中文模組-------------------------    
     # user_message='  je suis très intelligent '
    elif user_message.find('Traduction') !=-1 or user_message.find('traduction') !=-1 : 
        lang='fr'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='Vous êtes maintenant dans la fonction [traduction]! Pour quitter cette fonction, veuillez saisir les mots anglais [quit] ou [Quit]'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))        
        return 0        
#---------------------其他語言(德文)翻成中文模組-------------------------    
     # user_message=' ich bin sehr schlau '
    elif user_message.find('Übersetzung') !=-1 or user_message.find('übersetzen') !=-1:    
        lang='de'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='Sie befinden sich jetzt in der Funktion [Übersetzung]! Um diese Funktion zu beenden, geben Sie bitte die englischen Wörter [quit] oder [Quit] ein.'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))        
        return 0 
#---------------------其他語言(西班牙文)翻成中文模組-------------------------    
     # user_message='  soy inteligente '
    elif user_message.find('Traducción') !=-1 or user_message.find('traducción') !=-1:    
        lang='es'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='¡Ahora estás en la función [traducción]! Para salir de esta función, ingrese las palabras en inglés [quit] o [Quit]'
        line_bot_api.push_message(uid, TextSendMessage(Response_info))   
        return 0  
#---------------------其他語言(印度)翻成中文模組------------------------- 
     # user_message=' मैं बहुत चालाक हूँ '    
    elif user_message.find('अनुवाद') !=-1:    
        lang='hi'
        KMSH_UserDB_Con.set_trmode_r(uid,lang)        
        Response_info='अब आप [अनुवाद] समारोह में हैं! इस फ़ंक्शन को छोड़ने के लिए, कृपया अंग्रेजी शब्दों को छोड़ें [quit] या [Quit]' 
        line_bot_api.push_message(uid, TextSendMessage(Response_info))   
        return 0

############################## 使用者設定導航模式 ######################
    elif user_message.find('醫院搜尋') != -1:
        lang = '中'
        KMSH_UserDB_Con.set_trmode_m(uid, lang)

        Response_info = '您已經進入[醫院搜尋]的功能!\n若要離開此功能，請您輸入[離開醫院搜尋]或是[取消醫院搜尋]的文字命令喔!'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))
        Response_Quick = Quick_text()
        line_bot_api.push_message(uid, Response_Quick)

############################## 顯示使用者所儲存的醫院 ######################
    elif user_message.find('我的醫院') != -1:
        my_Hospital = KMSH_UserDB_Con.read_my_Hospital(uid)
        Response_info = reply_Hospital(my_Hospital)

        line_bot_api.reply_message(event.reply_token,Response_info)

#-------------- 加入或刪除使用者儲存的醫院 -----------------------------------------
        @handler.add(PostbackEvent)
        def handle_postback(event):
            if "action=add" in event.postback.data:
                data = event.postback.data.split(",")
                hs_Name = data[2]
                current_db_type = data[1]
                message = KMSH_UserDB_Con.add_my_Hospital(uid, hs_Name, current_db_type)

                line_bot_api.reply_message(
                    event.reply_token,
                    message)

            if "action=del" in event.postback.data:
                data = event.postback.data.split(",")
                hs_Name = data[1]
                message = KMSH_UserDB_Con.del_my_Hospital(uid, hs_Name)

                line_bot_api.reply_message(
                    event.reply_token,
                    message)

############################## 連結到衛生福利部疾病管制署 ######################
    elif user_message.find('台灣疫情') != -1:
        Flu_message = TemplateSendMessage(
            alt_text='台灣疫情',
            template=ButtonsTemplate(
                title='衛生福利部疾病管制署網站',
                text='查詢疫情近況和相關公告，請按以下連結查詢',
                actions=[
                    URITemplateAction(
                        label='進入網站',
                        uri="https://www.cdc.gov.tw/"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,Flu_message)

#################################################################################
#             病歷申請選單
#################################################################################
    elif user_message.find('病歷申請選單') != -1:
        apply_message = TemplateSendMessage(
            alt_text='病歷申請入口',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='小港醫院病歷申請-1/2',
                        text='病歷申請，請按以下連結',
                        actions=[
                            URITemplateAction(
                                label='各類病歷複製申請說明(含影像光碟)',
                                uri='https://www.kmsh.org.tw/rem/hisstepby.asp'
                            ),
                            URITemplateAction(
                                label='申請表單下載(Word檔)',
                                uri='https://drive.google.com/file/d/1wd81O6NTCSmQZmzK_uvJWzDO_h1WPori/view?usp=sharing'
                            ),
                            URITemplateAction(
                                label='申請進度網路查詢',
                                uri='http://www.kmhk.org.tw/Chart_Copy/Status_S.aspx'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='小港醫院病歷申請-2/2',
                        text='病歷網路申請，請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='病歷網路申請作業流程說明',
                                uri='http://www.kmhk.org.tw/Chart_Copy/intro.aspx'
                            ),
                            URITemplateAction(
                                label='病歷網路申請入口',
                                uri='http://www.kmhk.org.tw/Chart_Copy/index.aspx'
                            ),
                            URITemplateAction(
                                label='申請進度網路查詢',
                                uri='http://www.kmhk.org.tw/Chart_Copy/Status_S.aspx'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        #line_bot_api.push_message(uid, apply_message)
        line_bot_api.reply_message(event.reply_token,apply_message)
        return 0     
###############################################################################
#                  醫藥資訊入口選單   
##############################################################################        
    elif user_message.find('醫藥資訊選單') != -1:
        med_message = TemplateSendMessage(
            alt_text='醫藥資訊',
            template=CarouselTemplate(
                columns=[
# =============================================================================                    
                    CarouselColumn(
#                        image_aspect_ratio='square',
                        thumbnail_image_url='https://lh3.googleusercontent.com/I9z5HAxfxQ3HOUAc8fMjgBrbgEUgepmTqJ_jciMuZczTh7k9lrSA2a9bUyfiTLNpaUtkbTOHp7j0Hfm_7RVEl9i7rtQKAnyuh-l44NJliFxNGnG_pOCFKD3mMzsf6peKW_ELkN3nAg=w800',
                        title='衛福部疾管署(CDC)網站資訊',
                        text='相關防疫資訊，請按以下連結',
                        actions=[
                            URITemplateAction(
                                label='疾管署官方網站',
                                uri='https://www.cdc.gov.tw'
                            ),
                            URITemplateAction(
                                label='疾管署官方新聞稿',
                                uri='https://www.cdc.gov.tw/Bulletin/List/MmgtpeidAR5Ooai4-fgHzQ'
                            ),
                            URITemplateAction(
                                label='疾管署澄清專區',
                                uri='https://www.cdc.gov.tw/Bulletin/List/xpcl4W7tToptl-lFMjle2Q'
                            )
                        ]
                    ),
                # =============================================================================                    
                    CarouselColumn(
#                        image_aspect_ratio='square',
                        thumbnail_image_url='https://lh3.googleusercontent.com/I9z5HAxfxQ3HOUAc8fMjgBrbgEUgepmTqJ_jciMuZczTh7k9lrSA2a9bUyfiTLNpaUtkbTOHp7j0Hfm_7RVEl9i7rtQKAnyuh-l44NJliFxNGnG_pOCFKD3mMzsf6peKW_ELkN3nAg=w800',
                        title='領用藥查詢&病例申請系統',
                        text='領用藥查詢，請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='藥品查詢系統',
                                uri='https://www.kmsh.org.tw/web/DrugSearch/DrugSearch.aspx'
                            ),
                            URITemplateAction(
                                label='病人領用藥查詢系統',
                                uri='https://www.kmsh.org.tw/web/PickUpMedicineSearch/PickUpMedicineSearch.aspx'
                            ),
                            MessageTemplateAction(
                                label='病歷申請選單',
                                text='病歷申請選單'
                            )
                        ]
                    ),                        
# =============================================================================
                    CarouselColumn(
                     #   image_aspect_ratio='square',
                        thumbnail_image_url='https://lh3.googleusercontent.com/I9z5HAxfxQ3HOUAc8fMjgBrbgEUgepmTqJ_jciMuZczTh7k9lrSA2a9bUyfiTLNpaUtkbTOHp7j0Hfm_7RVEl9i7rtQKAnyuh-l44NJliFxNGnG_pOCFKD3mMzsf6peKW_ELkN3nAg=w800',
                        title='衛教資訊選單',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label= '文件衛教資訊',
                                text= '文件衛教'
                                ),
                            MessageTemplateAction(
                                label= '影片衛教資訊',
                                text= '影片衛教'
                                ),
                            MessageTemplateAction(
                                label= '特殊藥品使用衛教影片',
                                text= '特殊藥品使用衛教'
                                ),
                        ]
                    ),
# =============================================================================                    
                ]
            )
        )                    
                        
        line_bot_api.reply_message(event.reply_token, med_message)
        #line_bot_api.push_message(uid, med_message)
        return 0

#############################################################################
#                            文件衛教資訊      
#                 text 內容不可超過60字元，label內容不可超過20字元                       
#----------------------------------------------------------------------------
#                 ButtonsTemplate 的Actions 不可超過4個按鈕
#                 CarouselTemplate 的Actions 不可超過3個按鈕
############################## 一般照護 ####################################### 
    elif user_message.find('一般照護衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='一般照護衛教資訊',
            template=ButtonsTemplate(
#                        thumbnail_image_url='  ',
                        title='一般照護衛教資訊',
                        text='請按以下連結查詢',   # text 內容不可超過60字元，label內容不可超過20字元
                        actions=[
                            URITemplateAction(
                                label='保命防跌--預防跌倒13知',   # text 內容不可超過60字元，label內容不可超過20字元
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514023.pdf'
                            ),
                            URITemplateAction(
                                label='生活保健之預防痠痛衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502040.pdf'
                            ),                            
                            URITemplateAction(
                                label='預防胃食道逆流衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502029.pdf'
                            ),
                            URITemplateAction(
                                label='抗凝血劑Coumadin服用注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502019.pdf'
                            )                            
                        ]
                    )                        
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0 
################################### 心血管疾病 #################################       
    elif user_message.find('心臟血管疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='心臟血管疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='心臟血管疾病衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='高血壓居家自我照顧',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502022.pdf'
                            ),
                            URITemplateAction(
                                label='高血脂的飲食衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502021.pdf'
                            ),
                            URITemplateAction(
                                label='心肌梗塞復健運動衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306015.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='心臟血管疾病衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識永久性人工心臟節律器',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306014.pdf'
                            ),
                            URITemplateAction(
                                label='認識心臟衰竭及出院衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306013.pdf'
                            ),
                            URITemplateAction(
                                label='認識心導管檢查',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306012.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
      #   line_bot_api.push_message(uid, care_message)
        return 0 
############################### 手術相關 ####################################### 
    elif user_message.find('手術相關衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='手術相關衛教資訊',
            template=ButtonsTemplate(
#                       thumbnail_image_url='  ',
                        title='手術相關衛教資訊',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='傷口自我照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306017.pdf'
                            ),
                            URITemplateAction(
                                label='門診手術及麻醉準備注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306016.pdf'
                            )                            
                        ]
                    )                                               
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)
        return 0 
##############################  牙科 ##########################################
    elif user_message.find('牙科衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='牙科衛教資訊',
            template=ButtonsTemplate(               
#                        thumbnail_image_url='  ',
                        title='牙科衛教資訊',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='齒齦下刮除術暨牙根整平',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180511004.pdf'
                            ),
                            URITemplateAction(
                                label='牙齒矯正口腔清潔',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180511003.pdf'
                            ),                            
                            URITemplateAction(
                                label='牙科-手術術後注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180511002.pdf'
                            ),
                            URITemplateAction(
                                label='牙周手術術後注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180511001.pdf'
                            )                            
                        ]
            )                        
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0 
################################## 出院準備  ###################################
    elif user_message.find('出院準備衛教') != -1:        
        care_message = TemplateSendMessage(
            alt_text='出院準備衛教資訊',
            template = ButtonsTemplate(
                title='出院準備衛教資訊',
                text= '請按以下連結查詢',
                actions= [
                    URITemplateAction(
                        label= '輔具資源租借介紹',
                        uri= "http://www.kmsh.org.tw/hygr_Edu/hygr/20180306018.pdf"
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)
        return 0
#################################### 外科 ######################################
    elif user_message.find('外科衛教') != -1:        
        care_message = TemplateSendMessage(
            alt_text='外科衛教資訊',
            template = ButtonsTemplate(
                title='外科衛教資訊',
                text= '請按以下連結查詢',
                actions= [
                    URITemplateAction(
                        label= '靜脈曲張',
                        uri= "http://www.kmsh.org.tw/hygr_Edu/hygr/20190527002.pdf"
                        ),
                    URITemplateAction(
                        label= '乳房重建衛教',
                        uri= "http://www.kmsh.org.tw/hygr_Edu/hygr/20190527001.pdf"
                        ) 
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0        
################################# 外語護理指導 #################################
    elif user_message.find('外語護理指導衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='外語護理指導衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='外語護理指導衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='預防跌倒(中越)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514019.pdf'
                            ),
                            URITemplateAction(
                                label='預防跌倒(中英)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514018.pdf'
                            ),
                            URITemplateAction(
                                label='預防跌倒(印尼)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514017.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='外語護理指導衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='登革熱(英)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502052.pdf'
                            ),
                            URITemplateAction(
                                label='肺結核(英)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502051.pdf'
                            ),
                            URITemplateAction(
                                label='茲卡(英)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502050.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
################################## 皮膚疾病 ####################################
    elif user_message.find('皮膚疾病衛教') != -1:        
        care_message = TemplateSendMessage(
            alt_text='皮膚疾病衛教資訊',
            template = ButtonsTemplate(
                title='皮膚疾病衛教資訊',
                text= '請按以下連結查詢',
                actions= [
                    URITemplateAction(
                        label= '高齡者壓瘡傷口照護衛教',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180306021.pdf'
                        ),
                    URITemplateAction(
                        label= '燒燙傷的癒後照顧',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180306020.pdf'
                        ),
                    URITemplateAction(
                        label= '手或足部傷口浸泡與護理',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180306019.pdf'
                        ) 
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
    
############################### 耳鼻喉疾病衛教資訊 ##############################
    elif user_message.find('耳鼻喉疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='耳鼻喉疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='耳鼻喉疾病衛教資訊-1/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='關於內耳傷害引起之聽力喪失',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502018.pdf'
                            ),
                            URITemplateAction(
                                label='醫生我是頭痛不是鼻子痛',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502017.pdf'
                            ),
                            URITemplateAction(
                                label='擾人的鼾聲',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502016.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='耳鼻喉疾病衛教資訊-2/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='聲音異常疾患與嗓子的保養',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502015.pdf'
                            ),
                            URITemplateAction(
                                label='鼻竇炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502014.pdf'
                            ),
                            URITemplateAction(
                                label='漫談慢性中耳炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502013.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='耳鼻喉疾病衛教資訊-3/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='解除炫暈的頭位運動',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502012.pdf'
                            ),
                            URITemplateAction(
                                label='腮腺腫塊',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502011.pdf'
                            ),
                            URITemplateAction(
                                label='喉頭異物感',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502010.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='耳鼻喉疾病衛教資訊-4/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='甲狀腺腫塊',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502009.pdf'
                            ),
                            URITemplateAction(
                                label='天旋地轉之良性陣發姿勢性眩暈',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502008.pdf'
                            ),
                            URITemplateAction(
                                label='中耳積水',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502007.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='耳鼻喉疾病衛教資訊-5/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='口腔潰瘍與口腔癌',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502006.pdf'
                            ),
                            URITemplateAction(
                                label='天旋地轉之良性陣發姿勢性眩暈',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502008.pdf'
                            ),
                            URITemplateAction(
                                label='中耳積水',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502007.pdf'
                            )                            
                        ]
                    )                                         
#------------------------------------------------------------------------------
                ]
            )
        )        
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)
        return 0        
    
############################## 肝膽疾病 ########################################
    elif user_message.find('肝膽疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='肝膽疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='肝膽疾病衛教資訊-1/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='肝葉切除術之術後照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306031.pdf'
                            ),
                            URITemplateAction(
                                label='急性胰臟炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306030.pdf'
                            ),
                            URITemplateAction(
                                label='認識肝細胞癌(肝癌)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306029.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='肝膽疾病衛教資訊-2/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='腹腔鏡膽囊切除手術後之照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306028.pdf'
                            ),
                            URITemplateAction(
                                label='膽汁引流管日常照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306027.pdf'
                            ),
                            URITemplateAction(
                                label='認識膽結石',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306026.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='肝膽疾病衛教資訊-3/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識肝癌的經皮酒精注射治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306025.pdf'
                            ),
                            URITemplateAction(
                                label='肝癌的飲食治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306024.pdf'
                            ),
                            URITemplateAction(
                                label='認識肝癌的經肝動脈血管栓塞術治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306023.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='肝膽疾病衛教資訊-4/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識肝癌的手術治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306022.pdf'
                            ),
                            URITemplateAction(
                                label='肝癌的飲食治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306024.pdf'
                            ),
                            URITemplateAction(
                                label='認識肝癌的經肝動脈血管栓塞術治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306023.pdf'
                            )                            
                        ]
                    )                                                           
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE1-TemplateSendMessage
#------------------------------------------------------------------------------        
        line_bot_api.reply_message(event.reply_token,care_message)       
        #line_bot_api.push_message(uid, care_message)
        return 0    
###############################  兒科疾病 #####################################
    elif user_message.find('兒科疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='兒科疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='兒科疾病衛教資訊-1/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='熱性痙攣',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514016.pdf'
                            ),
                            URITemplateAction(
                                label='認識腸病毒',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514015.pdf'
                            ),
                            URITemplateAction(
                                label='認識哮吼及其照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514014.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-2/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識嬰幼兒/兒童泌尿道感染',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514013.pdf'
                            ),
                            URITemplateAction(
                                label='認識兒童腦膜炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514012.pdf'
                            ),
                            URITemplateAction(
                                label='認識兒童缺鐵性貧血',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514011.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-3/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識兒童急性腸胃炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514010.pdf'
                            ),
                            URITemplateAction(
                                label='認識兒童急性咽喉炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514009.pdf'
                            ),
                            URITemplateAction(
                                label='認識兒童下呼吸道感染',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514008.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-4/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識水痘',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514007.pdf'
                            ),
                            URITemplateAction(
                                label='認識小兒猩紅熱',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514006.pdf'
                            ),
                            URITemplateAction(
                                label='預防兒童跌倒',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514005.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-5/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='登革熱',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514004.pdf'
                            ),
                            URITemplateAction(
                                label='氧氣帳照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514003.pdf'
                            ),
                            URITemplateAction(
                                label='川崎氏症',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514002.pdf'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='兒科疾病衛教資訊-6/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='小兒發燒怎麼辦',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514001.pdf'
                            ),
                            URITemplateAction(
                                label='門診-頭部外傷衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502036.pdf'
                            ),
                            URITemplateAction(
                                label='門診-腸病毒衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502035.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-7/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='嬰兒常見的問題及處理方法',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306010.pdf'
                            ),
                            URITemplateAction(
                                label='嬰幼兒泌尿道感染',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306009.pdf'
                            ),
                            URITemplateAction(
                                label='認識新生兒鵝口瘡',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306008.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-8/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='新生兒沐浴及臍帶護理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306007.pdf'
                            ),
                            URITemplateAction(
                                label='新生兒腸胃炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306006.pdf'
                            ),
                            URITemplateAction(
                                label='新生兒黃疸',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306005.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-9/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='新生兒尿布疹',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306004.pdf'
                            ),
                            URITemplateAction(
                                label='新生兒日常照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306003.pdf'
                            ),
                            URITemplateAction(
                                label='嬰幼兒發燒了，怎麼辦？',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306002.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='兒科疾病衛教資訊-10/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='早產兒居家照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306001.pdf'
                            ),
                            URITemplateAction(
                                label='小兒發燒怎麼辦',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514001.pdf'
                            ),
                            URITemplateAction(
                                label='門診-腸病毒衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502035.pdf'
                            )                            
                        ]
                    )                                          
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage  
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0                 
################################# 泌尿疾病 #####################################
    elif user_message.find('泌尿疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='泌尿疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='泌尿疾病衛教資訊-1/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='迴腸膀胱造廔手術衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514021.pdf'
                            ),
                            URITemplateAction(
                                label='認識尿失禁衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502005.pdf'
                            ),
                            URITemplateAction(
                                label='預防泌尿道感染衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502004.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='泌尿疾病衛教資訊-2/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='尿路結石患者飲食衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502003.pdf'
                            ),
                            URITemplateAction(
                                label='何謂間質性膀胱炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502002.pdf'
                            ),
                            URITemplateAction(
                                label='如何保護攝護腺',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502001.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='泌尿疾病衛教資訊-3/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='雙J型導管之照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306040.pdf'
                            ),
                            URITemplateAction(
                                label='膀胱癌手術後須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306039.pdf'
                            ),
                            URITemplateAction(
                                label='體外震波碎石術後照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306038.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='泌尿疾病衛教資訊-4/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='膀胱造口之照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306037.pdf'
                            ),
                            URITemplateAction(
                                label='間歇性自我清潔導尿法',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306036.pdf'
                            ),
                            URITemplateAction(
                                label='精索靜脈曲張及術後照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306035.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='泌尿疾病衛教資訊-5/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='前列腺肥大及手術後照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306034.pdf'
                            ),
                            URITemplateAction(
                                label='泌尿道感染之照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306033.pdf'
                            ),
                            URITemplateAction(
                                label='導尿管照護之衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306032.pdf'
                            )                            
                        ]
                    )                                          
#------------------------------------------------------------------------------
                ]
            )
        ) 
        # 結束MESSAGE1-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)       
        return 0
################################# 肺部胸腔疾病 ################################
    elif user_message.find('肺部胸腔疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='肺部胸腔疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='肺部胸腔疾病衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識氣喘',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306046.pdf'
                            ),
                            URITemplateAction(
                                label='認識肺結核',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306045.pdf'
                            ),
                            URITemplateAction(
                                label='慢性阻塞性肺病',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306044.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='肺部胸腔疾病衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='結核菌檢查',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306043.pdf'
                            ),
                            URITemplateAction(
                                label='正確執行抽痰技術',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306042.pdf'
                            ),
                            URITemplateAction(
                                label='認識肺癌',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306041.pdf'
                            )                            
                        ]
                    )         
    
                ]
            )
        )         # 結束MESSAGE1-TemplateSendMessage    
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)       
        return 0    
################################ 侵入性檢查 ####################################
    elif user_message.find('侵入性檢查相關衛教') != -1:        
        care_message = TemplateSendMessage(
            alt_text='侵入性檢查衛教資訊',
            template = ButtonsTemplate(
                title='侵入性檢查衛教資訊',
                text= '請按以下連結查詢',
                actions= [
                    URITemplateAction(
                        label= '超音波導引下抽吸',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180502041.pdf'
                        ),
                    URITemplateAction(
                        label= '胃鏡前檢查須知',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180502033.pdf'
                        ),
                    URITemplateAction(
                        label= '大腸鏡前後檢查須知',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180502032.pdf'
                        ) 
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
################################# 急診相關  ####################################
    elif user_message.find('急診相關衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='急診相關衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='急診相關衛教資訊-1/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='手術前準備及注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514027.pdf'
                            ),
                            URITemplateAction(
                                label='頭部創傷需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306056.pdf'
                            ),
                            URITemplateAction(
                                label='腸胃炎照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306055.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='急診相關衛教資訊-2/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='暈眩照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306054.pdf'
                            ),
                            URITemplateAction(
                                label='發燒注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306053.pdf'
                            ),
                            URITemplateAction(
                                label='創傷傷口照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306052.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='急診相關衛教資訊-3/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='狹心症(心絞痛) 照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306051.pdf'
                            ),
                            URITemplateAction(
                                label='氣喘照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306050.pdf'
                            ),
                            URITemplateAction(
                                label='泌尿道感染照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306049.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='急診相關衛教資訊-4/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='上石膏後照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306048.pdf'
                            ),
                            URITemplateAction(
                                label='發燒處理衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306047.pdf'
                            ),
                            URITemplateAction(
                                label='手術前準備及注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514027.pdf'
                            )                            
                        ]
                    )                                                             
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)       
        return 0        
###############################################################################
    elif user_message.find('骨科疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='骨科疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='骨科疾病衛教資訊-1/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='人工膝關節置換術之照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514026.pdf'
                            ),
                            URITemplateAction(
                                label='預防下背痛衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502039.pdf'
                            ),
                            URITemplateAction(
                                label='板機指手術衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502038.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='骨科疾病衛教資訊-2/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='石膏護理衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502037.pdf'
                            ),
                            URITemplateAction(
                                label='痛風衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502024.pdf'
                            ),
                            URITemplateAction(
                                label='行動輔具使用之衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306063.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='骨科疾病衛教資訊-3/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='膝關節鏡手術前、後護理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306062.pdf'
                            ),
                            URITemplateAction(
                                label='骨質疏鬆症–無聲無息的隱形殺手',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306061.pdf'
                            ),
                            URITemplateAction(
                                label='發展性髖關節發育不良',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306060.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='骨科疾病衛教資訊-4/4',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識腕隧道症候群(CTS)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306059.pdf'
                            ),
                            URITemplateAction(
                                label='顏面骨折術後注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306058.pdf'
                            ),
                            URITemplateAction(
                                label='背架的穿法',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306057.pdf'
                            )                            
                        ]
                    )                                         
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)       
        return 0 
##################################### 健康保健 ################################
    elif user_message.find('健康保健衛教') != -1:        
        care_message = TemplateSendMessage(
            alt_text='健康保健衛教資訊',
            template = ButtonsTemplate(
                title='健康保健衛教資訊',
                text= '請按以下連結查詢',
                actions= [
                    URITemplateAction(
                        label= '認識檳榔危害',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180814002.pdf'
                        ),
                    URITemplateAction(
                        label= '戒菸防治',
                        uri= 'http://www.kmsh.org.tw/hygr_Edu/hygr/20180814001.pdf'
                        )                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
################################# 產科婦科疾病衛教資訊 ##########################
    elif user_message.find('產科婦科疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='產科婦科疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='產科婦科疾病衛教資訊-1/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='執行親子同室相關注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514025.pdf'
                            ),
                            URITemplateAction(
                                label='無痛分娩',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306083.pdf'
                            ),
                            URITemplateAction(
                                label='母乳哺餵須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306082.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='產科婦科疾病衛教資訊-2/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='增加奶水分泌的十大要訣',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306081.pdf'
                            ),
                            URITemplateAction(
                                label='認識親子同室',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306080.pdf'
                            ),
                            URITemplateAction(
                                label='早產及安胎護理指導單',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306079.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='產科婦科疾病衛教資訊-3/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='腹腔鏡手術後照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306078.pdf'
                            ),
                            URITemplateAction(
                                label='妊娠糖尿病',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306077.pdf'
                            ),
                            URITemplateAction(
                                label='腹腔鏡子宮全切除術後照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306076.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='產科婦科疾病衛教資訊-4/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='子宮肌瘤切除術後照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306075.pdf'
                            ),
                            URITemplateAction(
                                label='婦科手術後居家自我照顧須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306074.pdf'
                            ),
                            URITemplateAction(
                                label='尿失禁手術及術後照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306073.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='產科婦科疾病衛教資訊-5/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='子宮頸癌手術前後照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306072.pdf'
                            ),
                            URITemplateAction(
                                label='認識子宮頸癌',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306071.pdf'
                            ),
                            URITemplateAction(
                                label='認識婦女尿失禁',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306070.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='產科婦科疾病衛教資訊-6/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識子宮頸圓錐切片及返家注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306069.pdf'
                            ),
                            URITemplateAction(
                                label='凱格爾氏運動',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306068.pdf'
                            ),
                            URITemplateAction(
                                label='產後保健',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306067.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='產科婦科疾病衛教資訊-7/7',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='骨盆腔發炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306066.pdf'
                            ),
                            URITemplateAction(
                                label='妊娠性高血壓/子癇前症/子癇症',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306065.pdf'
                            ),
                            URITemplateAction(
                                label='子宮鏡檢查及返家注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306064.pdf'
                            )                            
                        ]
                    )                                          
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)       
        return 0            
############################### 腎臟疾病 #######################################
    elif user_message.find('腎臟疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='腎臟疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='腎臟疾病衛教資訊-1/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='血液透析病患低鈉飲食衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502048.pdf'
                            ),
                            URITemplateAction(
                                label='急性腎盂腎炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306091.pdf'
                            ),
                            URITemplateAction(
                                label='雙腔靜脈導管自我照顧-新',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306090.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腎臟疾病衛教資訊-2/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='首次血液透析注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306089.pdf'
                            ),
                            URITemplateAction(
                                label='血液透析病患飲食控制低磷飲食',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306088.pdf'
                            ),
                            URITemplateAction(
                                label='血液透析病患飲食控制低鉀飲食',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306087.pdf'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腎臟疾病衛教資訊-3/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='血液透析病人的自我照顧',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306086.pdf'
                            ),
                            URITemplateAction(
                                label='廔管手術後血管照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306085.pdf'
                            ),
                            URITemplateAction(
                                label='認識腹膜透析',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306084.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0     
############################### 感染疾病 #######################################    
    elif user_message.find('感染疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='感染疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='感染疾病衛教資訊-1/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='門診-蜂窩性組織炎衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502034.pdf'
                            ),
                            URITemplateAction(
                                label='認識全身性紅斑性狼瘡',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502030.pdf'
                            ),
                            URITemplateAction(
                                label='痰液採檢注意事項',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502028.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='感染疾病衛教資訊-2/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='登革熱患者之衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306094.pdf'
                            ),
                            URITemplateAction(
                                label='蜂窩組織炎',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306093.pdf'
                            ),
                            URITemplateAction(
                                label='認識免疫不全及其照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306092.pdf'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='感染疾病衛教資訊-3/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='結核病接觸者檢查衛教單',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502027.pdf'
                            ),
                            URITemplateAction(
                                label='結核病家屬之衛教單',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502026.pdf'
                            ),
                            URITemplateAction(
                                label='結核病完成治療後之衛教單',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502025.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0 
############################ 腸胃疾病 ##########################################
    elif user_message.find('腸胃疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='腸胃疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='腸胃疾病衛教資訊-1/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='急性腸胃炎飲食衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502020.pdf'
                            ),
                            URITemplateAction(
                                label='大腸癌的手術治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306109.pdf'
                            ),
                            URITemplateAction(
                                label='認識大腸癌',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306108.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腸胃疾病衛教資訊-2/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識闌尾炎及其照護處置',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306107.pdf'
                            ),
                            URITemplateAction(
                                label='認識痔瘡及其照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306106.pdf'
                            ),
                            URITemplateAction(
                                label='認識疝氣及其照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306105.pdf'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腸胃疾病衛教資訊-3/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識肛門廔管及其照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306104.pdf'
                            ),
                            URITemplateAction(
                                label='胃腸道手術後飲食衛教',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306103.pdf'
                            ),
                            URITemplateAction(
                                label='認識大腸癌',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306108.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0         
############################ 腦神經系統疾病 ####################################
    elif user_message.find('腦神經系統疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='腦神經系統疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='腦神經系統疾病衛教資訊-1/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='顏面神經麻痺如何自我照顧',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502031.pdf'
                            ),
                            URITemplateAction(
                                label='偏頭痛的預防',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502023.pdf'
                            ),
                            URITemplateAction(
                                label='老年失智症之用藥須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306101.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腦神經系統疾病衛教資訊-2/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='遠離隱形殺手～腦中風',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306100.pdf'
                            ),
                            URITemplateAction(
                                label='認識癲癇',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306099.pdf'
                            ),
                            URITemplateAction(
                                label='巴金森氏症居家照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306097.pdf'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腦神經系統疾病衛教資訊-3/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='老年失智症之居家照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306096.pdf'
                            ),
                            URITemplateAction(
                                label='眩暈症',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306095.pdf'
                            ),
                            URITemplateAction(
                                label='遠離隱形殺手～腦中風',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306100.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0          
############################ 腦神經系統疾病 ####################################
    elif user_message.find('腦神經系統疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='腦神經系統疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='腦神經系統疾病衛教資訊-1/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='顏面神經麻痺如何自我照顧',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502031.pdf'
                            ),
                            URITemplateAction(
                                label='偏頭痛的預防',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502023.pdf'
                            ),
                            URITemplateAction(
                                label='老年失智症之用藥須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306101.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腦神經系統疾病衛教資訊-2/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='遠離隱形殺手～腦中風',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306100.pdf'
                            ),
                            URITemplateAction(
                                label='認識癲癇',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306099.pdf'
                            ),
                            URITemplateAction(
                                label='巴金森氏症居家照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306097.pdf'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='腦神經系統疾病衛教資訊-3/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='老年失智症之居家照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306096.pdf'
                            ),
                            URITemplateAction(
                                label='眩暈症',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306095.pdf'
                            ),
                            URITemplateAction(
                                label='遠離隱形殺手～腦中風',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306100.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0      
############################ 精神科疾病 #######################################
    elif user_message.find('精神科疾病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='精神科疾病衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='精神科疾病衛教資訊-1/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='談精神病患如何生活管理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502044.pdf'
                            ),
                            URITemplateAction(
                                label='談家屬如何協助慢性精神病患居家生活',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502043.pdf'
                            ),
                            URITemplateAction(
                                label='認識精神科藥物副作用(門診版)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502042.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='精神科疾病衛教資訊-2/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='數羊的夜晚~談失眠',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306114.pdf'
                            ),
                            URITemplateAction(
                                label='認識精神科藥物副作用',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306113.pdf'
                            ),
                            URITemplateAction(
                                label='想發脾氣時怎麼辦？',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306112.pdf'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='精神科疾病衛教資訊-3/3',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='想自殺，怎麼辦？',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306111.pdf'
                            ),
                            URITemplateAction(
                                label='幻覺',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306110.pdf'
                            ),
                            URITemplateAction(
                                label='認識精神科藥物副作用(門診版)',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502042.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )  # 結束MESSAGE-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)
        return 0
############################ 糖尿病 ###########################################
    elif user_message.find('糖尿病衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='糖尿病衛教資訊',
            template=ButtonsTemplate(
#                       thumbnail_image_url='  ',
                        title='糖尿病衛教資訊',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='糖尿病高血糖處理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502047.pdf'
                            ),                            
                            URITemplateAction(
                                label='糖尿病低血糖處理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502046.pdf'
                            ),
                            URITemplateAction(
                                label='生病時的處理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502045.pdf'
                            
                            ),
                            URITemplateAction(
                                label='糖尿病足部護理',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306117.pdf'
                            )                            
                        ]
                    )                        
        )  # 結束Button-TemplateSendMessage
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0  
###############################  癌症相關 #####################################
    elif user_message.find('癌症相關衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='癌症相關衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='癌症相關衛教資訊-1/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識治療肝癌的射頻腫瘤滅除術',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514028.pdf'
                            ),
                            URITemplateAction(
                                label='大腸直腸癌的飲食原則',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514024.pdf'
                            ),
                            URITemplateAction(
                                label='乳癌kadcyla化學標靶藥物治療及照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180514022.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-2/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識肺癌標靶藥物副作用及自我照顧',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180502049.pdf'
                            ),
                            URITemplateAction(
                                label='靜脈植入式注射座照護須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306142.pdf'
                            ),
                            URITemplateAction(
                                label='週邊置入中心靜脈導管照護需知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306141.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-3/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='面對癌症疼痛',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306140.pdf'
                            ),
                            URITemplateAction(
                                label='乳癌Phyxol化學治療及照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306139.pdf'
                            ),
                            URITemplateAction(
                                label='乳癌與乳房自我檢查',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306138.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-4/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識乳癌化學治療之Taxotere',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306137.pdf'
                            ),
                            URITemplateAction(
                                label='認識乳癌的手術治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306136.pdf'
                            ),
                            URITemplateAction(
                                label='認識乳癌標靶治療之Herceptin',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306135.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-5/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識乳癌放射線治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306134.pdf'
                            ),
                            URITemplateAction(
                                label='認識乳癌化學治療之FEC',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306133.pdf'
                            ),
                            URITemplateAction(
                                label='乳癌FLC化學治療及其照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306132.pdf'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='癌症相關衛教資訊-6/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='乳癌手術的復健運動',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306131.pdf'
                            ),
                            URITemplateAction(
                                label='認識乳癌',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306130.pdf'
                            ),
                            URITemplateAction(
                                label='肺癌化學治療藥物副作用及自我照顧',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306128.pdf'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-7/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='認識非小細胞肺癌化學治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306129.pdf'
                            ),
                            URITemplateAction(
                                label='認識小細胞肺癌化學治療',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306127.pdf'
                            ),
                            URITemplateAction(
                                label='認識前列腺癌化學治療之Taxotere',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306126.pdf'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-8/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='膀胱內灌注化學藥物須知',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306125.pdf'
                            ),
                            URITemplateAction(
                                label='大腸直腸癌化學治療之5FU及葉酸',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306124.pdf'
                            ),
                            URITemplateAction(
                                label='大腸癌標靶治療Cetuximab',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306123.pdf'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-9/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='大腸癌化學治療FOLFIRI',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306122.pdf'
                            ),
                            URITemplateAction(
                                label='大腸癌標靶治療Bevacizumab',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306121.pdf'
                            ),
                            URITemplateAction(
                                label='大腸癌化學治療FOLFOX4',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306120.pdf'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='癌症相關衛教資訊-10/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='子宮頸術後接受放射療法常見問題及照護',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306119.pdf'
                            ),
                            URITemplateAction(
                                label='人類乳突病毒對子宮頸癌的影響',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306118.pdf'
                            ),
                            URITemplateAction(
                                label='面對癌症疼痛',
                                uri='http://www.kmsh.org.tw/hygr_Edu/hygr/20180306140.pdf'
                            )                            
                        ]
                    )                                          
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE2-TemplateSendMessage  
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0               
#############################################################################
##                          文件衛教 選單
##############################################################################
    elif user_message.find('文件衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='文件衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='文件衛教資訊-1/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='當月衛教新知',
                                uri=Clinic_Book.hnews()
                            ),
                            MessageTemplateAction(
                                label='心臟血管疾病',
                                text='心臟血管疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='手術相關',
                                text='手術相關衛教'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-2/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='牙科',
                                text='牙科衛教'
                            ),
                            MessageTemplateAction(
                                label='出院準備',
                                text='出院準備衛教'
                            ),
                            MessageTemplateAction(
                                label='外科',
                                text='外科衛教'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-3/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='外語護理指導',
                                text='外語護理指導衛教'
                            ),
                            MessageTemplateAction(
                                label='皮膚疾病',
                                text='皮膚疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='耳鼻喉疾病',
                                text='耳鼻喉疾病衛教'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-4/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='肝膽疾病',
                                text='肝膽疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='兒科疾病',
                                text='兒科疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='泌尿疾病',
                                text='泌尿疾病衛教'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-5/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='肺部胸腔疾病',
                                text='肺部胸腔疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='侵入性檢查相關',
                                text='侵入性檢查相關衛教'
                            ),
                            MessageTemplateAction(
                                label='急診相關',
                                text='急診相關衛教'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='文件衛教資訊-6/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='骨科疾病',
                                text='骨科疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='健康保健',
                                text='健康保健衛教'
                            ),
                            MessageTemplateAction(
                                label='產科、婦科疾病',
                                text='產科婦科疾病衛教'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-7/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='腎臟疾病',
                                text='腎臟疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='感染疾病',
                                text='感染疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='腸胃疾病',
                                text='腸胃疾病衛教'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-8/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='腦神經系統疾病',
                                text='腦神經系統疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='精神科疾病',
                                text='精神科疾病衛教'
                            ),
                            MessageTemplateAction(
                                label='糖尿病',
                                text='糖尿病衛教'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='文件衛教資訊-9/9',
                        text='各科別衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='癌症相關',
                                text='癌症相關衛教'
                            ),
                            MessageTemplateAction(
                                label='一般照護',
                                text='一般照護衛教'
                            ),
                            MessageTemplateAction(
                                label='兒科疾病',
                                text='兒科疾病衛教'
                            )                            
                        ]
                    )
                    
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage  
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)        
        return 0

################################# 吞嚥困難(影片衛教) ##########################        
    elif user_message.find('吞嚥困難衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='吞嚥困難衛教資訊',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='吞嚥困難衛教資訊-1/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='食在安全測試液體製作',
                                uri='https://www.youtube.com/watch?v=Go2Pn-ZjDig&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='食在安全蒸蛋製作方式',
                                uri='https://www.youtube.com/watch?v=nLXtMS5Z3io&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='進食安全步驟完整版',
                                uri='https://www.youtube.com/watch?v=zp8tewapWRo&feature=youtu.be'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='吞嚥困難衛教資訊-2/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='腹頸部肌力訓練完整版',
                                uri='https://www.youtube.com/watch?v=T3tVbGMenT8&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='臉頰按摩步驟完整版',
                                uri='https://www.youtube.com/watch?v=DOaFRNoQ_d0&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='灌食管灌食步驟完整版',
                                uri='https://www.youtube.com/watch?v=g1csRMSKSQU&feature=youtu.be'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='吞嚥困難衛教資訊-3/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='床邊語言復健運動',
                                uri='https://www.youtube.com/watch?v=XAra25wbv-8&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='健口瑜珈操高字塔',
                                uri='https://www.youtube.com/watch?v=CySwRJ57tRk&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='頭頸放鬆',
                                uri='https://www.youtube.com/watch?v=VztrSCrx2n8&feature=youtu.be'
                            )                            
                        ]
                    ),     
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='吞嚥困難衛教資訊-4/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='呼吸手部運動',
                                uri='https://www.youtube.com/watch?v=mZN_yRae06w&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='漱口唾液吞嚥',
                                uri='https://www.youtube.com/watch?v=gSyWKZiNicA&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='唇舌齒運動',
                                uri='https://www.youtube.com/watch?v=ixj3U_m8zvE&feature=youtu.be'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='外語護理指導衛教資訊-5/5',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='口腔輪替動作',
                                uri='https://www.youtube.com/watch?v=ZGlSN_PQs7Y&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='食在安全手冊',
                                uri='http://www.kmsh.org.tw/sweb/4000/Dysphagia/files/小港醫院-食在安全手冊(2).pdf'
                            ),
                            URITemplateAction(
                                label='咀嚼吞嚥障礙篩檢表',
                                uri='http://www.kmsh.org.tw/sweb/4000/Dysphagia/files/咀嚼吞嚥障礙篩檢表1080108.pdf'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
############################### 懷孕不適處理 (影片) ############################
    elif user_message.find('懷孕不適處理衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='懷孕不適處理衛教資訊',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='吞懷孕不適處理衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=nhcXYN5i4Io'
                            ),
                            URITemplateAction(
                                label='英文版',
                                uri='https://www.youtube.com/watch?v=oiVwjblOGck'
                            ),
                            URITemplateAction(
                                label='印尼文版',
                                uri='https://www.youtube.com/watch?v=tHMqY-6Yrqg'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='懷孕不適處理衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='泰文版',
                                uri='https://www.youtube.com/watch?v=7QnJgzg_sTA'
                            ),
                            URITemplateAction(
                                label='越南版',
                                uri='https://www.youtube.com/watch?v=y7Mc6534f2A'
                            ),
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=nhcXYN5i4Io'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        # line_bot_api.push_message(uid, care_message)
        return 0
############################### 孕期照護與福利 (影片) ##########################
    elif user_message.find('孕期照護與福利衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='孕期照護與福利衛教資訊',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='孕期照護與福利衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=IeT8lc5PS8Y'
                            ),
                            URITemplateAction(
                                label='英文版',
                                uri='https://www.youtube.com/watch?v=ZLr92g2CnFw'
                            ),
                            URITemplateAction(
                                label='印尼文版',
                                uri='https://www.youtube.com/watch?v=oA08aqGZvNY'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='孕期照護與福利衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='泰文版',
                                uri='https://www.youtube.com/watch?v=gDmXblIxJrE'
                            ),
                            URITemplateAction(
                                label='越南版',
                                uri='https://www.youtube.com/watch?v=Spu0Or1zlFc'
                            ),
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=IeT8lc5PS8Y'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
############################### 母乳哺餵 (影片)#################################   
    elif user_message.find('母乳哺餵衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='母乳哺餵衛教資訊',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='母乳哺餵衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=Y0sc_DbAmmA'
                            ),
                            URITemplateAction(
                                label='英文版',
                                uri='https://www.youtube.com/watch?v=5PAKGSp2Lr4'
                            ),
                            URITemplateAction(
                                label='印尼文版',
                                uri='https://www.youtube.com/watch?v=WGjVCzuunls'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='母乳哺餵衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='泰文版',
                                uri='https://www.youtube.com/watch?v=CbwsxVhgX4s'
                            ),
                            URITemplateAction(
                                label='越南版',
                                uri='https://www.youtube.com/watch?v=wqBR08baR7w'
                            ),
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=Y0sc_DbAmmA'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
############################### 如何調製配方奶及拍打嗝 (影片)####################    
    elif user_message.find('如何調製配方奶及拍打嗝衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='如何調製配方奶及拍打嗝衛教資訊',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='如何調製配方奶及拍打嗝衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=iF0OXZMoHlw'
                            ),
                            URITemplateAction(
                                label='英文版',
                                uri='https://www.youtube.com/watch?v=Y-9b3Azflzk'
                            ),
                            URITemplateAction(
                                label='印尼文版',
                                uri='https://www.youtube.com/watch?v=dPr0Ajyn8fE'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='如何調製配方奶及拍打嗝衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='泰文版',
                                uri='https://www.youtube.com/watch?v=b8OZKWKTBVs'
                            ),
                            URITemplateAction(
                                label='越南版',
                                uri='https://www.youtube.com/watch?v=UBaQOOqJ6DU'
                            ),
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=iF0OXZMoHlw'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
############################### 新生兒沐浴及臍帶護理 (影片)#####################   
    elif user_message.find('新生兒沐浴及臍帶護理衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='新生兒沐浴及臍帶護理衛教資訊',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='新生兒沐浴及臍帶護理衛教資訊-1/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=0F1D8IsZVH4'
                            ),
                            URITemplateAction(
                                label='英文版',
                                uri='https://www.youtube.com/watch?v=U-yyNErf0Fc'
                            ),
                            URITemplateAction(
                                label='印尼文版',
                                uri='https://www.youtube.com/watch?v=3oc9aTWkHoM'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='新生兒沐浴及臍帶護理衛教資訊-2/2',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='泰文版',
                                uri='https://www.youtube.com/watch?v=543pg65K1TU'
                            ),
                            URITemplateAction(
                                label='越南版-上架中',
                                uri='https://www.youtube.com/watch?v=UBaQOOqJ6DU&t=47s'
                            ),
                            URITemplateAction(
                                label='中文版',
                                uri='https://www.youtube.com/watch?v=0F1D8IsZVH4'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
##############################################################################
##                   特殊藥品使用衛教(影片)  入口選單
##############################################################################        
    elif user_message.find('特殊藥品使用衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='特殊藥品使用衛教',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/1.jpg',
                        title='特殊藥品使用衛教-1/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='諾和瑞諾易筆',
                                uri='https://www.youtube.com/watch?time_continue=8&v=c01vqB32K_4'
                            ),
                            
                            URITemplateAction(
                                label='Insulin NovoRapid FP',
                                uri='https://www.youtube.com/watch?time_continue=8&v=c01vqB32K_4'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/2.jpg',
                        title='特殊藥品使用衛教-2/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='諾和密斯30諾易筆',
                                uri='https://www.youtube.com/watch?time_continue=8&v=c01vqB32K_4'
                            ),
                            URITemplateAction(
                                label='Insulin NovoMix 30FP',
                                uri='https://www.youtube.com/watch?time_continue=8&v=c01vqB32K_4'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/3.jpg',
                        title='特殊藥品使用衛教-3/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='瑞和密爾諾易筆',
                                uri='https://www.youtube.com/watch?time_continue=8&v=c01vqB32K_4'
                            ),
                            URITemplateAction(
                                label='Insulin Levemir',
                                uri='https://www.youtube.com/watch?time_continue=8&v=c01vqB32K_4'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/Insulin%20Toujeo_20200521.jpg',
                        title='特殊藥品使用衛教-4/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='糖德仕注射筆',
                                uri='https://www.youtube.com/watch?v=4EL_R5YKUWk&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='Insulin Toujeo',
                                uri='https://www.youtube.com/watch?v=4EL_R5YKUWk&feature=youtu.be'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/trulicity_20200521.jpg',
                        title='特殊藥品使用衛教-5/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='易週糖注射筆',
                                uri='https://www.youtube.com/watch?v=uiXT8WrWZv8&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='Trulicity',
                                uri='https://www.youtube.com/watch?v=uiXT8WrWZv8&feature=youtu.be'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/6.jpg',
                        title='特殊藥品使用衛教-6/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='艾敏釋鼻用噴液懸浮劑',
                                uri='https://www.youtube.com/watch?v=0eNOSWoTBtA&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='Avamys Nasal Spr.',
                                uri='https://www.youtube.com/watch?v=0eNOSWoTBtA&feature=youtu.be'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/7.jpg',
                        title='特殊藥品使用衛教-7/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='多瑞喜穿皮貼片劑',
                                uri='https://www.youtube.com/watch?v=Sw4x3Yl9BQg'
                            ),
                            URITemplateAction(
                                label='Durogesic patch 25μg',
                                uri='https://www.youtube.com/watch?v=Sw4x3Yl9BQg'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/8.jpg',
                        title='特殊藥品使用衛教-8/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='多瑞喜穿皮貼片劑',
                                uri='https://www.youtube.com/watch?v=Sw4x3Yl9BQg'
                            ),
                            URITemplateAction(
                                label='Durogesic patch 12μg',
                                uri='https://www.youtube.com/watch?v=Sw4x3Yl9BQg'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/9.jpg',
                        title='特殊藥品使用衛教-9/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='瑞樂沙旋達碟',
                                uri='https://www.youtube.com/watch?time_continue=2&v=0gHBa4bAb_0'
                            ),
                            URITemplateAction(
                                label='Relenza rotadisk',
                                uri='https://www.youtube.com/watch?time_continue=2&v=0gHBa4bAb_0'
                            )                            
                        ]
                    ),                    
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://www.kmsh.org.tw/affairs/4600_file/populace/304-1/10.jpg',
                        title='特殊藥品使用衛教-10/10',
                        text='請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='泛得林噴霧劑',
                                uri='https://www.youtube.com/watch?v=AE-6YbeHLRo'
                            ),
                            URITemplateAction(
                                label='Ventolin Inhaler',
                                uri='https://www.youtube.com/watch?v=AE-6YbeHLRo'
                            )                            
                        ]
                    )                          
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0
##############################################################################
#                         影片衛教 入口選單        
##############################################################################   
    elif user_message.find('影片衛教') != -1:
        care_message = TemplateSendMessage(
            alt_text='影片衛教資訊',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='影片衛教資訊-1/5',
                        text='各影片衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='咀嚼吞嚥機能重建中心',
                                text='吞嚥困難衛教'
                            ),
                            MessageTemplateAction(
                                label='懷孕不適處理',
                                text='懷孕不適處理衛教'
                            ),
                            MessageTemplateAction(
                                label='孕期照護與福利',
                                text='孕期照護與福利衛教'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='影片衛教資訊-2/5',
                        text='各影片衛教資訊，請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='母乳哺餵',
                                text='母乳哺餵衛教'
                            ),
                            MessageTemplateAction(
                                label='如何調製配方奶及拍打嗝',
                                text='如何調製配方奶及拍打嗝衛教'
                            ),
                            MessageTemplateAction(
                                label='新生兒沐浴及臍帶護',
                                text='新生兒沐浴及臍帶護理衛教'
                            )                            
                        ]

                    ), 
# -----------------------------------------------------------------------------                
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='影片衛教資訊-3/5',
                        text='各影片衛教資訊，請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='藥物回收做環保',
                                uri='https://www.youtube.com/watch?v=LXxXHdKKeSE&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='藥袋資訊知多少',
                                uri='https://www.youtube.com/watch?v=SSBiAHXJ3Ug&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='小兒退燒好簡單',
                                uri='https://www.youtube.com/watch?v=u5BNvpCwowQ&feature=youtu.be'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='影片衛教資訊-4/5',
                        text='各影片衛教資訊，請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='合理使用抗生素',
                                uri='https://www.youtube.com/watch?v=8-B2KIPDZ-0&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='攝護腺肥大用藥介紹',
                                uri='https://www.youtube.com/watch?v=au0n2_LiWN4&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='高血壓介紹',
                                uri='https://www.youtube.com/watch?v=0B9Yl2OI178&feature=youtu.be'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='影片衛教資訊-5/5',
                        text='各影片衛教資訊，請按以下連結查詢',
                        actions=[
                            URITemplateAction(
                                label='糖尿病介紹',
                                uri='https://www.youtube.com/watch?v=tjCH5G4n6nU&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='低血糖介紹',
                                uri='https://www.youtube.com/watch?v=PX9XnS8LWaU&feature=youtu.be'
                            ),
                            URITemplateAction(
                                label='耳滴劑使用小知識',
                                uri='https://www.youtube.com/watch?v=dRHYxiQb-qI&feature=youtu.be'
                            )                            
                        ]
                    )                     
# -----------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage  
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)        
        return 0
##############################################################################
#                       衛教資訊(文件/影片)選單入口
##############################################################################
    elif user_message.find('衛教資訊選單') != -1:        
        care_message = TemplateSendMessage(
            alt_text='衛教資訊選單',
            template = ButtonsTemplate(
                image_aspect_ratio='square',
                thumbnail_image_url='https://lh3.googleusercontent.com/shB0u3JxHzJ2zbrIovXBLmy6gMq17epXkwMDPcBVf7olTuUSEA2JC0BdzUeiIJ-MxckF6mv4ZEkHhgjClivp0EBV-fNKXLDIquJOwzr_buhOW6XzEPc7ktrLrRPhbW1Uf_M08boveQ=w400',
                title='小港醫院衛教資訊選單',
                text= '各科別衛教資訊，請按以下連結查詢',
                actions= [
                    MessageTemplateAction(
                        label= '文件衛教資訊',
                        text= '文件衛教'
                        ),
                    MessageTemplateAction(
                        label= '影片衛教資訊',
                        text= '影片衛教'
                        ),
                    MessageTemplateAction(
                        label= '特殊藥品使用衛教影片',
                        text= '特殊藥品使用衛教'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.push_message(uid, care_message)
        return 0

############################### 內科門診掛號選單 ###############################
        
    elif user_message.find('內科門診掛號選單') != -1:
        reg_message = TemplateSendMessage(
            alt_text='內科門診掛號選單I',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='內科門診掛號選單-1/3',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='胃腸內科',
                                text='掛號胃腸內科'
                            ),
                              MessageTemplateAction(
                                label='肝膽胰內科',
                                text='掛號肝膽胰內科'
                            ),
                              MessageTemplateAction(
                                label='胸腔內科',
                                text='掛號胸腔內科'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='內科門診掛號選單-2/3',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='心臟血管內科',
                                text='掛號心臟內科'
                            ),
                              MessageTemplateAction(
                                label='內分泌新陳代謝內科',
                                text='掛號內分泌科'
                            ),
                              MessageTemplateAction(
                                label='血液腫瘤內科',
                                text='掛號血液腫瘤內科'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='內科門診掛號選單-3/3',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='過敏免疫風濕內科',
                                text='掛號過敏免疫風濕內科'
                            ),
                              MessageTemplateAction(
                                label='腎臟內科',
                                text='掛號腎臟內科'
                            ),
                              MessageTemplateAction(
                                label='感染內科',
                                text='掛號感染內科'
                            )                            
                        ]
                    )                                   
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage 
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0   
############################# 外科門診掛號選單 ################################## 
    elif user_message.find('外科門診掛號選單') != -1:
        reg_message = TemplateSendMessage(
            alt_text='外科門診掛號選單',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='外科門診掛號選單-1/3',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='腦神經外科',
                                text='掛號腦神經外科'
                            ),
                              MessageTemplateAction(
                                label='心臟血管外科',
                                text='掛號心血管外科'
                            ),
                              MessageTemplateAction(
                                label='胸腔外科',
                                text='掛號胸腔外科'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='外科門診掛號選單-2/3',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='胃腸肝膽及一般外科',
                                text='掛號胃腸一般外科'
                            ),
                              MessageTemplateAction(
                                label='乳房外科特診',
                                text='掛號乳房外科'
                            ),
                              MessageTemplateAction(
                                label='整形外科',
                                text='掛號整形外科'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='外科門診掛號選單-3/3',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='口腔顎面外科',
                                text='掛號口腔顎面外科'
                            ),
                              MessageTemplateAction(
                                label='耳鼻喉頭頸外科',
                                text='掛號耳鼻喉科'
                            ),
                              URITemplateAction(
                                label='當月門診手冊下載',
                                uri=Clinic_Book.get()
                            )                            
                        ]
                    )                                                                            
#------------------------------------------------------------------------------
                ]
            )
        ) 
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0        # 結束MESSAGE-TemplateSendMessage 
############################# 特別門診門診掛號選單 ################################## 
    elif user_message.find('特別門診掛號選單') != -1:
        reg_message = TemplateSendMessage(
            alt_text='特別門診掛號選單',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='特別門診掛號選單-1/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='更年期特別門診',
                                text='掛號更年期特診'
                            ),
                              MessageTemplateAction(
                                label='高齡特別門診',
                                text='掛號高齡特別門診'
                            ),
                              MessageTemplateAction(
                                label='戒煙門診',
                                text='掛號戒煙門診'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='特別門診掛號選單-2/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='減重塑身自費門診',
                                text='掛號家醫科'
                            ),
                              MessageTemplateAction(
                                label='旅遊醫學自費門診',
                                text='掛號旅遊醫學自費門診'
                            ),
                              MessageTemplateAction(
                                label='預立醫療照護門診',
                                text='掛號預立醫療照護門診'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='特別門診掛號選單-3/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='失智症整合門診',
                                text='掛號失智症整合門診'
                            ),
                              MessageTemplateAction(
                                label='員工心理健康門診',
                                text='掛號員工心理健康門診'
                            ),
                              MessageTemplateAction(
                                label='隱形眼鏡門診',
                                text='掛號眼科'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='特別門診掛號選單-4/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='咀嚼吞嚥困難特別門診',
                                text='掛號咀嚼吞嚥困難特別門診'
                            ),
                              MessageTemplateAction(
                                label='醫學美容門診(全自費)',
                                text='掛號皮膚科'
                            ),
                              URITemplateAction(
                                label='當月門診手冊下載',
                                uri=Clinic_Book.get()
                            )                            
                        ]
                    )                                                                             
#------------------------------------------------------------------------------
                ]
            )
        ) 
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0        # 結束MESSAGE-TemplateSendMessage
############################# 牙科門診掛號選單 ################################## 
    elif user_message.find('牙科門診掛號選單') != -1:
        reg_message = TemplateSendMessage(
            alt_text='牙科門診掛號選單',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='牙科門診掛號選單-1/2',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='牙科一診',
                                text='掛號牙科一診'
                            ),
                              MessageTemplateAction(
                                label='口腔顎面外科',
                                text='掛號口腔顎面外科'
                            ),
                              MessageTemplateAction(
                                label='齒顎矯正科',
                                text='掛號齒顎矯正科'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='牙科門診掛號選單-2/2',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='牙周病&顯微根管治療3D齒雕',
                                text='掛號牙周病與根管治療'
                            ),
                              MessageTemplateAction(
                                label='牙科約診-醫師群(I)',
                                text='掛號牙科約診A'
                            ),
                              MessageTemplateAction(
                                label='牙科約診-醫師群(II)',
                                text='掛號牙科約診B'
                            )                            
                        ]
                    )                                                                        
#------------------------------------------------------------------------------
                ]
            )
        ) 
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0        # 結束MESSAGE-TemplateSendMessage
###############################################################################
#                               門診掛號選單  
#                       user_message='門診掛號選單'                             
############################################################################### 
    elif user_message.find('門診掛號選單') != -1:
        reg_message = TemplateSendMessage(
            alt_text='門診掛號選單I',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-1/7',
                        text='請按以下連結查詢',
                        actions=[
                              URITemplateAction(
                                label='網路掛號',
                                uri='https://www.kmsh.org.tw/web/KMUHWeb/Pages/P02Register/NetReg/NetRegFirst.aspx?openExternalBrowser=1'
                              ),
                              URITemplateAction(
                                label='網路查詢/取消',
                                uri = 'https://www.kmsh.org.tw/online/NetReg_delSch.asp?openExternalBrowser=1'
                              ),                              
                              MessageTemplateAction(
                                label='電話掛號服務',
                                text='電話掛號服務'
                            )                            
                        ]
                    ),                        
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-2/7',
                        text='請按以下連結查詢',
                        actions=[
                              URITemplateAction(
                                label='當月門診手冊下載',
                                uri = Clinic_Book.get()
                              ),                            
                              MessageTemplateAction(
                                label='內科門診-掛號選單',
                                text='內科門診掛號選單'
                              ),
                              MessageTemplateAction(
                                label='外科門診-掛號選單',
                                text='外科門診掛號選單'
                              ),
                                                   
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-3/7',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='特別門診-掛號選單',
                                text='特別門診掛號選單'
                              ),
                              MessageTemplateAction(
                                label='婦產科',
                                text='掛號婦產科'
                              ),
                              MessageTemplateAction(
                                label='小兒科',
                                text='掛號小兒科'
                            )                            
                        ]
                    ),                                                                  
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-4/7',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='家庭醫學科',
                                text='掛號家醫科'
                              ),
                              MessageTemplateAction(
                                label='神經內科',
                                text='掛號神經內科'
                              ),
                              MessageTemplateAction(
                                label='精神科',
                                text='掛號精神科'
                            )                            
                        ]
                    ),                                                    
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-5/7',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='牙科門診-掛號選單',
                                text='掛號牙科門診掛號選單'
                              ),
                              MessageTemplateAction(
                                label='皮膚科',
                                text='掛號皮膚科'
                              ),
                              MessageTemplateAction(
                                label='眼科',
                                text='掛號眼科'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-6/7',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='泌尿科',
                                text='掛號泌尿科'
                              ),
                              MessageTemplateAction(
                                label='職業病科',
                                text='掛號職業病科'
                              ),
                              MessageTemplateAction(
                                label='復健科',
                                text='掛號復健科'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/XmbgERb-XCLN1xNYwCPHME4ZnsF0CivPHQx4g3F_LNRkZTEFS49Upd_V_kQdaQ8y8kPuU-SE7b3QYmzpUsCsMOPAk5DJ_wHMx3A3dB9sDA6p1qcuxS3LGV5unrhADcH5dCEGIGskhw=w800',
                        title='門診掛號選單-7/7',
                        text='請按以下連結查詢',
                        actions=[                              
                              MessageTemplateAction(
                                label='骨科-醫師群(I)',
                                text='掛號骨科A'
                              ),
                              MessageTemplateAction(
                                label='骨科-醫師群(II)',
                                text='掛號骨科B'
                              ),
                              MessageTemplateAction(
                                label='特別門診-掛號選單',
                                text='特別門診掛號選單'
                            )  
                              
                        ]
                    ),                                                         
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage 
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0         
############################  胃腸內科掛號 #####################################    
    elif user_message.find('掛號胃腸內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='胃腸內科掛號',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/9-WGrDtOPx6wBT-xPmCLIRIv-ZRJNXXxcFa-HsDHUKwLRfgSicHZ0C7Tf0IuFQDj8XQHET_iQ1yFUAjXJruMZYMpmf1C1DEZFBpf0o74t048LK6vBU1fNWN8HMfew7wV3NzIDJR6ew=w400',
                        title='郭昭宏院長/胃腸內科-1/7',
                        text='小港醫院院長/胃腸內科主治醫師。[臨床專業]:幽門桿菌和潰瘍、胃癌之關聯性胃腸蠕動學、消化道癌症.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介郭昭宏醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號郭昭宏醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=158&dept_code=0100'
                            )                            
                        ]
                    ),
                      
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/r7O6NIWl1rXJt1K6_HJeKv7KCUjuudWPIgDhU8poKFDQqnJJwXJgYfDUT7XaaAle4fh0aFVVBhYprytA2tIhCvxR5poIBTKy9Y4YFKfvGU6yG8cy8O-_ICXGDO-VlqRrhYQsvU7sow=w400',
                        title='王耀廣醫師/胃腸內科-2/7',
                        text='小港醫院胃腸內科主治醫師。[臨床專業]:消化道疾病、消化道內視鏡..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王耀廣醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王耀廣醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=423&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/fxRhXib7rg81NnnvVrA2xcD6nt-wtgmpUxidZmD5Z7ROVLYAVXM6xWfq2toUb1QtT35JnfvJaiVL9ssauBquuVaa0-XyUO4r8WBI8xpljWhsYt9X63_T6iHOgRcbuPaXU_hT1XxCfQ=w400',
                        title='余方榮醫師/胃腸內科-3/7',
                        text='高醫大附設醫院胃腸內科主治醫師。[臨床專業]:消化道癌症, 胃幽門桿菌, 治療性內視鏡.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介余方榮醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號余方榮醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=57&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/cmbpM3w-PfKEq9Enl5FA1G11oaXEAaxJ1Ru-aAPdnd27ZXWz-c6PHZJOJjjJM_KcuD_4pRQhLDhIII8tw_9FoHb4E61Tx0AQsy_JuysHW93on3yqAgJDHkr8agLkgZkNoMSGndQqhg=w400',
                        title='龔育民醫師/胃腸內科-4/7',
                        text='小港醫院胃腸內科特約主治醫師。[臨床專業]:消化道疾病、消化道內視鏡.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介龔育民醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號龔育民醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=443&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Eeb71Tne8TjO_h5BCMH__RSGh2Tx5DiSN3t5q-d8yDjeM5qPe4X0WBuSBJhjy2OyItm8LYk7JfeYsiTKhKvgO7Qv9Cv90nZru77E9JqZ7DPl7wCo7StGns5To4NIrL1OK2swQdSTEw=w400',
                        title='沈群勝醫師/胃腸內科-5/7',
                        text='小港醫院胃腸內科主治醫師，[臨床專業]:肝膽疾病、消化道疾病、消化內視鏡檢查..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介沈群勝醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號沈群勝醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=564&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/08PSrV4c_BnmEL2SJXwWi2Nd_HnsY-B7lY3f9sEz5_5mR3GtlVRluBV9h3PQLNhmQS79F_dVO1TRTDGCPkf7m6-kaoTOX6h95lMS-y7zofmzyK0Z6IfRcgxkhSlS2bdDIf0wTFR4qA=w400',
                        title='謝孟書醫師/胃腸內科-6/7',
                        text='小港醫院胃腸內科主治醫師。[臨床專業]:肝膽疾病、消化道疾病、消化內視鏡檢查..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介謝孟書醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號謝孟書醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=543&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/wnDk8aadclrUpNS28UAOsPNIzMSBaIKhtej0n7Bezyqv_TqrUKY4R3EdmYCQRxaXIUOW86Dlt8Dn4JKO-jGLBOXQrmY8FjFxfh0J5khAXfKv78HdzbdFxcBZ75vWviobqKdEDmVgRw=w400',
                        title='朱能生醫師/胃腸內科-7/7',
                        text='小港醫院胃腸內科主治醫師。[臨床專業]:消化道疾病、消化內視鏡檢查..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介朱能生醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號朱能生醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=524&dept_code=0100'
                            )                            
                        ]
                    )                
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0
############################-肝膽胰內科########################################
    elif user_message.find('掛號肝膽胰內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='胃腸肝膽內科掛號',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EOFe8D7KtiIW6Xt71ZL4UKe96GUCJHJBPaKQz-3YHWZAX3Wqnp83AEeqpZvnL0Ej-ySSiHOCs98d3kUvSopWI97OaM68COCMWiazdDc-2JA0ScgzvFP4VAWXtJ889V1Awik69Ah_vw=w400',
                        title='林宜竑醫師/肝膽胰內科-1/2',
                        text='小港醫院肝膽胰內科主治醫師。[臨床專業]:肝炎治療、肝硬化、肝癌、消化系內科..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林宜竑醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林宜竑醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=362&dept_code=0100'
                            )                            
                        ]
                    ),  
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/xHj9DIfQsD5e7F_6VfwEXr44uCP8WW7nToC71l4rZCxego9A4lWzdu4I3Mu8-ScLIL406e0xmOvfu7bJRLONflfvqutj8rbYK82ERND16_M8EV6pBdhAYfKZuakuKZvaK6kQqVU4AQ=w400',
                        title='王志文醫師/肝膽胰內科-2/2',
                        text='小港醫院肝膽胰內科主治醫師。[臨床專業]:肝膽胰疾病、肝炎治療、肝臟腫瘤治療..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王志文醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王志文醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=515&dept_code=0100'
                            )                            
                        ]
                    )                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0
################################- 胸腔內科 ####################################
    elif user_message.find('掛號胸腔內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='胸腔內科掛號',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/D68tZgfgUe9V6p_tBijLLEOs2OSU-TgG3c2JukaTBB3gS-KY-JK_5__eCyotwfFMkw2uNCkb9cptTUBJASBqOeFOOnNk_Nnk93inYbzGhloTawdQ-DLs5azz2Uq1i7LA_TR5q7fXew=w400',
                        title='陳煌麒醫師/胸腔內科-1/6',
                        text='胸腔內科主治醫師。[臨床專業]:如急性或慢性咳嗽、呼吸道感染、肺炎、肺結核、氣喘、胸腔腫瘤、肺癌.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳煌麒醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳煌麒醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=176&dept_code=0100'
                            )                            
                        ]
                    ),  
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/3q78VRbkkXtnjhv5o4cIs0rgRCtnEgjRVFgBnJrw6ch4gVXR5POse42d2F3UTZK-dwTeHW0bJnCicIIA5nkfyUxfJ98dhOogN7ACEpNdc3PT1qurfu_jjb3IOsnD-LF6qWNynD48uQ=w400',
                        title='郭家佑醫師/胸腔內科-2/6',
                        text='小港醫院胸腔內科主治醫師。[臨床專業]:一般內科與各類胸腔及呼吸道疾病、睡眠、老人醫學.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介郭家佑醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號郭家佑醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=563&dept_code=0100'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
              CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/eA47fwAKMw4r5gvSTR4uIHZg7vLpQIGcKJBwfcfkiAm5B9pPOo5gsKPqFz5eJ-5jbObX2GYWyCQXZGnRcZ1hHTZmY-Jd7nUUFRWIEFx7YvfR3InkHMQyCxUpvLmGEfQ6qij5yAWWgQ=w400',
                        title='郭子右醫師/胸腔內科-3/6',
                        text='小港醫院胸腔內科主治醫師。[臨床專業]:一般內科與各類胸腔及呼吸道疾病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介郭子右醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號郭子右醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=425&dept_code=0100'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
              CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/jy0NkY4iHhftJTL8FAYqBNPCrofVhq68tgf-SQVHJVsK84F0ajus9YzYnGTtXIlBacHuHJjYsYvxstV9V0QcZ-XQ9_xGPHZsWfh8qr8fvHkIE2o2XnEWSen3qifyHrtG15ETmSfOeg=w400',
                        title='李玫萱醫師/胸腔內科-4/6',
                        text='高雄醫學大學附設醫院胸腔內科主治醫師。[臨床專業]:咳嗽、咳血、呼吸困難、氣喘、肺結核、肺炎、胸腔腫瘤、呼吸道感染.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李玫萱醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李玫萱醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=239&dept_code=0100'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
              CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/W7-W13qKfyarHYb5Uy-3NFVeIOccD9_NlfbvA43zjyeGEtmWIF0yQljdEQ2UN6xoXliPjoqqotdbfVod9tYmIgkJVxC2L711VuXr-z1NdwZFjn-tPZKYPucZMiu7rgaa6odIJJCI_A=w400',
                        title='阮懷磊醫師/胸腔內科-5/6',
                        text='小港醫院胸腔內科主治醫師。[臨床專業]:胸腔及呼吸道疾病（如急性或慢性咳嗽、各類呼吸道感染、肺炎、肺結核.等)',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介阮懷磊醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號阮懷磊醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=453&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
              CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/HiuSzxbJwBQX_lrpcHtZaAVwwEQrf3N_IKZ5x7DWmULTh0EQO7tGnsYtfXL00xEMYZaEs5TNp95EiXVEuer3U1pKheEOqJWubO_fsN_1aDizjLprXq4qP8Yqw0yG3IqfjeP3As0ucA=w400',
                        title='吳大緯醫師/胸腔內科-6/6',
                        text='小港醫院胸腔內科主治醫師。[臨床專業]:呼吸系統疾病：咳嗽、氣喘、慢性阻塞性肺病、肺炎、肺結核.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介吳大緯醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號吳大緯醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=505&dept_code=0100'
                            )                            
                        ]
                    ) 
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0        
    
#############################  神經內科掛號 ####################################   
    elif user_message.find('掛號神經內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號神經內科',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/b4EHC2xsHBxG4d0PdkrcZyIXct8gNbGQZEVigBOsub9W1if3CxZJZ6fE3w-0cV_vq1q4NCr_7YrTvnIci97l0pCJY9Ksz2YWBQfjikrmfP0-GWipV2OHV7KL9-xRoDzLAdjwsTDktA=w400',
                        title='陳俊鴻醫師/神經內科-1/9',
                        text='小港醫院神經科主治醫師、神經科主任。[臨床專業]:神經學、腦中風、神經重症.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳俊鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳俊鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=389&dept_code=1000'
                            )                            
                        ]
                    ),
                      
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/037SWWjFZiBxIsL-pIF4rmCugpMDNr70b-hfPOiY7UM1rVpybYYmPktAHJxgjnUOQ_sjUVBqqLI3C_Ahy0IFG2tpWNikByLSJ2Oj68hW3-saFLccx4REZbloLaq6072Qo7KSBdem3Q=w400',
                        title='劉立民醫師/神經內科-2/9',
                        text='高醫大附設醫院神經部主治醫師。[臨床專業]:帕金森氏症、不自主運動、肉毒桿菌注射、癲癇、自律神經功能失調.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉立民醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉立民醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=184&dept_code=1000'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/opYpAIhHVT2IkpzENoLUN_EX77f5BaIKqjYattqq0Af9dsyAQkwny0CIjEExWl6Ff2BjRVLzj9xmtdC_h1ea-NDLKtP-J8cEyuqWvIZ6O9ALdnNzQshALTaOGF2azlYrXq0Fpj-jZw=w400',
                        title='謝升文醫師/神經內科-3/9',
                        text='小港醫院神經科主治醫師。[臨床專業]:一般神經科、腦中風、睡眠障礙.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介謝升文醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號謝升文醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=299&dept_code=1000'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/rhk9yWnPGcucJ3RhDnk8ScrVZxgTBYluXemYOd6TlEIGM0wMeCAlCdYqYd_WaDo8WloJTWI2qbLScg05LkvUdmyJ5XXs29yQXGensOFdgPbn70jN6vA2yL2MCjs5iSXpPnV9CRhiXQ=w400',
                        title='黃柏穎醫師/神經內科-4/9',
                        text='小港醫院神經科主治醫師。[臨床專業]:一般神經學、腦中風、神經科急重症、生物資訊.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃柏穎醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃柏穎醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=320&dept_code=1000'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/KgaiL4gTt9WxNtt9jXreoKquC8jydV8IuxZaj3u9c3UpUAlbKFKfH3Xp20Lbf4RDBRLf20XiWOPRQjVqCSYoXdemRQV7FrrlKx-8SYeM1BhAKnIJeKAtaQdQNWHdZqOzZGUuVJXWtA=w400',
                        title='李建勳醫師/神經內科-5/9',
                        text='小港醫院神經科主治醫師，[臨床專業]:一般神經醫學、腦中風、失智症、頭痛..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李建勳醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李建勳醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=298&dept_code=1000'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/myDEnYJy7GwpNkVyWvhvfUK00sBuP3-dKl-UvpZViZZMMGmBWf8Y8mcInbn4KPG6g6W8tEe-VX-7bmPwytsXaIRbiOm9cgPIIEvA_92hi2gykuW-dFc3PsaUqHfWJ5NN_nfG7OT_AQ=w400',
                        title='李國瑋醫師/神經內科-6/9',
                        text='小港醫院神經科主治醫師。[臨床專業]:一般神經科、腦中風、癲癇..等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李國瑋醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李國瑋醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=529&dept_code=1000'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/ZJeCW_NbGAjLWMKf6tahyBjv3eQddW9M2rABHJa379QEw5IOVSHIvgH4P7CIwpvnCa45QjLUFlf41uMCynAk0QfbaEq27w9c0nc4zk-eL8YgY0ixZ4TjRlr4VHgvDgDX7_O2w3ZK5w=w400',
                        title='洪志憲醫師/神經內科-7/9',
                        text='高雄醫學大學附設醫院神經部主治醫師。[臨床專業]:一般神經內科、腦中風、頭痛.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介洪志憲醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號洪志憲醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=360&dept_code=1000'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
                    # CarouselColumn(
                    #     image_aspect_ratio='square',
                    #     imageSize='contain',
                    #     thumbnail_image_url='https://lh3.googleusercontent.com/g2te0mJ0n1mspADpyC3rR8m_sBfG0l1Q7p39nsCEbSHLoUor3-31dHnaX-lZsWUfxlt5XjGJ_PiC23e7SQhxs2X9_bRWncN5qznHztLEtiEVhDrXAIuYOyjcIf9xG37iINXAMsfHtg=w400',
                    #     title='蔡君儀醫師/神經內科-8/9',
                    #     text='神經內科主治醫師。[臨床專業]:一般神經內科、腦中風、睡眠障礙.等。',
                    #     actions=[
                    #         MessageTemplateAction(
                    #             label='醫師簡介',
                    #             text='簡介蔡君儀醫師'
                    #         ),
                    #         MessageTemplateAction(
                    #             label='門診掛號',
                    #             text='掛號蔡君儀醫師'
                    #         ),
                    #         URITemplateAction(
                    #             label='個人網頁',
                    #             uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=489&dept_code=1000'
                    #         )                            
                    #     ]
                    # ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/TaTH85FgKpRvwKP3IXuzW_-celdAxO4XwhP6U980fQOGV-qxSZ73pRlxal9w18muEmzvQajlqL_pJJtIqOi0ZiDp-k8fgLwX5pXRUCSjSbKwA38qzOPoT8GSFsiWOcwNFICpNN4IqA=w400',
                        title='林子超醫師/神經內科-9/9',
                        text='小港醫院神經科主治醫師。[臨床專業]:一般神經科、腦中風、癲癇.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林子超醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林子超醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=480&dept_code=1000'
                            )                            
                        ]
                    ) 
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0    
#############################  失智症整合門診 #################################   
    elif user_message.find('掛號失智症整合門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號智症整合門診',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/b4EHC2xsHBxG4d0PdkrcZyIXct8gNbGQZEVigBOsub9W1if3CxZJZ6fE3w-0cV_vq1q4NCr_7YrTvnIci97l0pCJY9Ksz2YWBQfjikrmfP0-GWipV2OHV7KL9-xRoDzLAdjwsTDktA=w400',
                        title='陳俊鴻醫師/神經內科-1/4',
                        text='小港醫院神經科主治醫師、神經科主任。[臨床專業]:神經學、腦中風、神經重症.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳俊鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳俊鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=389&dept_code=1000'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/037SWWjFZiBxIsL-pIF4rmCugpMDNr70b-hfPOiY7UM1rVpybYYmPktAHJxgjnUOQ_sjUVBqqLI3C_Ahy0IFG2tpWNikByLSJ2Oj68hW3-saFLccx4REZbloLaq6072Qo7KSBdem3Q=w400',
                        title='劉立民醫師/神經內科-2/4',
                        text='高醫大附設醫院神經部主治醫師。[臨床專業]:帕金森氏症、不自主運動、肉毒桿菌注射、癲癇、自律神經功能失調.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉立民醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉立民醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=184&dept_code=1000'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/opYpAIhHVT2IkpzENoLUN_EX77f5BaIKqjYattqq0Af9dsyAQkwny0CIjEExWl6Ff2BjRVLzj9xmtdC_h1ea-NDLKtP-J8cEyuqWvIZ6O9ALdnNzQshALTaOGF2azlYrXq0Fpj-jZw=w400',
                        title='謝升文醫師/神經內科-3/4',
                        text='小港醫院神經科主治醫師。[臨床專業]:一般神經科、腦中風、睡眠障礙.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介謝升文醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號謝升文醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=299&dept_code=1000'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/rhk9yWnPGcucJ3RhDnk8ScrVZxgTBYluXemYOd6TlEIGM0wMeCAlCdYqYd_WaDo8WloJTWI2qbLScg05LkvUdmyJ5XXs29yQXGensOFdgPbn70jN6vA2yL2MCjs5iSXpPnV9CRhiXQ=w400',
                        title='黃柏穎醫師/神經內科-4/4',
                        text='小港醫院神經科主治醫師。[臨床專業]:一般神經學、腦中風、神經科急重症、生物資訊.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃柏穎醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃柏穎醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=320&dept_code=1000'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                      
############################  內分泌科掛號 ################################## 
    elif user_message.find('掛號內分泌科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號內分泌內科',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/KlRjhYj-AJB7Ol6FIZu-boNd8HwGwvi24Q7GT5uRRRMbBdDdvxHQ6TmcAEGp5cpdGPZIhGC7PW06a0IytaMXRiS3xqoDkK3SRt-C4u2zJap7zltN8mo2O7oRCnCJMnspMxql54xgsw=w400',
                        title='李美月醫師/內分泌內科-1/3',
                        text='高雄醫學大學附設醫院內分泌新陳代謝內科 主任/主治醫師。[臨床專業]:糖尿病、高脂血症、腎上腺疾病、甲狀腺疾病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李美月醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李美月醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=274&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/YXtXTbCF2vf0zxAqcMF4M4OpRzTz9ujsPRxJTieFhaZmOuNJWvROS90sQiU6W0KHYVHoKwzToEquSyn7ImmPCTz25QkjjHu0eUiPKI49ngjWeiKGqRCKiGCFMLidFZYivmGGtNX0PA=w400',
                        title='徐瑋壕醫師/內分泌內科-2/3',
                        text='小港醫院內分泌新陳代謝內科主治醫師。[臨床專業]:糖尿病、高脂血症、甲狀腺疾病、新陳代謝症候群、腎上腺疾病.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介徐瑋壕醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號徐瑋壕醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=393&dept_code=0100'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/jME_kr95xX52JMbplxRBONky_ehlhr2LUiOZQJBW1LmnibLuTmT7dsIv1CZGLSW2WDcKHzFEKLY-IgGoz1vooiZwPxABj8WRVliPxNMnv_H4VNHh5__6DwQ1bNZOr9ijjM_t4fJClg=w400',
                        title='溫緯倫醫師/內分泌內科-3/3',
                        text='小港醫院內分泌新陳代謝內科主治醫師。[臨床專業]:糖尿病、高血壓、高脂血症、甲狀腺疾病、內分泌疾病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介溫緯倫醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號溫緯倫醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=541&dept_code=0100'
                            )                            
                        ]
                    )                     
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0  
############################# 心臟內科掛號 ####################################
    elif user_message.find('掛號心臟內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號心臟血管內科',
            template=CarouselTemplate(
                columns=[
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/_ffyuDg1SUAqNk6M7sxK95BXP4etYNzn4fi9iupKUNcVsHwVc8Ul8n_DpBhIuifEfYKqrOKbuqcHpvADnWNSl_OKEr1Zzpkmr20Adkm0SO5xxfHrlSmJFvfu6ts08eWYiQcfWt4n2A=w400',
                        title='蘇河名醫師/心臟血管內科-1/7',
                        text='小港醫院內科主任/主治醫師。[臨床專業]:心肌梗塞,高血壓,心臟衰竭,心律不整,胸痛,心悸,狹心症.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介蘇河名醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號蘇河名醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=196&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/GpeT0zPKxxpYu0mn0AllbLeMhO2901FZQ3hzCEkWlool5kPaR1z7jV8aT2BZ2Kobc_OZpBNYYYOK2jybGglVL7C59URkb-AXjWVY6XSkrQptEqBBomLJW48h58Yb3DFIA4aDeNGS_w=w400',
                        title='陳盈志醫師/心臟血管內科-2/7',
                        text='心臟血管內科主治醫師。[臨床專業]:胸悶、胸痛、心悸、心律不整、高血壓、心臟衰竭、心絞痛、冠狀動脈疾病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳盈志醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳盈志醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=483&dept_code=0100'
                            )                            
                        ]
                    ),
  
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/xlR-dB06epEtEtGx9UZZBOA8zVo8uQcgvkP4p5FRBhlkH2TaL6hpHt0RvBximHZqXQvoXsDWjQKGtA1lxfsOtw5ik-xCqLGrSYLh578JhcDipuPWE9BD3bSkL-LRN6ofjDFzJXGKdA=w400',
                        title='李文賢醫師/心臟血管內科-3/7',
                        text='高雄醫學大學附設醫院心臟內科主治醫師。[臨床專業]:心肌梗塞,高血壓,心臟衰竭,心律不整,胸痛,心悸,狹心症.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李文賢醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李文賢醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=223&dept_code=0100'
                            )                            
                        ]
                    ),  
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/P9UqJKJIfVLmVsQEv-pBBo3VIjcKlPTMOyOT8glMUyQ9Mi8xjodHWMpwU_nK_-I149jxbREF2DQCPqiWNAv5t7owS9Tg1sUg2zDIwllGCcbscHh6OfPC2QBa3PI5dRZ4rxHLtIubxg=w400',
                        title='許栢超醫師/心臟血管內科-4/7',
                        text='高醫大附設醫院心臟血管內科主治醫師。[臨床專業]:高血壓、高血脂、心衰竭、心絞痛、心肌梗塞、冠狀動脈疾病、心臟急重症等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介許栢超醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號許栢超醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=262&dept_code=0100'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/A6FvLGFJGJJkqPiKaAJZsnA8RqHgkdSqcspUdrpcSqnKS4kj_Bxfg7jAkChdYj4mDFMdunPqDKuNWFIE8OzeW9TeV9eGQgGRpFY_sFDFxbHMj0Hfm_xlbTktmbZ3f2iuJRV1q7Yu9w=w400',
                        title='李智雄醫師/心臟血管內科-5/7',
                        text='高雄醫學大學附設醫院一般醫學內科主任/主治醫師。[臨床專業]:重症加護醫學、心律不整之電燒治療、心律調節器.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李智雄醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李智雄醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=96&dept_code=0100'
                            )                            
                        ]
                    ),
                    
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/7uH0fF1PlMnfgArZ_Y5YPsahmgVt4B6IcEeUk3v8KCK_o30bNZg7F2ZK8NJOAZSmvPXHfWMie3sSuXliLJQVwRLXldFi1kWlP4-_p3uz_oHcJMFyBxq4LNp9iDzT1naaSVU2d8vjkA=w400',
                        title='顏學偉醫師/心臟血管內科-6/7',
                        text='高醫大附設醫院心臟血管內科主治醫師/心臟加護病房主任。[臨床專業]:高血壓、高血脂症、心血管動脈硬化、心臟衰竭.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介顏學偉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號顏學偉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=192&dept_code=0100'
                            )                            
                        ]
                    ),
                    # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Pa1Ezf3fTwzjDluk6nvbgxp4BDJJzaShvcUEbGYQKcFUawP37rQP6Q7NIX7vT9RhijkcHzpk3Y6pJi4kVauUxCiHhPMZ0J2MAuKL4yGb_FJs0KuAx0t9gB3rckeaTJFQ0OXLROEK7w=w400',
                        title='劉宜學醫師/心臟血管內科-7/7',
                        text='小港醫院心臟內科主治醫師。[臨床專業]:胸悶、心悸、心律不整、高血壓、糖尿病、高血脂、心臟衰竭.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉宜學醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉宜學醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=572&dept_code=0100'
                            )                            
                        ]
                    )
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0
############################-感染內科###########################################
    elif user_message.find('掛號感染內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號感染內科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/pEmuNDRtTrgKOpd-ifO2_2Ncy352gSqPU8t0tIj994TgsS8aBAFuX7c6QwXMmdUyIW84ioxZoOIHPHIGqdjoiqQdRdn_RZR4zdAMLj0uW6TvmfNQxDBuNCZMBrpeN26t-xqgqbIJQQ=w400',
                        title='張科醫師/感染內科-1/2',
                        text='小港醫院感控室主任/感染內科主治醫師。[臨床專業]:一般內科，發燒，感染症，感染控制，抗生素使用.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張科醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張科醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=75&dept_code=0100'
                            )                            
                        ]
                    ),  
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/8sx1tG89278q57ncLwv6mfVNnW5HWdNcAQ10r0mfS18AhOSXAmcQAk4pXBcsK789FUXIpV8SdEe1USTjrQXLW1oXAEDIaJ36f4pEP6-Ub2Vx3OqSgGcwpl6CLPchtpaIVnta-RpfaQ=w400',
                        title='李雋元醫師/感染內科-2/2',
                        text='小港醫院感染內科主治醫師。[臨床專業]:愛滋病學、一般感染症、感染管制.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李雋元醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李雋元醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=517&dept_code=0100'
                            )                            
                        ]
                    )  
                        
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0  
###############################-腎臟內科 ########################################
    elif user_message.find('掛號腎臟內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號腎臟內科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/AuLNpUWaeXL6YQv5nzJpGRJ0ZrsqEN6aSBxMk6LtPfnHWQLgujcScm3KS0cj21FFiFX4hvSazIVqaLgKgJmvgGMj42D2yjyxUvcQmTU1aIjkKwBHxBeTh1zlqe7PIyRuKspEtQHXag=w400',
                        title='陳思嘉醫師/腎臟內科-1/5',
                        text='小港醫院教學研究中心主任/腎臟內科主治醫師。[臨床專業]:血尿, 蛋白尿,急慢性腎衰竭, 尿毒症.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳思嘉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳思嘉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=70&dept_code=0100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/_h4mdVK00UK4s9ETuax8bQVkZvPi0Vck83Oib49pcSm6Ib89yKJ5SJpgzLhFyLKTEqgf3QJ4mi8UIkwaDcHHmYT2GwjciO6ME-fo7BDocOoYrXyCzBdgrjVhOJjuP9akwrZ1ZTQwQg=w400',
                        title='吳珮瑜醫師/腎臟內科-2/5',
                        text='小港醫院腎臟內科主治醫師。[臨床專業]:腎臟疾病、透析、糖尿病、高血壓.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介吳珮瑜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號吳珮瑜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=457&dept_code=0100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/y2lWszF1XM0YKNSkyhaluP5oGgjXKereAU39UvRbPGQFk8afpAEMFloOVs-2qofw-EALXFCuuNRreDfE3sVr4WYashSeZ81VYqBUpb5nhKxYIawGnn2HHouuEEKL2ywAk2QEKCESwg=w400',
                        title='黃俊祺醫師/腎臟內科-3/5',
                        text='小港醫院腎臟內科主治醫師。[臨床專業]:腎臟疾病、透析、糖尿病、高血壓.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃俊祺醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃俊祺醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=334&dept_code=0100'
                            )                            
                        ]
                    ),  
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/LOvLI_r0DzwEvmFEGcynfOcaaKKPAWv-jyiiPUlo8466d73Ls9QUvRF3FJtSEwDM95Wc2fz-8Vt8v54o99XYetAdq1Oejck-MEmu9_TZJat0PTEWXloT4pM-dAqY_hwksY5dxWBguw=w400',
                        title='李政學醫師/腎臟內科-4/5',
                        text='小港醫院內科特約主治醫師。[臨床專業]:急慢性腎衰竭,電解質異常,水腫 ,血尿及蛋白尿,糖尿病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李政學醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李政學醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=79&dept_code=0100'
                            )                            
                        ]
                    ),  
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/piPxDqEA7ZqY_DiPvHlWrQvPR6PzYlU5guWfRkC8dXFrVv11UIgt3OLTB71oFgtjhS6qlYegl6r-V7nAeu7_wQbpWCfCc2fiBEAHltPGh8o-TghwqbHRiKbUSRGdLhps8aWX-YK21g=w400',
                        title='許仲邦醫師/腎臟內科-5/5',
                        text='小港醫院腎臟及內分泌科特約主治醫師。[臨床專業]:腎臟病、高血壓、尿毒、血尿、尿蛋白.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介許仲邦醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號許仲邦醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=445&dept_code=0100'
                            )                            
                        ]
                    )  
                                                                           
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
###########################過敏免疫風濕內科#####################################
    elif user_message.find('掛號過敏免疫風濕內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號過敏免疫風濕內科',
            template = ButtonsTemplate(
                image_aspect_ratio='rectangle',
                thumbnail_image_url='https://lh3.googleusercontent.com/YBLuAcpbQUcnHJgp_Z1iJ3F4Zs3_c-naE07SXmF8QuvT7tY7oaIwPBbeH4zNG_dsRFfAfDicP_wPV5tHmTd2W5KMZ_O_TBL6Zj1AW92dJ2T9F-IdeNAS91V4UIBVhp2t2ujIN47Qtw=w400',
                title='歐燦騰醫師/過敏免疫風濕內科',
                text= '高雄醫學大學附設醫院過敏免疫風濕內科主治醫師。[臨床專業]:各種過敏性疾病、僵直性脊椎炎、乾癬性關節炎、反應性關節炎.等',
                actions= [
                    MessageTemplateAction(
                        label= '醫師簡介',
                        text='簡介歐燦騰醫師'
                        ),
                    MessageTemplateAction(
                        label= '門診掛號',
                        text= '掛號歐燦騰醫師'
                        ),
                    URITemplateAction(
                        label= '個人網頁',
                        uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=6&dept_code=0100'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
############################血液腫瘤內科 ######################################
    elif user_message.find('掛號血液腫瘤內科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號血液腫瘤內科',
            template = ButtonsTemplate(
                image_aspect_ratio='rectangle',
                thumbnail_image_url='https://lh3.googleusercontent.com/pp1LzNzq9ZMdZlggLA7o30q25-OdVkFyfg3TvFGVnaCKNAo8cbKYLjSQwGxuem8Mt1Pr8HSwqpqWKk4VIr_dY1XfsKNRYEra4hUHiMSXSBQ3BsBqb-VjC0S-ojZfAuCURMypXwu8Bg=w400',
                title='謝絜羽醫師/血液腫瘤內科',
                text= '高雄醫學大學附設醫院血液腫瘤內科總醫師。[臨床專業]:血液疾病、癌症治療.等',
                actions= [
                    MessageTemplateAction(
                        label= '醫師簡介',
                        text='簡介謝絜羽醫師'
                        ),
                    MessageTemplateAction(
                        label= '門診掛號',
                        text= '掛號謝絜羽醫師'
                        ),
                    URITemplateAction(
                        label= '個人網頁',
                        uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=547&dept_code=0100'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0       
#################################腦神經外科####################################
    elif user_message.find('掛號腦神經外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號腦神經外科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/nmQA9RbAsW9z11ANQPIpsZqg9tkQd4JeP1rqNx5Ds-dz8ZZXQUvbvUxvTetKTiTax8l12KKTKOWlHyC698JfOm6gajjC0tRXCnDqa3b0ogibq2MzVcp07wic0REF8N6chu84oaurEQ=w400',
                        title='鍾嘉勵醫師/腦神經外科-1/3',
                        text='小港醫院外科加護病房主任/腦神經外科主治醫師。[臨床專業]:神經外科，包含各類腦部及脊椎手術.',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介鍾嘉勵醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號鍾嘉勵醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=142&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Qf4VTXLZ__cM-yI6cF851NkxYVttVjE8ZJtVHgN9XwWI4WG1OOyDFfbm2byyKYZhQ8MYaFnAQ1qolEcKSCGsya2Azz47GQegtk3BGmzBwgJiNLxOC_mL55T2qdQau0ryTeigcYT0MA=w400',
                        title='吳東軒醫師/腦神經外科-2/3',
                        text='小港神經外科主治醫師/外科加護病房主治醫師。[臨床專業]:頭部外傷、腦出血、腦腫瘤、骨刺、坐骨神經痛.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介吳東軒醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號吳東軒醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=435&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/B2BWDbJaknoVq3ORqVVJXlMjgE10BB2Ea9gzRKEih1fNWSc9iN9FB1rnIjkwXn6t0lg2PkDYp0uxIHJZOGf6rK86pCOeOJTlhOjxD1Bx7l0TP5xR1DEcikHuyxL99_S1crcYMWXm7A=w400',
                        title='林奕呈醫師/腦神經外科-3/3',
                        text='高雄醫學大學附設醫院神經外科住院醫師。[臨床專業]:一般神經外科、疼痛科、脊椎外科、各種疼痛、骨刺.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林奕呈醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林奕呈醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=503&dept_code=0200'
                            )                            
                        ]
                    ),  
                                 
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
#############################心臟血管外科######################################
    elif user_message.find('掛號心血管外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號心臟血管外科',
            template = ButtonsTemplate(
                image_aspect_ratio='rectangle',
                thumbnail_image_url='https://lh3.googleusercontent.com/pzFRVdP-Unsx3o5diayVJJx7jYEgTfYqOQee_vmvGolhmAuHZzndhsb1WAWdx3fH-L08s3YXgcysG_4I5wFrdzJE-Uru2LfTX6GsYwMYEkMN8hN9-pJxqyvxuVNKOsWK7w79KV5BYw=w400',
                title='謝炯昭醫師/心臟血管外科',
                text= '高雄醫學大學附設醫院心臟外科主任。',
                actions= [
                    MessageTemplateAction(
                        label= '醫師簡介',
                        text='簡介謝炯昭醫師'
                        ),
                    MessageTemplateAction(
                        label= '門診掛號',
                        text= '掛號謝炯昭醫師'
                        ),
                    URITemplateAction(
                        label= '個人網頁',
                        uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=194&dept_code=0200'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
##############################胸腔外科#########################################
    elif user_message.find('掛號胸腔外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號胸腔外科',
            template = ButtonsTemplate(
                image_aspect_ratio='rectangle',
                thumbnail_image_url='https://lh3.googleusercontent.com/jzLjUc_96SxdxOP-EAhTsXY2rwE67PHqyD0mekSRqWGY4OA_3MtjrOBX_zApNNx_FbK13ju9olubGCq2v7awTbZyizFJpxa3Ov7N25QGvBOUWTX5PPZ7fF5_TFjrj249ZvxuP12pQA=w400',
                title='蔡東霖醫師/胸腔外科',
                text= '小港醫院胸腔外科主治醫師。[臨床專業]:胸部外傷，胸腔疾病，胃食道逆流，吞嚥困難，內視鏡手術.等。',
                actions= [
                    MessageTemplateAction(
                        label= '醫師簡介',
                        text='簡介蔡東霖醫師'
                        ),
                    MessageTemplateAction(
                        label= '門診掛號',
                        text= '掛號蔡東霖醫師'
                        ),
                    URITemplateAction(
                        label= '個人網頁',
                        uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=455&dept_code=0200'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
#################################胃腸及一般外科#################################
    elif user_message.find('掛號胃腸一般外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號胃腸一般外科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/-7PBHcUN4n8suqTCCX55l9-6W3isrzA6jyawlNTUnApULYRkBXcxQMYFlsye4wpVIqq18dmw4uVY-Av4A6krLEwPnmMNjRhvsKXkvPiATIPBYGFE8CVVXTLA78zWBJ1a0X9BHm6jSg=w400',
                        title='莊捷翰醫師/胃腸及一般外科-1/5',
                        text='小港醫院 外科主任。[臨床專業]:大腸癌,乳癌 ,甲狀腺癌,胃癌,疝氣手術 ,腹腔鏡手術.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介莊捷翰醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號莊捷翰醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=152&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/FFK12LynN9KIG1Z7oDNW8XlPm3k5fnHiJUDDO78qv4XojTex0zALdKssap5fXW55Nir_vWRpKq4xkQFIlewIPNy3GoUhy2RSMyKZ8_wJaaWupDUDqhV2Pdhi-3ND75o6d-XRv8AwYQ=w400',
                        title='黃建偉醫師/胃腸及一般外科-2/5',
                        text='小港醫院肝膽胰外科主治醫師。[臨床專業]:腹腔鏡膽囊切除手術，腹腔鏡總膽管截石手術、肝胰脾臟腫瘤切除手術。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃建偉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃建偉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=450&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/_4vG9SjRGI6wKMWEWaUU7MLcsuZdxFrThCIf7hHGU1hRILWz2tVz8DzUqtD8ah1M4wrT_yiziIKVQmskCjVu1jMe1D0vsouDyup-6Zz_4mBcxsaJpQpexU7eqkxwWqsMTet-fWEWNQ=w400',
                        title='陳映哲醫師/胃腸及一般外科-3/5',
                        text='小港醫院外科主治醫師/衛福部屏東醫院胃腸及一般外科主治醫師。[臨床專業]:大腸直腸癌、胃癌、痔瘡、甲狀腺、等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳映哲醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳映哲醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=454&dept_code=0200'
                            )                            
                        ]
                    ),  
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Mu32LbDv5zwcioMAxlL3nXcmYpn1TZgpASVkMOcy8YJ27-aRQiqVVebVfVlhgt41FD3a9RCJ6cd1DgEYDYGyBaAl3UpnVSRHp7RmyxcuCiI4T64pZbqScalpo5tMznPGudioOtjuHg=w400',
                        title='蘇家弘醫師/胃腸及一般外科-4/5',
                        text='小港醫院外科主治醫師。[臨床專業]:大腸直腸外科、消化外科、內分泌外科、疝氣、乳房外科、直腸肛門手術、等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介蘇家弘醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號蘇家弘醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=398&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/qJCZ9jPTGisMour1xz6rHdTtnFVEYGZAyLsWwCI8YVYSn0EnnFC1ovFwJi0_EmEpKoK9ik6F9koiftyURABnrYh1Humi1Yp6XO-_TUZ0106dKOOa-ExxOK-zDXaG1mauJjfJidKyeQ=w400',
                        title='陳伯榕醫師/胃腸及一般外科-5/5',
                        text='小港醫院外科主治醫師。[臨床專業]:胃腸道手術、大腸直腸手術、腹腔鏡手術、疝氣修補手術、等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳伯榕醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳伯榕醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=497&dept_code=0200'
                            )                            
                        ]
                    )                                    
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
##############################乳房外科#########################################
    elif user_message.find('掛號乳房外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號乳房外科',
            template = ButtonsTemplate(
                image_aspect_ratio='rectangle',
                thumbnail_image_url='https://lh3.googleusercontent.com/-7PBHcUN4n8suqTCCX55l9-6W3isrzA6jyawlNTUnApULYRkBXcxQMYFlsye4wpVIqq18dmw4uVY-Av4A6krLEwPnmMNjRhvsKXkvPiATIPBYGFE8CVVXTLA78zWBJ1a0X9BHm6jSg=w400',
                title='莊捷翰醫師/胃腸及一般外科',
                text= '小港醫院 外科主任。[臨床專業]:大腸癌,乳癌 ,甲狀腺癌,胃癌,疝氣手術 ,腹腔鏡手術.等。',
                actions= [
                    MessageTemplateAction(
                        label= '醫師簡介',
                        text='簡介莊捷翰醫師'
                        ),
                    MessageTemplateAction(
                        label= '門診掛號',
                        text= '掛號莊捷翰醫師'
                        ),
                    URITemplateAction(
                        label= '個人網頁',
                        uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=152&dept_code=0200'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
#################################整形外科######################################
    elif user_message.find('掛號整形外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號整形外科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/PipgUg0iAE-MTaFP0TChFSdtkYnH6gCas2BUKNSajXe7ZKghnuWwproF4lOCLiYFLaFZJ2nxJebC5S22sapK2PMGxuwDF1vv7qNxfRq3WBGc6MihmMLM2jYMmcEwtgkTsEz4NFVKhQ=w400',
                        title='李書欣醫師/整形外科-1/5',
                        text='小港醫院副院長/小港醫院外科主任。[臨床專業]:整形外科、美容外科顏、面創傷及顱顏外科、燒傷.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李書欣醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李書欣醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=570&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/dszOY-0_hWKzvpOk2qnm0W0-6SNAhNkrJugtZ15CiigVIP6SN8pJBH38XaFgcFwVGEcNfD5kQ58ynSfl583iLB9x9SteUTnvznJl824Ab3fi7BgWeuVXhigzcCwPoqDwSuVedYCHgA=w400',
                        title='林運男醫師/整形外科-2/5',
                        text='小港醫院外科主治醫師。[臨床專業]:癌症術後重建手術、乳癌術後乳房重建手術、內視鏡輔助移除靜脈曲張手術、等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林運男醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林運男醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=433&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/B-5CUTdtFKa6PmKC8d0Dk6-59zmWUzDLmy-0OVp-GHeMZKqsuKVJmObRYp78ExbnqyS2w8L7JdajD_H24R9dZGCh-iKTkC30Jq6VDZWlq2v__wpncnNq4lVoo8eXauw7fZKhzaEjOg=w400',
                        title='蔡明哲醫師/整形外科-3/5',
                        text='小港醫院外科主治醫師。[臨床專業]:整形外科、手外科、頭頸部腫瘤切除後重建、四肢疼痛性疤痕脂肪移植.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介蔡明哲醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號蔡明哲醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=458&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/cXdyOBGuIFfJYCylzkkgb0kWmvTuAn47fQMPEj99AJD8fgjspfQ-cgXR0uQELCKnJRtuZFEIM3A8kzen2gWlzTTGa_0mrD0yvj6S5ULquXVbf7Acmb0sI1nPPHCoJjs9tZVBMkzaCA=w400',
                        title='李孝貞醫師/整形外科-4/5',
                        text='高雄醫學大學附設醫院整形外科主治醫師。[臨床專業]:整形外科、美容外科.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李孝貞醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李孝貞醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=525&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/sr1MMpR6oafDsyfrHGo57ZCkNhHVSbQMTz5dlVVh_nc6WfdECJnuWmvkPRSDJMCBEKxV-CKk0m8YUQugwpf8t8RG77CBjyzIrx544Hi4oE9E8rf7LjHdImoYKm58yo_fbIUmkWwiYQ=w400',
                        title='楊錦江醫師/整形外科-5/5',
                        text='小港醫院整形外科特約醫師。[臨床專業]:整形外科、美容外科、燒傷、手外科、外科雷射手術、皮膚雷射整容.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊錦江醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊錦江醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=48&dept_code=0200'
                            )                            
                        ]
                    ),
                                                                                                                                 
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
#################################自費美容門診####################################
    elif user_message.find('掛號自費美容門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號自費美容門診',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/dszOY-0_hWKzvpOk2qnm0W0-6SNAhNkrJugtZ15CiigVIP6SN8pJBH38XaFgcFwVGEcNfD5kQ58ynSfl583iLB9x9SteUTnvznJl824Ab3fi7BgWeuVXhigzcCwPoqDwSuVedYCHgA=w400',
                        title='林運男醫師/自費美容門診-1/2',
                        text='小港醫院外科主治醫師。[臨床專業]:癌症術後重建手術、乳癌術後乳房重建手術、內視鏡輔助移除靜脈曲張手術、等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林運男醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林運男醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=433&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/dVj05JuUS9yauwGRTYNxsRAiC4tWjZaTjwA8ou800mTcfNhSjIgu3ytYKmg1aeq1awHZNczb5CHI3i6cAz4MKmwuhupQ9WuhO3RdF-Ezhn9QyzXhIVDa73uzQt6GQeHTZFSs7YDcjw=w400',
                        title='林幸道醫師/自費美容門診-2/2',
                        text='高雄醫學大學附設醫院整形外科顧問醫師/高雄醫學大學名譽教授。[臨床專業]:整形外科、美容外科顏、自體脂肪乳房重建.。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林幸道醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林幸道醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=463&dept_code=0200'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
###############################################################################    
    elif user_message.find('掛號耳鼻喉科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號耳鼻喉頭頸外科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/94sCt-OamCmsuVO-jZyvjVif_zQFdsjdyd7-ZNQtR1ORfb_DnAfGQyKZX7HwLenElG8sSX4HQiAJG3c9EktosDml-ExKTuU3OXAw_HMoT2ovLaWh6sB_7rQerVuhX4ZsANpqJ9H9gA=w400',
                        title='吳哲維醫師/耳鼻喉頭頸外科-1/10',
                        text='小港醫院耳鼻喉科主任/耳鼻喉部主治醫師。[臨床專業]:頭頸部癌症治療及手術 (鼻咽癌、口腔咽喉癌、頸部腫塊).',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介吳哲維醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號吳哲維醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=272&dept_code=0600'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/nJibWAVJjxMOBvKhsZYAJOBXj9rLqbxX5nyBQVIfmfmOXefGyEEdeGDkAjB0t_WeNYwQDxEVknv2nzvsMDguDIelB2zwAG9J91V7kpX_oUkoOKP5sbZ9xtD8kMdR7gamWEH3N0oh9Q=w400',
                        title='簡禎佑醫師/耳鼻喉頭頸外科-2/10',
                        text='高雄醫學大學附設醫院耳鼻喉部主治醫師。[臨床專業]:聽力障礙、耳科疾病、眩暈及平衡疾病.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介簡禎佑醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號簡禎佑醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=535&dept_code=0600'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/cXdyOBGuIFfJYCylzkkgb0kWmvTuAn47fQMPEj99AJD8fgjspfQ-cgXR0uQELCKnJRtuZFEIM3A8kzen2gWlzTTGa_0mrD0yvj6S5ULquXVbf7Acmb0sI1nPPHCoJjs9tZVBMkzaCA=w400',
                        title='柯皓允醫師/耳鼻喉頭頸外科-3/10',
                        text='高雄醫學大學附設中和醫院 主治醫師。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介柯皓允醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號柯皓允醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=571&dept_code=0600'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/lygDJqgZUocQHtTS6Nepn4jnTmiouF5vcgl-FLA3xC13XX-9tk-zY1wDe1aRc6bl2U_1XE2NStpR_j8yCu_WKr5o0uCbbCIyNSKGyhFYbtBfXHeRpcWdbL37y1QcodcIYfprIF4cfw=w400',
                        title='劉承信醫師/耳鼻喉頭頸外科-4/10',
                        text='高雄醫學大學附設小港醫院 主治醫師。[臨床專業]:鼻部、甲狀腺、喉部、睡眠頭頸部腫瘤、一般耳鼻喉科疾病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉承信醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉承信醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=565&dept_code=0600'
                            )                            
                        ]
                    ), 
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/z6PdHa-PaCJmLSnVnANhchpa7Zimzfa3nvTxF7G79fDg2ngrqazdXxWVbNa_DE89b8XziogPY1TA8vX_uNNkDMbxC4Ru8qSutRk4-aKyvNf9AcyLS2d4Zhcu7hc2gYR4J03ri8THXw=w400',
                        title='林漢琛醫師/耳鼻喉頭頸外科-5/10',
                        text='高雄醫學大學附設醫院耳鼻喉科總醫師。[臨床專業]:口腔癌、頭頸部癌症、鼻整形、鼻外傷重建.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林漢琛醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林漢琛醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=513&dept_code=0600'
                            )                            
                        ]
                    ),   
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/1LVW7s1dsuWRcwVy08tWYrd7YTMEbJFUvFQZgOKJf1ouJ0HlWmeQSLVihG-oAwG3Msz1fS2DNn9ejjv9J3uMjA9lELuCwK_O0DrMxqDQDDBnG2xogiT6mp8Ckci3oaPmolimOgMROQ=w400',
                        title='曾馨儀醫師/耳鼻喉頭頸外科-6/10',
                        text='高雄醫學大學附設醫院耳鼻喉科總醫師。[臨床專業]:喉科疾病、頭頸部癌症、睡眠障礙、一般耳鼻喉科疾病.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾馨儀醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾馨儀醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=537&dept_code=0600'
                            )                            
                        ]
                    ), 
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/PIaPftDKdx7m-NUpjgjMkhwjZrTRxYEUu-nsOoK3-qJO-vRfDq80bgtQP1wN-xVj_DmEJj5bqtyrlMlI5Eiuh9G_KSOtmAifK7vudrkNSRPzGhIiaBOErqr6c8LcBIFWvxlqt68-GA=w400',
                        title='戴志峰醫師/耳鼻喉頭頸外科-7/10',
                        text='小港醫院耳鼻喉科主治醫師。[臨床專業]:過敏性鼻炎、鼻竇炎、鼻內視鏡手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介戴志峰醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號戴志峰醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=72&dept_code=0600'
                            )                            
                        ]
                    ), 
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/kg15aDvGXdqzaoDr1eSL0CyhTnjEJYZIavUoVEtqhtseXj52rlLokl_98vTTewCS3E5dfa6kCA1IU4bkfuB2h9StpFV6VtT8IZJCrHLm162RhsMnMup_yICWYVeka8G-75ALEGEwgQ=w400',
                        title='曾良鵬醫師/耳鼻喉頭頸外科-8/10',
                        text='高雄醫學大學附設醫院耳鼻喉科主治醫師。[臨床專業]:頭頸 部腫塊、聲音沙啞、鼻腔與鼻竇疾病及一般耳鼻喉疾病..',                    
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾良鵬醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾良鵬醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=249&dept_code=0600'
                            )                            
                        ]
                    ), 
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/DmFEByRFrqhEfsUm7kNRDq63Y_dzSQIyo9hAQ1bVoRt5jFrBg4FNspJpOsW7HR-7PSMGCQV5eUdZt5ImcIdnfd0Z3z8h4fY8j285esUX9cQDvR31GVrKGTsiW03hUNF0E7z4lZ4vGA=w400',
                        title='張寧家醫師/耳鼻喉頭頸外科-9/10',
                        text='小港醫院耳鼻喉科主治醫師。[臨床專業]:耳部疾病、鼻部疾病、咽喉疾病聽力障礙 ...',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張寧家醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張寧家醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=271&dept_code=0600'
                            )                            
                        ]
                    ), 
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/g6OuwhISsikSSzXJ5TxoqzjVrDYceIVqOCXvKwJdzDvWsDHCMZLIQEIEAPUpGWOgT7MmApKb04UwqMqEa4BI5TaDF_twDHqKUB8-m8EXVfrIF3qFpFsoWwKM8dbhpnaLplvmzygyug=w400',
                        title='王遜模醫師/耳鼻喉頭頸外科-10/10',
                        text='高雄醫學大學附設醫院耳鼻喉科醫師。[臨床專業]:一般耳鼻喉疾病、聽力障礙疾病、耳科疾病、眩暈及平衡障礙疾病..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王遜模醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王遜模醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=461&dept_code=0600'
                            )                            
                        ]
                    ),                                                                                                                             
#------------------------------------------------------------------------------
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
#########################  婦產科 ############################################    
    elif user_message.find('掛號婦產科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號婦產科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/j7m_Nta9CV3wnytwqGfZAaTQBfHxv2hr1DO0UpxK4NknJHD25CO8q8DW6_kVXbqJTsX_vVu6ekeZrm7CAwNhmDApKiavek8SOoU4APFEA15yHWeZMQfJhO_FYQPcQH2N4Nw7OYK8tw=w400',
                        title='陳永鴻醫師/婦產科-1/6',
                        text='小港醫院院長室秘書/高雄醫學大學婦產科主治醫師。[臨床專業]:高危險妊娠、腹腔鏡手術、陰道雷射..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳永鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳永鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=138&dept_code=0300'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/zky3n1QGIs2JWKMY-X9NuKCBNNjf7u2NgesD1uSznlKooDsKQ4pSY9GhVduecv4e_q4m75JlfRD7gY_McAbAvdh_HZ1c5YUIXFR2UA8oNT8o13zqLLmHaa51xaEbki80yB9UW6qk7Q=w400',
                        title='王秋麟醫師/婦產科-2/6',
                        text='小港醫院婦產科主任/小港醫院婦產科主治醫師。[臨床專業]:不孕症、微無創手術、腹腔鏡檢查及手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王秋麟醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王秋麟醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=40&dept_code=0300'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/PRU3ruIj71vtcGRoSd2mBulJOEmlvalTf4KUfzEzXQeD8Vaw2_4NCXdFXD1n5iTywh_AREFJKhA-4kW4QqqidR67CgqJ54N10h9Dx-Rvp-PaHnTij27FONRUprGUZFIZ5OamNi9wWw=w400',
                        title='龍震宇醫師/婦產科-3/6',
                        text='高雄醫學大學婦產部部長/主治醫師。[臨床專業]:婦女子宮膀胱脫垂、婦科手術、陰道雷射、海扶刀子宮肌瘤消融手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介龍震宇醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號龍震宇醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=164&dept_code=0300'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/f9iapvDgBFz-S5u3NBsyQaCW4WTtsin1DhLGe55pLuladAPoQbeauSZgeYyBPvUILiz4z4oKSnS4Of_SvcMiN4njnSwIIYyto-vbeTKvLB2tai6BXjh_yP0Ap1QtFjhJju4TaHgNGA=w400',
                        title='劉奕吟醫師/婦產科-4/6',
                        text='台灣婦產科醫學會專科醫師。[臨床專業]一般婦科、產科、婦女骨盆器官脫垂及尿失禁、陰道雷射、、腹腔鏡及子宮鏡手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉奕吟醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉奕吟醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=507&dept_code=0300'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/vsO4EAYqcETb69MvAgJ-o_VX_omyWaU0mm1NhdPk-OD1crpDvub5aP6VMz_qAavl3MGhTfhtErnKJ9DGYyzkfLsSkqmBb18gAA-anLfZO7Hnr2B0aMoq-UV0hkoXHNPU1r5dG4I81w=w400',
                        title='張慧名醫師/婦產科-5/6',
                        text='小港醫院婦產科主治醫師。[臨床專業]:一般婦科、陰道雷射..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張慧名醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張慧名醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=403&dept_code=0300'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Zp7w9GrQtfnnDpRJ1eGoFEtAsrCle4BZ02q5Mlom3Trk5B91J4ohcc473QlAO815n6tx7dq52FXbuItORa1CzmTeCnrDhiQoSlMP7aUwZ3rN8Zcx65MaTLdsb5vrrTLqhFkTabbOvQ=w400',
                        title='方嘉宏醫師/婦產科-6/6',
                        text='小港醫院婦產科特約主治醫師。[臨床專業]:產科高層次超音波、婦科腹腔鏡手術、婦科腫瘤手術、不孕症檢查及治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介方嘉宏醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號方嘉宏醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=555&dept_code=0300'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                     
##############################胸腔外科#####################################
    elif user_message.find('掛號更年期特診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號更年期特診',
            template = ButtonsTemplate(
                image_aspect_ratio='rectangle',
                thumbnail_image_url='https://lh3.googleusercontent.com/vsO4EAYqcETb69MvAgJ-o_VX_omyWaU0mm1NhdPk-OD1crpDvub5aP6VMz_qAavl3MGhTfhtErnKJ9DGYyzkfLsSkqmBb18gAA-anLfZO7Hnr2B0aMoq-UV0hkoXHNPU1r5dG4I81w=w400',
                title='張慧名醫師/更年期特診',
                text= '小港醫院婦產科主治醫師。[臨床專業]:一般婦科、陰道雷射..',
                actions= [
                    MessageTemplateAction(
                        label= '醫師簡介',
                        text='簡介張慧名醫師'
                        ),
                    MessageTemplateAction(
                        label= '門診掛號',
                        text= '掛號張慧名醫師'
                        ),
                    URITemplateAction(
                        label= '個人網頁',
                        uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=403&dept_code=0300'
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
########################### 小兒科  ###########################
    elif user_message.find('掛號小兒科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號小兒科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/KwfDct7_L6U64l-3ulVX4grDCic279lOFlHzvxyo_OAW2VwtXeZh4BsgIeFDAGZf7V01OGviaC3M0UHAXeEyenIZQLfaiVYbmlR8_F5Jku2aNnEFBEwWLA975UAIx1giMaNnfq9wzg=w400',
                        title='洪志興醫師/小兒科-1/10',
                        text='小港醫院副院長/小兒過敏及免疫科主治醫師。[臨床專業]:過敏學、免疫學、小兒科學...',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介洪志興醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號洪志興醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=244&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/NDmykOQph0_ue_6qhoKXEqTPaY9TJgKuSqFItckxDPD4-AxJtJsTqVC3ATavj4Jd9wAvtrpugM2IA0gNGKKLEliZp8CRPvUsXYNnICZgDrgGj3zKtRGh2LbNcwapFPerWzCJU8G_fQ=w400',
                        title='李雅婷醫師/小兒科-2/10',
                        text='小港醫院小兒科主任/小兒科主治醫師。[臨床專業]:發燒、咳嗽、腹痛、腹瀉、嘔吐、食慾不佳、健康檢查..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李雅婷醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李雅婷醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=78&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/AY7tPi5iEIkdFsOt2VITYd7f-eoH6gQ964LTzTtY5m4eXPx5l2umh5IzSaf1JL5sZtuq6yWMJim0zJzFt1OTOcOcajc5xAxM8P3hPu2NQCEnds8fMRVYRdO8irYio6f3PBTyZcuk-Q=w400',
                        title='劉怡慶醫師/小兒科-3/10',
                        text='高雄醫學大學附設醫院小兒科主治醫師。[臨床專業]:小兒專科醫師、小兒心臟血管專科醫師..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉怡慶醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉怡慶醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=465&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/CJGZRhnxVUwuVVukFcLwpLF9HiMqgHaE4gUqMHImTKA3SGY04vZ3xn6rOO0jaV47GWISkCIdx_6BpRcR5xlvyLecKl6bRamGGKTGsj4rIaHy1axi-ecHlV22EaCXRcR64zwHNA19eQ=w400',
                        title='王建華醫師/小兒科-4/10',
                        text='小港醫院主治醫師。[臨床專業]:發燒、咳嗽、腹瀉、嘔吐、食慾不佳、活動力降低、健康檢查..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王建華醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王建華醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=376&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/vFNwdzC7phQkXAWabdigUKHNKb4ooV5F7ESgFMMLSMq-zJcemX0Z-2SGzHHDdyYmV15joQW7Kv4ysSxTFEsUiRhGuYmsVzPUdPPYwjAXul1Q8Jg7eGBBDli8zZVPf72Ewd6KO8TumA=w400',
                        title='林龍昌醫師/小兒科-5/10',
                        text='高雄醫學大學附設醫院小兒科主治醫師。[臨床專業]:發燒、咳嗽、腹瀉、嘔吐、食慾不佳、活動力降低、健康檢查..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林龍昌醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林龍昌醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=173&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/THU0x78muI4bWqxerWtEle78hNcHgO5HPDv6Letq21NPkwVZpid6G3U9yl1uXhZIAK5Mim4oP96Z4IqJZ7eNlRQj6Q92eR0SBcsgIyS6vj_tv-2HDXLPTR2ybOGzNRyvtM4j61ucwQ=w400',
                        title='李威德醫師/小兒科-6/10',
                        text='高雄醫學大學附設醫院小兒科主治醫師。[臨床專業]:新生兒黃疸、早產兒追縱、新生兒疾病、兒童健檢、發燒、咳嗽、腹痛..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李威德醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李威德醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=207&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/zwGbetkrsj9W--A9moDdLPPa2Ne9g5PC_QCkspR057rXgeh9juQdpuRRjBKEUZl-13_D7WHf6Ncg5ynFvjSCqEM1J6scelbyXbnVdbA73IXi0qU7DYxMfL3CMnds3gRqlaXNP30aXg=w400',
                        title='吳晃維醫師/小兒科-7/10',
                        text='小港醫院小兒科主治醫師。[臨床專業]:一般兒科、嬰幼兒預防接種，嬰幼兒身體評估、兒童胸痛、先天性心臟異常..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介吳晃維醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號吳晃維醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=519&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/vEPcy1D1eVvomYYry3Z6EypRWJ_FK_6Z9cLeKJTrrTViz5Io3zcvT1SCCVgl4_v48nTt-6_paAhSfNtvCQWtzWP54QjefMbBePWzPdnNaMrV2uGIZyGBuxaQWAAl1wTgW9-gTIGHXA=w400',
                        title='蕭惠彬醫師/小兒科-8/10',
                        text='高雄醫學大學小兒遺傳及內分泌科主任/小兒科主治醫師。[臨床專業]:內分泌疾病、小兒遺傳疾病及新陳代謝疾病診斷及治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介蕭惠彬醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號蕭惠彬醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=94&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/5ptgKePn9abTd1TrAFVvkuc_huPrBxKRnIpsQNbT8hqlN-9sYRJq6FjSJSD2OAcpZU02fJrnxkRvXSvL5QtUaPuKxNGS7_jxopeMe4izpuK0I4o6SwleAdKnFIiXKNXL5qZjrSB5Xw=w400',
                        title='施相宏醫師/小兒科-9/10',
                        text='高雄醫學大學小兒一般科主任/主治醫師。[臨床專業]:兒童腸胃問題，兒童腹部超音波及內視鏡檢查，小兒黃疸，腹痛，嘔吐..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介施相宏醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號施相宏醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=160&dept_code=0400'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/uwuoXvVcv7Ty28AgWeDUKC3wOgRatuG1eM5-B9BggKnSRXa1gwD4_uBehTUmqQTnKSXxwj1541zDzNaBMZAqFOgWvw_JGbjuEIg5EEBHEKUXBOCAV_i79PO03uQ07EIWc5-DeM31-A=w400',
                        title='王一帆醫師/小兒科-10/10',
                        text='小港醫院小兒科特約醫師。[臨床專業]:發燒、咳嗽、腹痛、腹瀉、嘔吐、食慾不佳、活動力降低、健康檢查..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王一帆醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王一帆醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=30&dept_code=0400'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0   #
########################### 皮膚科  ###########################
    elif user_message.find('掛號皮膚科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號皮膚科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/J0TVfRJV8D1CXRz-ILPFfDYgLOO49qoNmpspUjWuuuxXzemwowYGK7JcYjaqc6-tSDmV63jdHgyXThCJy2ktaxHVnKCdw9PZjgHGVQM4LoABo3C-MNKAg98D9W-stBN2prej1WP7tw=w400',
                        title='胡楚松醫師/皮膚科-1/3',
                        text='小港醫院皮膚科主任/主治醫師。[臨床專業]:一般皮膚科疾病、醫學美容、皮膚腫瘤、異位性皮膚炎..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介胡楚松醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號胡楚松醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=317&dept_code=0900'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EfsFf6KaX3S2ygwovDF624aUEXs6sABNVB2YiNVUpHIABQr4dinw_9QB8_LvM6wBgisZcj5d886N7gJyGBIM9Ed8z16sfgkt7W2vtTjb4Y_hy5Avbc-uin4iFp5-hZaeuPyWeQg-uQ=w400',
                        title='黃子鴻醫師/皮膚科-2/3',
                        text='小港醫院皮膚科主治醫師。[臨床專業]:一般皮膚病、醫學美容、免疫性皮膚病、落髮/禿髮..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃子鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃子鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=533&dept_code=0900'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/rp95aSz67D15gi-LUTKnRMm3SRbhEMUZVqKsxMM9n701RXEmWvPSl914sBXPXmz98iAVJBma7WfDYPkhqwRIDvZAYmhu1QVvXcEG2LczjaRbzZ_897VGtk3UBJWWPRozjZLvUNcCrg=w400',
                        title='楊翔宇醫師/皮膚科-1/3',
                        text='小港醫院皮膚科主治醫師。[臨床專業]:一般皮膚病、美容醫學、落髮/禿髮、過敏及免疫性皮膚疾病..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊翔宇醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊翔宇醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=301&dept_code=0900'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0  
   
########################### 家醫科  ###########################
    elif user_message.find('掛號家醫科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號家醫科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/UNIU-8Tm3JzARxPQkrWFmL3OFrPPvEQWr2CKVUg-i63nHQ648iKkuquY8a2J-lsDqpmnMEKEkezhpV-TtYuPuNBAcbyx6WKrF73fpVRDQyY3ovtxvNW_-WIjcLCaEt0lMetOn11OmQ=w400',
                        title='楊鎮誠醫師/家醫科-1/9',
                        text='小港醫院家庭醫學科主任/職業病科主任。[臨床專業]:預防保健健康管理、家庭醫學(急慢性疾病)、職業醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊鎮誠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊鎮誠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=531&dept_code=1500'
                            )                            
                        ]
                    ),

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/i_mZqe24PxgWrjx_ktzJ20jwaRliTQg-kRda_dnDNLWG6vFzNWhquqcugGBsrl25xBuvMEkZc7UvWhXN22MAVxOsdVKNaeQEg8RqS3MMUZrqMkKKCTySQLOAe-QgMLs3Z0044CRouA=w400',
                        title='蔡惠如醫師/家醫科-2/9',
                        text='小港醫院家醫科兼任主治醫師。[臨床專業]:家庭醫學(急性與慢性疾病)、肥胖醫學、戒菸治療、安寧緩和醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介蔡惠如醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號蔡惠如醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=464&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/7MqyQIv0VH6BnJ_nABp8vUnTfU8bI5uF2SSTGKd9R_4homiO77Nc1HHzJ6SeGDhWtdW_DRCLUTsoOi4NislKBTx2usA1m3KHELItW7dfSNqkSrCyCyPOmr-M0PZcnGw1L1gcpM6YpQ=w400',
                        title='林晴筠醫師/家醫科-3/9',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:慢性疾病(高血壓,高血脂.)、急性疾病、國際旅遊醫學門診、戒菸門診..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林晴筠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林晴筠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=97&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/y89zsZjYtXyIyrT73zPKbt2qn8pJB75HYeZYB0iZmZ1E-uITtsMT1buDR-fmx_QP2byhin6dXG7EFCetMVGSVC-XF5babDJsVDCWbwASTMedTD9NJnLJfXwUM7xeKNqV1hFltwO9ZQ=w400',
                        title='李純瑩醫師/家醫科-4/9',
                        text='高雄醫學大學附設醫院家庭醫學科主任。[臨床專業]:家庭醫學、肥胖醫學、一般內科、老人醫學',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李純瑩醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李純瑩醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=190&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/1SXhSvx7gR3IxpsTl3sz5XB4wPGMJlOzarFVX05-6-lvXIOy91z8rLsWqYY7U1GLRfJpSrh7A2GtvRZLimmMY-XBiBcvJF5MtX7gM3q5gZ9al0WB-vCMPlA_UpNsCHLlTgEC-NMmeg=w400',
                        title='張家禎醫師/家醫科-5/9',
                        text='高雄醫學大學附設醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學，老人醫學，青少年醫學，流行病學，戒菸，減重..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張家禎醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張家禎醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=141&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/5vW23MyXznB0No_3BZvAsF4WR835dTy4eFqgMiJS5lVXUTLT4_NYNBcXwSkodTnSmHjqBIOx_2NaVV5oCjrrYbNPM-D10HoxR-sonn7O0LFxggAQZa1WazvLAVG44Zr3FEDfdGUacg=w400',
                        title='歐明蓉醫師/家醫科-6/9',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學(急性與慢性疾病治療)、預防保健、社區醫學安寧緩和醫學、戒菸治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介歐明蓉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號歐明蓉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=530&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/a8X2y3FbdOVbcpYumx3RixGfI7NVpJRuRxiIVG16NfDwwm9n654kfwrlrvmLlWOs48cI9j5G2cJKEcJHf4hoS4x8Zi7IQPqwdPC8Epr5hkxm668Hr0nIFG6Gqzzl_z-6jMj1D_phTQ=w400',
                        title='王奕淇醫師/家醫科-7/9',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學(急性與慢性疾病治療)、預防醫學、社區醫學、安寧緩和醫學、老年醫學.',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王奕淇醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王奕淇醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=485&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EN5UF1GbgsU_OCDEeDwMuwa0Pf_RiR6ZviCeoD2AExlIOMKzfVe68uHuPfhiw5LK-RN4vqAZIMFH1yEx8unFBUYpBEFGYJHbcVFW4aUf3BihShhSNcC-eHU1PftydaQgTyNoPbly8w=w400',
                        title='曾愉芳醫師/家醫科-8/9',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾愉芳醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾愉芳醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=356&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EqfLEVIvlpjROiYRpAS-fzM_w2Av9yF8-H2vvzlTaAZ_bk8LBpVZ_piKd9r6_fYJMYU3C659U2pTtCZ4Sk3qy52lwKR3MIyT9ZjAwX3yx5wzceRdvbOdIMdDCpSTDz8lEQsfCUq-Fg=w400',
                        title='鄭如君醫師/職業病科-9/9',
                        text='小港醫院/職業病科暨健康管理中心主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介鄭如君醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號鄭如君醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=418&dept_code=1900'
                            )                            
                        ]
                    ),                                                                                                                                                              
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                     
########################### 戒煙門診  ###########################
    elif user_message.find('掛號戒煙門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號家醫科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/UNIU-8Tm3JzARxPQkrWFmL3OFrPPvEQWr2CKVUg-i63nHQ648iKkuquY8a2J-lsDqpmnMEKEkezhpV-TtYuPuNBAcbyx6WKrF73fpVRDQyY3ovtxvNW_-WIjcLCaEt0lMetOn11OmQ=w400',
                        title='楊鎮誠醫師/家醫科-1/5',
                        text='小港醫院家庭醫學科主任/職業病科 主任。[臨床專業]:預防保健健康管理、家庭醫學(急慢性疾病)、職業醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊鎮誠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊鎮誠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=531&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EN5UF1GbgsU_OCDEeDwMuwa0Pf_RiR6ZviCeoD2AExlIOMKzfVe68uHuPfhiw5LK-RN4vqAZIMFH1yEx8unFBUYpBEFGYJHbcVFW4aUf3BihShhSNcC-eHU1PftydaQgTyNoPbly8w=w400',
                        title='曾愉芳醫師/家醫科-2/5',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾愉芳醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾愉芳醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=356&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/5vW23MyXznB0No_3BZvAsF4WR835dTy4eFqgMiJS5lVXUTLT4_NYNBcXwSkodTnSmHjqBIOx_2NaVV5oCjrrYbNPM-D10HoxR-sonn7O0LFxggAQZa1WazvLAVG44Zr3FEDfdGUacg=w400',
                        title='歐明蓉醫師/家醫科-3/5',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學(急性與慢性疾病治療)、預防保健、社區醫學安寧緩和醫學、戒菸治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介歐明蓉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號歐明蓉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=530&dept_code=1500'
                            )                            
                        ]
                    ),                                    
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/7MqyQIv0VH6BnJ_nABp8vUnTfU8bI5uF2SSTGKd9R_4homiO77Nc1HHzJ6SeGDhWtdW_DRCLUTsoOi4NislKBTx2usA1m3KHELItW7dfSNqkSrCyCyPOmr-M0PZcnGw1L1gcpM6YpQ=w400',
                        title='林晴筠醫師/家醫科-4/5',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:慢性疾病(高血壓,高血脂.)、急性疾病、國際旅遊醫學門診、戒菸門診..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林晴筠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林晴筠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=97&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EqfLEVIvlpjROiYRpAS-fzM_w2Av9yF8-H2vvzlTaAZ_bk8LBpVZ_piKd9r6_fYJMYU3C659U2pTtCZ4Sk3qy52lwKR3MIyT9ZjAwX3yx5wzceRdvbOdIMdDCpSTDz8lEQsfCUq-Fg=w400',
                        title='鄭如君醫師/職業病科-5/5',
                        text='小港醫院/職業病科暨健康管理中心主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介鄭如君醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號鄭如君醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=418&dept_code=1900'
                            )                            
                        ]
                    ),                       
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0  
########################### 高齡科  ###########################
    elif user_message.find('掛號高齡特別門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號家醫科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/y89zsZjYtXyIyrT73zPKbt2qn8pJB75HYeZYB0iZmZ1E-uITtsMT1buDR-fmx_QP2byhin6dXG7EFCetMVGSVC-XF5babDJsVDCWbwASTMedTD9NJnLJfXwUM7xeKNqV1hFltwO9ZQ=w400',
                        title='李純瑩醫師/家醫科-1/2',
                        text='高雄醫學大學附設醫院 家庭醫學科主任。[臨床專業]:家庭醫學、老人醫學、肥胖醫學、一般內科..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李純瑩醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李純瑩醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=190&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/1SXhSvx7gR3IxpsTl3sz5XB4wPGMJlOzarFVX05-6-lvXIOy91z8rLsWqYY7U1GLRfJpSrh7A2GtvRZLimmMY-XBiBcvJF5MtX7gM3q5gZ9al0WB-vCMPlA_UpNsCHLlTgEC-NMmeg=w400',
                        title='張家禎醫師/家醫科-2/2',
                        text='高雄醫學大學附設醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學，老人醫學，青少年醫學，流行病學，戒菸，減重..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張家禎醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張家禎醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=141&dept_code=1500'
                            )                            
                        ]
                    ),

#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0   
########################### 預立醫療照護別門診  ###########################
    elif user_message.find('掛號預立醫療照護門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號家醫科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/7MqyQIv0VH6BnJ_nABp8vUnTfU8bI5uF2SSTGKd9R_4homiO77Nc1HHzJ6SeGDhWtdW_DRCLUTsoOi4NislKBTx2usA1m3KHELItW7dfSNqkSrCyCyPOmr-M0PZcnGw1L1gcpM6YpQ=w400',
                        title='林晴筠醫師/家醫科-1/2',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:慢性疾病(高血壓,高血脂.)、急性疾病、國際旅遊醫學門診、戒菸門診..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林晴筠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林晴筠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=97&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EN5UF1GbgsU_OCDEeDwMuwa0Pf_RiR6ZviCeoD2AExlIOMKzfVe68uHuPfhiw5LK-RN4vqAZIMFH1yEx8unFBUYpBEFGYJHbcVFW4aUf3BihShhSNcC-eHU1PftydaQgTyNoPbly8w=w400',
                        title='曾愉芳醫師/家醫科-2/2',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾愉芳醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾愉芳醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=356&dept_code=1500'
                            )                            
                        ]
                    ),
                       
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0        
########################### 旅遊醫學門診  ###########################
    elif user_message.find('掛號旅遊醫學自費門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號家醫科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/UNIU-8Tm3JzARxPQkrWFmL3OFrPPvEQWr2CKVUg-i63nHQ648iKkuquY8a2J-lsDqpmnMEKEkezhpV-TtYuPuNBAcbyx6WKrF73fpVRDQyY3ovtxvNW_-WIjcLCaEt0lMetOn11OmQ=w400',
                        title='楊鎮誠醫師/家醫科-1/4',
                        text='小港醫院家庭醫學科主任/職業病科 主任。[臨床專業]:預防保健健康管理、家庭醫學(急慢性疾病)、職業醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊鎮誠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊鎮誠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=531&dept_code=1500'
                            )                            
                        ]
                    ),

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EN5UF1GbgsU_OCDEeDwMuwa0Pf_RiR6ZviCeoD2AExlIOMKzfVe68uHuPfhiw5LK-RN4vqAZIMFH1yEx8unFBUYpBEFGYJHbcVFW4aUf3BihShhSNcC-eHU1PftydaQgTyNoPbly8w=w400',
                        title='曾愉芳醫師/家醫科-2/4',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾愉芳醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾愉芳醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=356&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/5vW23MyXznB0No_3BZvAsF4WR835dTy4eFqgMiJS5lVXUTLT4_NYNBcXwSkodTnSmHjqBIOx_2NaVV5oCjrrYbNPM-D10HoxR-sonn7O0LFxggAQZa1WazvLAVG44Zr3FEDfdGUacg=w400',
                        title='歐明蓉醫師/家醫科-3/4',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:家庭醫學(急性與慢性疾病治療)、預防保健、社區醫學安寧緩和醫學、戒菸治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介歐明蓉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號歐明蓉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=530&dept_code=1500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/7MqyQIv0VH6BnJ_nABp8vUnTfU8bI5uF2SSTGKd9R_4homiO77Nc1HHzJ6SeGDhWtdW_DRCLUTsoOi4NislKBTx2usA1m3KHELItW7dfSNqkSrCyCyPOmr-M0PZcnGw1L1gcpM6YpQ=w400',
                        title='林晴筠醫師/家醫科-4/4',
                        text='小港醫院家庭醫學科主治醫師。[臨床專業]:慢性疾病(高血壓,高血脂.)、急性疾病、國際旅遊醫學門診、戒菸門診..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林晴筠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林晴筠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=97&dept_code=1500'
                            )                            
                        ]
                    ), 
                      
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0  

########################### 精神科  ###########################
    elif user_message.find('掛號精神科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號精神科',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/B1pUGQU7b6uuQUJeWWXowju9mi_Cc7cx7csWhxORdYfy2vNRMCcDTA_GFIA9VKRafgIRn-J87rvXFBSoP20-9-f6HWLuoAP891wPHhSjq8m4nG-u0bBtKNwGtMJOVsv9p4orE0q4hw=w400',
                        title='柯志鴻醫師/精神科-1/3',
                        text='小港醫院精神科主任/主治醫師。[臨床專業]:網路成癮、一般精神醫學.',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介柯志鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號柯志鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=131&dept_code=1100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/J1tCGEJAVuGQPjmTC2Z3t1VQ6wA1wU9SbHR813ztX0LwSk9l-QEwBBXfPaJ7pyqNGD8NQ1dHcIUhRefDGMZVgaUGHCSRcruSxV2lmolEgMlZh01FQFZ_550Jw0A6e5Er-rVDD8bv6g=w400',
                        title='柯巧俐醫師/精神科-2/3',
                        text='小港醫院精神科主治醫師。[臨床專業]:身心症、焦慮症、恐慌症、睡眠疾患、憂鬱症、老年精神醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介柯巧俐醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號柯巧俐醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=255&dept_code=1100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/qyC2rgZfDYKtwEIjUJI6miFxo9l-_AQaOUVPXmKdvGOqKCYbBMXrOtufqaGfqgolWn92KImAW6TT_a5_4iERCTZHKY9dluieuOyPlItgGdIu79an-0NZEKae3CLBpK4xEOE-H3QjfQ=w400',
                        title='林貝芸醫師/精神科-3/3',
                        text='高醫精神科主治醫師。[臨床專業]:失眠 焦慮、憂鬱 、恐慌自律神經失調、腦神經衰弱(精神官能症)..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林貝芸醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林貝芸醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=504&dept_code=1100'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
########################### 員工心理健康門診  ###########################
    elif user_message.find('掛號員工心理健康門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號員工心理健康門診',
            template=CarouselTemplate(
                columns=[

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/J1tCGEJAVuGQPjmTC2Z3t1VQ6wA1wU9SbHR813ztX0LwSk9l-QEwBBXfPaJ7pyqNGD8NQ1dHcIUhRefDGMZVgaUGHCSRcruSxV2lmolEgMlZh01FQFZ_550Jw0A6e5Er-rVDD8bv6g=w400',
                        title='柯巧俐醫師/精神科-1/2',
                        text='小港醫院精神科主治醫師。[臨床專業]:身心症、焦慮症、恐慌症、睡眠疾患、憂鬱症、老年精神醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介柯巧俐醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號柯巧俐醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=255&dept_code=1100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/qyC2rgZfDYKtwEIjUJI6miFxo9l-_AQaOUVPXmKdvGOqKCYbBMXrOtufqaGfqgolWn92KImAW6TT_a5_4iERCTZHKY9dluieuOyPlItgGdIu79an-0NZEKae3CLBpK4xEOE-H3QjfQ=w400',
                        title='林貝芸醫師/精神科-2/2',
                        text='高醫精神科主治醫師。[臨床專業]:失眠 焦慮、憂鬱 、恐慌自律神經失調、腦神經衰弱(精神官能症)..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林貝芸醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林貝芸醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=504&dept_code=1100'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0 
########################### 眼科  ###########################
    elif user_message.find('掛號眼科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號眼科',
            template=CarouselTemplate(
                columns=[

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/ue3xsbhCjaOePWtEqVR5nxXqvX4XLmfJcn_2wLwWImqnkKZq6ovo-MjfZhAP4ucCdcZjSslVGNdf5JwOeasr6wbKyPubhPUqu1u6LKDfTnsh_BIz_wJ8Gdqi5QYsgaWb2roVLAPqJg=w400',
                        title='鄭凱駿醫師/眼科-1/6',
                        text='小港醫院眼科主任。[臨床專業]:一般眼科、糖尿病視網膜病變、視網膜雷射手術、飛蚊症..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介鄭凱駿醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號鄭凱駿醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=60&dept_code=0500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/y1brnPutkhgf5GJYTjA_uG_x4Eg7_XzmeyfFR6EGMJ6V8atk_3zq9ldTVYTgis9lbhcp_vAffnfX1wMCvhSH1WKJt3SJ5MwktAhK2vyzsYduIy4WPtB5fUEf2WnUrGYSALEpLuHPIw=w400',
                        title='張祐誠醫師/眼科-2/6',
                        text='小港醫院眼科主治醫師。[臨床專業]:視網膜科:糖尿病視網膜病變、視網膜雷射手術、飛蚊症..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張祐誠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張祐誠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=110&dept_code=0500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/b02yCbH_r5FW6WAy2anlwA0Rgw4_VzRKP3lyhy259Km0dxfhCssNURHO53eY6rFJC7dnZQ5pyTvOUKciRQxKqXQYcK0Ol-egyjz1Ln3w_M3M5tZPKtVtOXZWjppZK68AGDOWPIz2Mg=w400',
                        title='林佳靜醫師/眼科-3/6',
                        text='小港醫院眼科主治醫師。[臨床專業]:視網膜科：視網膜病變(含糖尿病視網膜病變篩檢)、黃斑部病變視網膜及玻璃體手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林佳靜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林佳靜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=518&dept_code=0500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Pm60JJVu7YJpqdQ7FVzhdaiOu6tznaKEmcUZUj6polsuGIsmKEid1zehp3nPABcRauxkx2c5F4X-VpromiHNARfM4oo3PyC_G4uk_cOanNZsBhrCuZvIvRp94P7oXfi_zbIfOWPkWw=w400',
                        title='紀立中醫師/眼科-4/6',
                        text='小港醫院 眼科主治醫師。[臨床專業]:小兒眼科與斜視、弱視、屈光異常先天性眼疾、斜視、白內障、青光眼..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介紀立中醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號紀立中醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=345&dept_code=0500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/pjn-cnborZ7M92w8S071fBAjX-x0t4ll0PsIxpP27GovF_7QBXDjUMVo6eoVy8kALBhWInQDA3jrRp9umUm5KeEDUZfmPDgCZ5k2OI_8pwPu0Rk7OyGUK0kAnYDae6t774T9M26mwA=w400',
                        title='曾漢儀醫師/眼科-5/6',
                        text='小港醫院眼科主治醫師。[臨床專業]:眼科學、一般眼科、青光眼、眼角膜..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曾漢儀醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曾漢儀醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=49&dept_code=0500'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/uQVfvPrnZVy965zv7k93jd_k648JrK48zXg5F5WwyrCuKlEhrjPwktlqZCAs89tkdDcTXaI76XKWYNQybWtBedpdZGdUVF3eGX-GRkqn-1JVIkrq_Nx7bPLaxAunkL0jXR6XWoPDig=w400',
                        title='賴昱宏醫師/眼科-6/6',
                        text='小港醫院眼科主治醫師。[臨床專業]:小兒眼科與斜視、弱視、屈光異常、先天性眼疾、斜視眼、神經疾病..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介賴昱宏醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號賴昱宏醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=5&dept_code=0500'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                     
########################### 泌尿科  ###########################
    elif user_message.find('掛號泌尿科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號泌尿科',
            template=CarouselTemplate(
                columns=[

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/z-RoQ7MISci4F63BtApCLqs-6e-WHh_vAnq-9LVZl-eDXI30Xd9OfeGCSLLf5Zcscv8MYqXkTH6s9WzaRmys0TaJ639wfN2ucE_aoj58xpqn480VWkIIEHQ-0bsUi3DOCaWugDbMkA=w400',
                        title='李永進醫師/泌尿科-1/10',
                        text='小港醫院泌尿科主任。[臨床專業]:泌尿道腫瘤: 膀胱、腎臟及前列腺癌相關手術、排尿障礙、一般泌尿疾病..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李永進醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李永進醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=487&dept_code=0800'
                            )                            
                        ]
                    ),
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/OBLVIV46jhHBTig6U5YI2JPhy2qNAR-IIshSEIPxrHCBQy-fOOOnROIPf0_lUXgI6zkJG6_Rua03POlEI3ApOBZnagRcktvZHCB9TDSRhsrWcLJga16IUTV3cIXiGJ2NVXo3MW_29g=w400',
                        title='黃琮懿醫師/泌尿科-2/10',
                        text='高雄醫學大學附設醫院 泌尿部主治醫師。[臨床專業]:一般泌尿疾病、尿路結石、血尿、尿道感染等..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃琮懿醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃琮懿醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=523&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Q3y31DbF0xhX0O7-rmafpApjeDsdKa96OebwGovGvLIUEpHzn1wQq9JgnVW3YuxsGM03Xp_ejvcAm7wlyc9c5ydcR18kilTFYJ8EpzI7JViQ1JkNbKU42YNk039mS6nQDZwtGCKfkg=w400',
                        title='沈榮宗醫師/泌尿科-3/10',
                        text='小港醫院泌尿科主治醫師。[臨床專業]:泌尿腫瘤、排尿障礙、感染、結石、男性泌尿生殖疾病、男性不孕症..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介沈榮宗醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號沈榮宗醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=115&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EaqCq6CWnF3PIUQ815MPTUgC9vJtlICMvgDlLqszMJhIZYLnX_HJvvngRGuXERPil1V1U-Bn9jEASHyR120H_WhVtNVg5KKk_A5NXOUIJDAnRwvDU6i-reqtRoWuYwdP9JtHVcCAOA=w400',
                        title='王巽玄醫師/泌尿科-4/10',
                        text='小港醫院泌尿科主治醫師。[臨床專業]:泌尿腫瘤、腹腔鏡及達文西泌尿腫瘤手術、攝謢腺肥大、雷射攝謢腺手..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王巽玄醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王巽玄醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=314&dept_code=0800'
                            )                            
                        ]
                    ),

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/_sA3fkL7OPe5mhG_yfPz0c4NtZ95GBHVQ4LELhkPBmmjee69bDr91Fz16WCB4u4ms5myUbg9ZwWJBkliotQGfO6f8wXHXIEdpAWYXWJKqe3Mutbb7S8k959PbLw8Pc3loXIrIsu2Gg=w400',
                        title='曹曜軒醫師/泌尿科-5/10',
                        text='小港醫院泌尿科主治醫師。[臨床專業]:尿路結石、排尿症狀、疝氣、包皮手術、一般泌尿疾病、攝護腺肥大..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介曹曜軒醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號曹曜軒醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=560&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/nJBaMoG7ogHda1RjGP46jCPVGA9XxulC4r-Q8O22luVw1WF1PwcEC2N8ndAiGbxJNBKdayvPmoOmcwXa4sqiPGH6iv0YR2rt3boJmgt9v7N4aDgEOPgD_6FLrS-wyyGJvNv0ZHvAEA=w400',
                        title='詹鎮豪醫師/泌尿科-6/10',
                        text='小港醫院泌尿科主治醫師。。（單孔）腹腔鏡手術、攝護腺手術、泌尿系統腫瘤、泌尿道結石..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介詹鎮豪醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號詹鎮豪醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=522&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/nroCSyDA-4bcBkt2I-DLC4Ur_iuBAGLh9DeWzaQtcD-XVTaohc-QLucgAU7v074QnGVt4Ux4fFUoj6hNCWf8RNqsv5ROMw6sgRsneURfCsQtAeFxGIGaBDHVB6L50HqD8sJ_ZFnP6g=w400',
                        title='古筱菁醫師/泌尿科-7/10',
                        text='小港醫院泌尿科主治醫師。[臨床專業]:一般泌尿科、前列腺(攝護腺)肥大、尿路結石、尿路感染..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介古筱菁醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號古筱菁醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=532&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/rXqU0kXMTteR6a9NpPoqrTb4mGTqHY05tbT0BmCY6oklA_4Kplu7Nm94_5GWwxuk4zUUdbcIemJMg_c3vOqg8nON2Cp4vjiAjFqK1nosJjE8EHzqYyYTYBgICrN7LmTHFgbAADFLKg=w400',
                        title='耿俊閎醫師/泌尿科-8/10',
                        text='小港醫院泌尿科主治醫師。[臨床專業]:攝護腺肥大、尿路結石、泌尿道感染、泌尿道腫瘤、一般泌尿科手術.',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介耿俊閎醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號耿俊閎醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=422&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/HAV1LH1ucbTj3myldsEz8DcS1pN3zcLWwg073Ff04LxMLZDg1uaQwfExv_Rakr1mYrCTfbMjhfpOAEvGGNiwXQy0x8JbEtlR0k8Y79-ls8KImS5fX0S9KsgSIJJrKQQ5BKu-oVNAmA=w400',
                        title='張美玉醫師/泌尿科-9/10',
                        text='小港醫院泌尿科特約主治醫師。[臨床專業]:婦女應力性尿失禁、膀胱脫垂、尿路動力學檢查、性別研究..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張美玉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張美玉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=95&dept_code=0800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/17slw98ZPhLl8xk5pKVisnN8IMwyMdKaDBX6NEBj9XoGkfaNihI19PFIGjnmC6gFFhLzqBh5cEaba02_SrKgLy-D581EiY89q7ZVYo-5BhhA7uHI_WSYjnfOfrgqF_jfENJ_H0MQFQ=w400',
                        title='楊凱富醫師/泌尿科-10/10',
                        text='小港醫院泌尿科主治醫師。[臨床專業]:頻尿、血尿、尿失禁、排尿障礙、早洩、不舉、性功能障礙..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊凱富醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊凱富醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=456&dept_code=0800'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                     
############################ 職業病科  ###########################
    elif user_message.find('掛號職業病科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號職業病科',
            template=CarouselTemplate(
                columns=[

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/V8_CMuUsCrqJ6skZGcXbtFu9QjI4xQebWul8_Jaqfo1wTE8UemnH1Maje95IEaIluCbaBiomLies7uy5qV5OE7a_iQ6MI9SpuuYaH7ocFaZCAVt-8cXcTSSjz7C2t9GrCBzJd2IcRQ=w400',
                        title='楊鎮誠醫師/職業病科-1/5',
                        text='小港醫院職業病科主任/家庭醫學科主任。[臨床專業]:職業醫學、家庭醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介楊鎮誠醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號楊鎮誠醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=546&dept_code=2100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/-ZTHQZ--V0qYHm4A9enFHsyzwSvhmm3Q3n-jqFxZ3EnqgV_hace3dkbPlnyTtZYhLvlqwcmi0gXrBerBkefMLUOkXaDOLxOuulfwE3JKD-DIwlOzdcUYmQ_9RKPyVvvmFmnq1RkAMw=w400',
                        title='林嘉益醫師/職業病科-2/5',
                        text='大同醫院 健康管理中心 主任。[臨床專業]:內科學、職業醫學..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林嘉益醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林嘉益醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=551&dept_code=2100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/V0ZKOdByHyg6rSLm-eMyK7L11Wn0QMFgyp8JV5N4zEb96DLwEDB7EMawaIEHvCdhRa_E3yifnhf0UZHrNph2KMPgknLdexB2rurLDpgVsmiFfdrYGCiNmIAlQjJ5C2BhwxrZR2zWVg=w400',
                        title='林文一醫師/職業病科-3/5',
                        text='高雄醫學大學附設醫院職業暨環境醫學科主治醫師。[臨床專業]:肝膽胰內科疾病,B型肝炎,C型肝炎治療,職業病診斷與治療.',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介林文一醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號林文一醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=553&dept_code=2100'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Y6NYpYD075rvcYXgjM2XCyt6EHE8ZtWLhk-yBYnRoAFKV2ZY7enGyw_-KSkIp8VAP1OXlFZHdG1xe7eBO4uIf3kd4f9J6CGGO16omqMSvaUfZVUrlRpUxgXVE8RHAohlXcPL6dLqXQ=w400',
                        title='黃兆寬醫師/職業病科-4/5',
                        text='小港醫院/職業病科主治醫師。[臨床專業]:肝膽內科,超音波專科,消化系專科..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃兆寬醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃兆寬醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=187&dept_code=1900'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/EqfLEVIvlpjROiYRpAS-fzM_w2Av9yF8-H2vvzlTaAZ_bk8LBpVZ_piKd9r6_fYJMYU3C659U2pTtCZ4Sk3qy52lwKR3MIyT9ZjAwX3yx5wzceRdvbOdIMdDCpSTDz8lEQsfCUq-Fg=w400',
                        title='鄭如君醫師/職業病科-5/5',
                        text='小港醫院/職業病科暨健康管理中心主治醫師。[臨床專業]:家庭醫學科、一般內科、預防醫學、安寧緩和醫療、戒菸..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介鄭如君醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號鄭如君醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=418&dept_code=1900'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0
########################### 骨科 I  ###########################
    elif user_message.find('掛號骨科A') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號骨科I',
            template=CarouselTemplate(
                columns=[

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/D5teVInniSM6-xB9-6iOjuQqb2BMeuVAn5OawCQWywjSmI_yK_EdSKbcuZtDpMXCbH1gRngWE2o-bWjI_2e9LXEBH7Qyy5NiSCDO5NE7VDXPaI5rFeni1jDYMsNhYOEfQaIHHaFNUw=w400',
                        title='盧政昌醫師/骨科醫師群I-1/7',
                        text='小港醫院骨科主任/主治醫師。[臨床專業]:一般骨科、 骨折創傷、 運動醫學、 關節鏡手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介盧政昌醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號盧政昌醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=116&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/KNVT6hAUaaTM8kxqWbl8kjUx0TQK6n9ONUu4W65ClTIdJUuggqDoRwBLhKatfIVwqvak3B_id8z2XcClBXaOVomYAFP8R0s-52bGajtf3RoNJOzI55zn2xu4zLBwrL-W2Oz8s3otwA=w400',
                        title='王應鈞醫師/骨科醫師群I-2/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:關節重建手術、關節內視鏡手術、骨創傷手術、微創手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王應鈞醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王應鈞醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=451&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/XvawaE9cTqS8yHLTrEZ6v0n9G_RkQpS9pQ0O0ckF-x1GaFpUIh9yuaikHQop7ArbbhOUS3KaQsr5MHDU7iUuL55d69YGbtj2G3fZLCTwfdV35U-dgLZfEQw60wIZ5r8fq_izwk1giA=w400',
                        title='黃士豪醫師/骨科醫師群I-3/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:手外科、骨折創傷..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃士豪醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃士豪醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=364&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/pMbN_lEt254A9KhDyfR2TEflXBkce7HWopP0x4BeZBQfE_eoF_jL-lS1qAlEr2rDQxaAJy5gouqSFLXS6Uzwb29mznyKxKzEEsq_L2iIfltu4GYlVFeN9G0JaxGhVf58_N4kBmHc8g=w400',
                        title='陳姝蓉醫師/骨科醫師群I-4/7',
                        text='高雄醫學大學附設醫院骨科部主治醫師。[臨床專業]:足踝外科、一般及創傷骨科、骨質疏鬆、關節重建..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳姝蓉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳姝蓉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=481&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Zq4vOyzAVTEXOWUXS_Ha0M8B178Po7nBNqBetcPTAVDrHI8e6wM6Jm07tlvuWnRHkZ2sg2O8pQNLl8MzdEI-c8S9LtEN5qKsWZiizmMht3jI4BAcptCtDbx5mILkK8fxeMfyfNNO9A=w400',
                        title='沈柏志醫師/骨科醫師群I-5/7',
                        text='高雄醫學大學附設醫院骨科主治醫師。[臨床專業]:小兒骨科、一般骨科、骨折創傷..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介沈柏志醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號沈柏志醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=363&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/MVNRVnT9fVovdsD6_qPNPhJfd0wSHCSqyNj62RueOJW7pBrrKVi4_7c0Kzsx4sJTa5aiYsQx9HJG7kdCdFG1b6YA6G8O1v0WOPpJNBTRfsatfg-ezbwp_Kww6T9OW4fPeocTM8VdhA=w400',
                        title='劉秉政醫師/骨科醫師群I-6/7',
                        text='高雄醫學大學附設醫學院骨科部主治醫師.[臨床專業]:骨折﹑外傷﹑一般骨科疾病之手術治療﹑骨質疏鬆、 人工關節重建..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉秉政醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉秉政醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=127&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/qRfSmFrg1CXgplip4qdFRsHu2KOed70wukz911BZHlJ5mAGujhcJ_3LnxfPtluBbklIvCmnFR4SnWHIggdH-ZRoYfuBBvHrVbObundijST6IVqRhZqN-aLcrS7wtMZOGqWdLnLHuWw=w400',
                        title='卓進益醫師/骨科醫師群I-7/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:脊椎疾患、 下背痛,頸肩痛,椎間板突出一般骨科, 人工關節..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介卓進益醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號卓進益醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=214&dept_code=0700'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                    
########################### 骨科 I  ###########################
    elif user_message.find('掛號骨科B') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號骨科II',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/4D8tGfF6oOBxPwylfz2B7VZFNUkq-lECBM3fNLOy9VFZ5ZWfHYUbguLG1upzbiaiu-G0Fvk-eNkrcEl7qU1W3WmS5vGmcu2cxfN0y23PfvSfujSuzRxikc_nD-ys6L17TakFNZYPCQ=w400',
                        title='陳建志醫師/骨科醫師群II-1/7',
                        text='小港醫院骨科主任。[臨床專業]: 一般性骨折診治、外傷性骨折治療、骨質疏鬆治療及保健..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳建志醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳建志醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=155&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/Nx-Bzp7n7cHc2mXonTDO-6lzCp0Z4xp3opoGQf8wIt9mDC58ZkYr4KrBc2k4v-Wds0tjmujsHbhd7gVh-6wHX27LBj49t-GzPCK0S-OVN-FyUA1ITArc48YvaBYukaQOLdmFwGmWRQ=w400',
                        title='傅尹志醫師/骨科醫師群II-2/7',
                        text='高雄醫學大學附設醫院骨科主治醫師。[臨床專業]:手外科、創傷外科、顯微再接..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介傅尹志醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號傅尹志醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=332&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/5FicjTVElJGlUDn41J-lC-p_uxG5mSHvFzA3mhuU0OGkhpqs3QhH8lqgNTHR7iRVINGsLvVJbd9qHWNyMDrPH5JvuoTI7CRFsI2XS3rZ7Ssi0dqNgx8FY5Slh3f9e-eqBCgNVfbqLA=w400',
                        title='周伯禧醫師/骨科醫師群II-3/7',
                        text='高雄醫學大學附設醫院主治醫師/運動醫學系 教授。[臨床專業]:運動傷害、運動生物力學、膝、肩、肘外科、關節鏡手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介周伯禧醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號周伯禧醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=174&dept_code=0700'
                            )                            
                        ]
                    ),                     
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/LnliGsne6OBUd8JaGUCC2XdUohiiiAudhlREBJWox1_QpmKkvS1_1FYI_I7XUfC5NJZqeJN04dA5kD_4X9chaezedPZz8kjwYX-0ICeBgYQTIoELZDnxVSame2-qkfh_3oTp8vqKuw=w400',
                        title='沈柏因醫師/骨科醫師群II-4/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:骨折創傷..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介沈柏因醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號沈柏因醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=526&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/M6eul4vZ2RG50DYP4ZwOE5GZUxTsqQX46Fm7Ittm86e0mmPROCVa6a4_eIFQ79vsnbRrKvHr8zo6F1jBOQiSSvlzT6VSJdpmTDfyKPjXDZUWHFp52Gi7TPFDf9Lo5dZIBPI4iGVs7Q=w400',
                        title='蘇育德醫師/骨科醫師群II-5/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:一般骨科、人工關節置換、骨折創傷、手外科、骨質疏鬆、各類運動傷害..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介蘇育德醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號蘇育德醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=559&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/ZZSdfcyWzBDZn3lDpYrteiW94CvLRuowgDULkKcuNsU3vZ-U6Excg5qIRtYNxc29Zb-30HP33gbnAuDjyD4a9Dj58Dd02eF2euDe2nXTgcCnPtFwCrcanS1MfsWXhuYdl8Gw12_cnw=w400',
                        title='李忠祐醫師/骨科醫師群II-6/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:骨折創傷、人工關節置換、骨質疏鬆、運動傷害..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李忠祐醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李忠祐醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=558&dept_code=0700'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/0jUBORh7uREgg7BqrL8eNXx306sTetKq2MycqNLLbKPrtp9cEnOTTaM99psFmDCJq9nokZ8cSzTPnG_RSQ18jHG7M6AYSsXMo4bLH92O6_0TJ6cfYHDgfjbojv151IUmc_nTaHvBiw=w400',
                        title='劉文智醫師/骨科醫師群II-7/7',
                        text='小港醫院骨科主治醫師。[臨床專業]:手外科及上肢疾患、顯微肢體重建手術、關節鏡手術、骨折創傷..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介劉文智醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號劉文智醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=502&dept_code=0700'
                            )                            
                        ]
                    ),
                   
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                    

########################### 復健科 ###########################
    elif user_message.find('掛號復健科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號復健科',
            template=CarouselTemplate(
                columns=[
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/yk4jyKiSpy0NY_4e189awnklrqOp0tlgEOhCrFxoRAHXl4Xt8SeifGqMnOxmsJYbIpH82SqeF33s9pQ5yIOyr0ywmmToeHogzrp5b353w3ovuX1Vj9pkPS0QmZSd-h0QfbAOZ2WU6g=w400',
                        title='陳怡媜醫師/復健科-1/5',
                        text='小港醫院復健科主任/主治醫師。[臨床專業]:復健醫學、心肺復健、肌肉骨骼超音波檢查',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳怡媜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳怡媜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=527&dept_code=1800'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/k2lbx_cd2yssIpDTBdRk25Ldj-jJtl3CHQe0nwaCmv4IhlgMA9DjM1MyPVsuwS3QkkWFGSXxg55s_M4TSn1Qc0zrv7inHro1CIaorYV7jRSODodj8CZdt-wx7sPy4zYq8vhacJ0Q7w=w400',
                        title='郭芳妤醫師/復健科-2/5',
                        text='高雄醫學大學附設醫院復健科主治醫師。[臨床專業]:神經復健(腦中風、腦外傷、脊髓損傷復健)、五十肩、肩頸痠痛.',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介郭芳妤醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號郭芳妤醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=562&dept_code=1800'
                            )                            
                        ]
                    ),
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/g_fH6NgtY20jll6GdGPGbF_2YgNXz0WDlH4Z1b9tJz7Z9-betslENovk_GkyjeNIzNBYz5wo59vOKhFLJoTPXozt59VWrSFDLrMCbWEsslPpvEO1TNKYgiNl3XdBHxlwJN-H7ZxkDQ=w400',
                        title='李佳玲醫師/復健科-3/5',
                        text='小港醫院/復健科主治醫師。[臨床專業]:職業傷病的評估、復健與復工、運動傷害復健、超音波檢查、癌症復健..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李佳玲醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李佳玲醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=36&dept_code=1800'
                            )                            
                        ]
                    ),
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/tueViA0sgUye-HHWGf7IFhgD-VcwvVEe4W7X7D0L7apa0oUX-bB4b7SByik2pwoB0FBBkbXpIdbbJpAapX1vzX66sjPBxPJm_95uOw3EIG9TOqySZo2R72JuDch5MuTfwh-Lp8Hr9w=w400',
                        title='李權峯醫師/復健科-4/5',
                        text='高雄醫學大學附設醫院/復健科主治醫師。[臨床專業]:復健醫學、運動醫學、老人醫學、物理治療學、肌肉骨骼復健..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李權峯醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李權峯醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=528&dept_code=1800'
                            )                            
                        ]
                    ),
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/IuKqcRBI72K4w5Z67uCI5kEMBKYVTJ1fW_hrjbaDNm1w3xcZBQ3HEzoln5R6bEDoXJ9dN2UkE5uny2i_9NUGG4VEEt3ud5Hbci4o5NAeZGy41VbXJpzYnXV_Ja_kLLYv4oTXNBrI3A=w400',
                        title='莊世鴻醫師/復健科-5/5',
                        text='小港醫院/復健科特約主治醫師。[臨床專業]:運動醫學、肌肉骨骼復健、肌肉骨骼超音波檢查、神經復健..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介莊世鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號莊世鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=259&dept_code=1800'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                    
########################## 掛號咀嚼吞嚥困難特別門診 ###########################
    elif user_message.find('掛號咀嚼吞嚥困難特別門診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號咀嚼吞嚥困難特別門診',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/b4EHC2xsHBxG4d0PdkrcZyIXct8gNbGQZEVigBOsub9W1if3CxZJZ6fE3w-0cV_vq1q4NCr_7YrTvnIci97l0pCJY9Ksz2YWBQfjikrmfP0-GWipV2OHV7KL9-xRoDzLAdjwsTDktA=w400',
                        title='陳俊鴻醫師/神經內科-1/3',
                        text='小港醫院神經科主任/主治醫師。[臨床專業]:神經學、腦中風、神經重症.等',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳俊鴻醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳俊鴻醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=389&dept_code=1000'
                            )                            
                        ]
                    ),                      
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='rectangle',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/yk4jyKiSpy0NY_4e189awnklrqOp0tlgEOhCrFxoRAHXl4Xt8SeifGqMnOxmsJYbIpH82SqeF33s9pQ5yIOyr0ywmmToeHogzrp5b353w3ovuX1Vj9pkPS0QmZSd-h0QfbAOZ2WU6g=w400',
                        title='陳怡媜醫師/復健科-2/3',
                        text='小港醫院復健科主任/主治醫師。[臨床專業]:復健醫學、心肺復健、肌肉骨骼超音波檢查',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳怡媜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳怡媜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=527&dept_code=1800'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/opYpAIhHVT2IkpzENoLUN_EX77f5BaIKqjYattqq0Af9dsyAQkwny0CIjEExWl6Ff2BjRVLzj9xmtdC_h1ea-NDLKtP-J8cEyuqWvIZ6O9ALdnNzQshALTaOGF2azlYrXq0Fpj-jZw=w400',
                        title='謝升文醫師/神經內科-3/3',
                        text='小港醫院神經科/主治醫師。[臨床專業]:一般神經科、腦中風、睡眠障礙.等。',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介謝升文醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號謝升文醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='https://www.kmsh.org.tw/pro/search_data2.asp?pno=299&dept_code=1000'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0    
########################### 掛號牙科一診 ###########################
    elif user_message.find('掛號牙科一診') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號牙科一診',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/bk5ucPTNfKfrgALwGrLQc5cqjFF-6dRH1OcDnm2IvnBdKQ1twkWE5pjRVUytF5IaCji0V0FWyNzsSLhpjnWpevhGpuOVEGPjeIe8EytFfPfp6GOIvzMl2wvlvVvBTNqndIJYm5RVPA=w400',
                        title='陳翰生醫師/牙科一診-1/5',
                        text='小港醫院牙科主治醫師。[臨床專業]:一般牙科治療、牙周病治療、植牙、牙周再生手術、牙冠增長術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳翰生醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳翰生醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=132&dept_code=1300'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/OkMTTZECVmploWf4MLIUj3Qc2DHPS4ArdGqXqbRjQCHq93Qe-gteEp_KQxJioakUUQrHHJ75bNohARZunRowEVWiSP6e4nsaY4cqZ7Oa9v-DDaG71xld7tOjc5dZ-YsgGhbV6jD14w=w400',
                        title='陳佳琪醫師/牙科一診-2/5',
                        text='小港醫院牙科部主治醫師。[臨床專業]:一般牙科、全口重建、人工植牙..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳佳琪醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳佳琪醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=566&dept_code=1300'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='魏祥禮醫師/牙科一診-3/5',
                        text='小港醫院牙科部主治醫師。[臨床專業]:一般牙科、全口重建、人工植牙..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介魏祥禮醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號魏祥禮醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=569&dept_code=1300'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='游智凱醫師/牙科一診-4/5',
                        text='小港醫院牙科主治醫師。[臨床專業]:一般牙科全人治療、全口贗復治療、人工植牙',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介游智凱醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號游智凱醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=534&dept_code=1300'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='嚴崇文醫師/牙科一診-5/5',
                        text='高雄醫學大學附設醫院/口腔顎面外科主治醫師。[臨床專業]:一般牙科、口腔顎面外科專科、口腔外科手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介嚴崇文醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號嚴崇文醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=568&dept_code=1300'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                    
########################### 掛號口腔顎面外科 ###########################
    elif user_message.find('掛號口腔顎面外科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號口腔顎面外科',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/vRj3_D2yfP8gmNYcwCP0gf8Bc9sPcocOxBk1Z20hRz0vvWmhGg4UtZS057vXyTbMoTr7EPahokyWCoTgYm7TQHObvBz6acy40mnhyxDqgv1Ta_ypzYvXZ6KUzOra_gXM0qXoftPdUg=w400',
                        title='許經偉醫師/口腔顎面外科-1/2',
                        text='小港醫院口腔顎面外科暨牙科主治醫師。[臨床專業]:正顎手術、植牙手術含困難補骨手術、口腔及顎顏面良性與惡性腫瘤手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介許經偉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號許經偉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=366&dept_code=1300'
                            )                            
                        ]
                    ),
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='嚴崇文醫師/口腔顎面外科-2/2',
                        text='高雄醫學大學附設醫院/口腔顎面外科主治醫師。[臨床專業]:一般牙科、口腔顎面外科專科、口腔外科手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介嚴崇文醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號嚴崇文醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=568&dept_code=1300'
                            )                            
                        ]
                    ),                     
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0                     
########################### 掛號齒顎矯正科 ###########################
    elif user_message.find('掛號齒顎矯正科') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號齒顎矯正科',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/2ZElnKEUNbt4FH_GPma6W4WFn6QzYmfkqWtci1z2PdiwBKl7UjztsD4u0CdTTWQPZgybEkN5E3NNtVSuDEQMzW2bLTJCRiy3OkHFi-AzNySnxptbr9j1VYcV8hI9sRPjTSkeGCFbqw=w400',
                        title='潘金芸醫師/掛號齒顎矯正科',
                        text='高雄醫學大學附設醫院齒顎矯正科主治醫師。[臨床專業]:一般牙科、齒顎矯正科專科、成人各類異常咬合之齒顎矯正治療',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介潘金芸醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號潘金芸醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=82&dept_code=1300'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0  
########################### 掛號牙周病科 ###########################
    elif user_message.find('掛號牙周病與根管治療') != -1:
        clinic_message = TemplateSendMessage(
            alt_text='掛號牙周病與根管治療',
            template=CarouselTemplate(
                columns=[
                     
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/bk5ucPTNfKfrgALwGrLQc5cqjFF-6dRH1OcDnm2IvnBdKQ1twkWE5pjRVUytF5IaCji0V0FWyNzsSLhpjnWpevhGpuOVEGPjeIe8EytFfPfp6GOIvzMl2wvlvVvBTNqndIJYm5RVPA=w400',
                        title='陳翰生醫師/牙周病科',
                        text='小港醫院牙科主治醫師。[臨床專業]:一般牙科治療、牙周病治療、植牙、牙周再生手術、牙冠增長術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳翰生醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳翰生醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=132&dept_code=1300'
                            )                            
                        ]
                    ),                    
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/rOPFxzSS-R6HJ2CoXnGOZGFDDD-Q4x0SwjOvBtIqhJaykpgC2IbjLU0bTlgM1ZJ_Rib5QmqTsO6xyJqYn8QZd3-9BF5o__0RZBeT4WfWRm4FB9JsRNsUCnU_pOwb8jicMbjhJntzKQ=w400',
                        title='李惠娜醫師/根管治療',
                        text='高雄醫學大學附設中和醫院牙髓病曁牙體復形科主治醫師。[臨床專業]:牙齒美白、外傷牙處理、顯微根管治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李惠娜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李惠娜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=567&dept_code=1300'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message)
        return 0   
########################### 掛號牙科約診 A ###########################
    elif user_message.find('掛號牙科約診A') != -1:        
        clinic_message = TemplateSendMessage(
            alt_text='掛號牙科約診',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/bk5ucPTNfKfrgALwGrLQc5cqjFF-6dRH1OcDnm2IvnBdKQ1twkWE5pjRVUytF5IaCji0V0FWyNzsSLhpjnWpevhGpuOVEGPjeIe8EytFfPfp6GOIvzMl2wvlvVvBTNqndIJYm5RVPA=w400',
                        title='陳翰生醫師/牙科約診 I-1/6',
                        text='小港醫院牙科主治醫師。[臨床專業]:一般牙科治療、牙周病治療、植牙、牙周再生手術、牙冠增長術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介陳翰生醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號陳翰生醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=132&dept_code=1300'
                            )                            
                        ]
                    ),                    

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/RHi25VSbXxWk0MKCfYYdFvByXmwSoHGJInmZS5VOMRbNx5FzdzSuE32_I04d0kT7urXsqLWidG6wpaaEvVTpViQNhEm4guqRefykgjXHMRc1_HVHIq7hRKi3uhoQTbTPTsFQUvUpfg=w400',
                        title='黃英瑋醫師/牙科約診 I-2/6',
                        text='小港醫院牙科主治醫師。[臨床專業]:非手術性根管治療、手術性根管治療手術、外傷牙處理牙體復形治療、..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃英瑋醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃英瑋醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=367&dept_code=1300'
                            )                            
                        ]
                    ), 
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='魏祥禮醫師/牙科一診 I-3/6',
                        text='小港醫院牙科部主治醫師。[臨床專業]:一般牙科、全口重建、人工植牙..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介魏祥禮醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號魏祥禮醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=569&dept_code=1300'
                            )                            
                        ]
                    ),                    
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/kFIDyvzBm2ybWtjymBDbeIJ4QsL7BOUfNUraxXFBkidrjICxfQRyQlDpH6dEkPZoqpIbNsQhtcYqA8pGY1fCYEJuYBPRu_1G1g-7uCzDUGLnKcTqXNNciw5R_4LtScbemIsPmkNtsQ=w400',
                        title='鄭戎軒醫師/牙科約診 I-4/6',
                        text='高雄醫學大學附設中和醫院齒顎矯正科主治醫師。[臨床專業]:一般牙科、兒童及青少年早期齒顎矯正、合併牙周補綴相關齒顎矯正',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介鄭戎軒醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號鄭戎軒醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=372&dept_code=1300'
                            )                            
                        ]
                    ), 
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='游智凱醫師/牙科一診 I-5/6',
                        text='小港醫院牙科主治醫師。[臨床專業]:一般牙科全人治療、全口贗復治療、人工植牙',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介游智凱醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號游智凱醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=534&dept_code=1300'
                            )                            
                        ]
                    ),                    

#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/yv0fcc3PodEoAupRJNGIvHI0tb1PIXCEBnp8xj_DquNbMUXmIo2IHx8GFBxqEzlv9ZefyvF27lscXKYV7bADg-k0Uv1gfxZPK_s4bDes4cWApKSnSYEaXHZmxDyUsQMxPVH23ZhNqw=w400',
                        title='王紹光醫師/牙科約診 I-6/6',
                        text='小港醫院牙科主治醫師。[臨床專業]:一般牙科全人治療、全口贗復治療、人工植牙..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介王紹光醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號王紹光醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=478&dept_code=1300'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                ]
            )
        )       
                
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message2)
        return 0    
########################### 掛號牙科約診 B ###########################
    elif user_message.find('掛號牙科約診B') != -1:        
        clinic_message = TemplateSendMessage(
            alt_text='掛號牙科約診B',
            template=CarouselTemplate(
                columns=[
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/vRj3_D2yfP8gmNYcwCP0gf8Bc9sPcocOxBk1Z20hRz0vvWmhGg4UtZS057vXyTbMoTr7EPahokyWCoTgYm7TQHObvBz6acy40mnhyxDqgv1Ta_ypzYvXZ6KUzOra_gXM0qXoftPdUg=w400',
                        title='許經偉醫師/牙科約診 II-1/6',
                        text='小港醫院口腔顎面外科暨牙科主治醫師。[臨床專業]:正顎手術、植牙手術含困難補骨手術、口腔及顎顏面良性與惡性腫瘤手術..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介許經偉醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號許經偉醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=366&dept_code=1300'
                            )                            
                        ]
                    ),
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/2Mylla4PVBdd5bXY-5miCp-VI2YprnDImFHGC5P11yz58uz9XVxc1T8M8M2zcpCurE2_7T9t9o2O-d7juaX4XvHC-DLxLbni8JlqD36DCOvfQE_MZFBzBONGr9X_tM1xugfy7iUwTg=w400',
                        title='張宏博醫師/牙科約診 II-2/6',
                        text='小港醫院牙科主治醫師/高雄醫學大學口腔醫學院客座教授。[臨床專業]:兒童及青少年各類異常咬合之齒顎矯正治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介張宏博醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號張宏博醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=353&dept_code=1300'
                            )                            
                        ]
                    ),
  #-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/t9KZVYiEYDjKmaj-bEDnWWC9MH9ypkn7nLZqiG1bf3ElPPf_P471-w-oZRk056Ewrv03zeH7k6FJ6mtdiBKSaja3qQERbe692J1bSC8VK09kR62HGxa_W3QZBvbJ5BYzfib4vosoZg=w400',
                        title='黃靜瑜醫師/牙科約診 II-3/6',
                        text='高雄醫學大學附設醫院兒童暨特殊需求者牙科醫師。[臨床專業]:兒童牙科..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介黃靜瑜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號黃靜瑜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=545&dept_code=1300'
                            )                            
                        ]
                    ),                                      
  # -----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/rOPFxzSS-R6HJ2CoXnGOZGFDDD-Q4x0SwjOvBtIqhJaykpgC2IbjLU0bTlgM1ZJ_Rib5QmqTsO6xyJqYn8QZd3-9BF5o__0RZBeT4WfWRm4FB9JsRNsUCnU_pOwb8jicMbjhJntzKQ=w400',
                        title='李惠娜醫師/牙科約診 II-4/6',
                        text='高雄醫學大學附設中和醫院牙髓病曁牙體復形科主治醫師。[臨床專業]:牙齒美白、外傷牙處理、顯微根管治療..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李惠娜醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李惠娜醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=567&dept_code=1300'
                            )                            
                        ]
                    ),                    
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/8Wd9RFN6P4U9-0g1_QMzp4alq33Kw1tPzbzYL-FT4T_gxfawv_S7ld2KwYg203KzHPAhbGWLC7g9glvc0Z-4RD10XcRrC0BdEY0NH-N2XAXiwk0ocqXJ-hAlttnzzDBHlUvmwSx1lw=w400',
                        title='李昆峰醫師/牙科約診 II-5/6',
                        text='小港醫院牙科部主治醫師。[臨床專業]:一般牙科、兒童及青少年早期齒顎矯正、合併正顎手術齒顎矯正..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介李昆峰醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號李昆峰醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=521&dept_code=1300'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------                    
                    CarouselColumn(
                        image_aspect_ratio='square',
                        imageSize='contain',
                        thumbnail_image_url='https://lh3.googleusercontent.com/mCzK3o8ht_8CFq0PKgm89sKhfV5NlrBMXHqD9O7FyeXmHCi3ZYNsvUDcBjInLTX21OK8wiftxzifZq7kEESMs97U4KA5d59zg49eIB8Zxd0U08YchDm2kbMPVQhq78pSiyUvAIWNOw=w400',
                        title='任心如醫師/牙科約診 II-6/6',
                        text='小港醫院牙科部主治醫師。[臨床專業]:一般牙科、全口重建、人工植牙..',
                        actions=[
                            MessageTemplateAction(
                                label='醫師簡介',
                                text='簡介任心如醫師'
                            ),
                            MessageTemplateAction(
                                label='門診掛號',
                                text='掛號任心如醫師'
                            ),
                            URITemplateAction(
                                label='個人網頁',
                                uri='http://www.kmsh.org.tw/pro/search_data2.asp?pno=511&dept_code=1300'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                ]
            )
        )       
                
        line_bot_api.reply_message(event.reply_token,clinic_message)
        #line_bot_api.push_message(uid, clinic_message2)
        return 0                    
###############################################################################
#                              網路掛號選單
#           網路掛號/查詢掛號/取消掛號   #user_message='查詢掛號'     
###############################################################################       
    elif user_message.find('網路掛號選單') != -1:               
        
        reg_message = TemplateSendMessage(
            alt_text='網路掛號選單',
            template = ButtonsTemplate(
                image_aspect_ratio='square',
                thumbnail_image_url='https://lh3.googleusercontent.com/ONYKtzARFUPHbls7C-Manq9wBe5ZbpcQirM7m5zP417GFtH8aMMmHga3hWZ_spws0ovVSOJhcgYUxRN4JjCQBLBZfpaVZ3S6f6yf8BdsAFWtn0r_exFbEnms-OJ5v_MDMOb9TxuG7A=w400',
                title='小港醫院網路掛號/查詢/取消掛號',
                text= '請按以下連結查詢',
                actions= [
                    # MessageTemplateAction(
                    #     label= '電話掛號服務',
                    #     text= '電話掛號服務'
                    #     ),
                    URITemplateAction(
                        label= '網路掛號',
                        uri= 'https://www.kmsh.org.tw/web/KMUHWeb/Pages/P02Register/NetReg/NetRegFirst.aspx'
                        ),
                    URITemplateAction(
                        label= '查詢/取消掛號',
                        uri= 'https://www.kmsh.org.tw/online/NetReg_delSch.asp?openExternalBrowser=1'
                        ),
                    MessageTemplateAction(
                        label= '電話掛號服務',
                        text= '電話掛號服務'
                        ),                    
                    URITemplateAction(
                        label= '當月份門診表下載',
                        uri= Clinic_Book.get()
                        )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.push_message(uid, reg_message)
        return 0
################################################################################
#                           電話掛號服務
###############################################################################        
    elif user_message.find('電話掛號服務') != -1:               
        
        reg_message = TemplateSendMessage(
            alt_text='電話掛號服務',
            template = ButtonsTemplate(
                image_aspect_ratio='square',
                thumbnail_image_url='https://lh3.googleusercontent.com/9yPKsQk1n-LO4Yo1hETOr0T5IBLeZJi42HU3dEiRVXe2ynwJsaw-1Sp3tGMT7qX8CqB1b7Vv86NxQvnwUku4KjmYmOMJE9kZpJpVrMY2vG3iSiLo_sWBnILZfURdpI6S-glJ5atuUg=w400',
                title='小港醫院電話掛號服務',
                text= '請按以下連結查詢',
                actions= [
                    MessageTemplateAction(
                        label= '總機電話號碼',
                        text= '小港醫院電話號碼'
                        ),
                    MessageTemplateAction(
                        label= '人工掛號電話(只到下午4點)',
                        text= '小港醫院人工掛號專線'
                        ),
                    MessageTemplateAction(
                        label= '語音掛號專線',
                        text= '小港醫院語音掛號專線'
                        ),
                   
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,reg_message)
        #line_bot_api.push_message(uid, reg_message)
        return 0 
#-----------------------------------------------------------------------------
    elif user_message.find('小港醫院電話號碼') != -1:                               
        line_bot_api.reply_message(event.reply_token,TextSendMessage('078036783'))
        #line_bot_api.push_message(uid, reg_message)
        return 0
#-----------------------------------------------------------------------------    
    elif user_message.find('小港醫院人工掛號專線') != -1:                               
        line_bot_api.reply_message(event.reply_token,TextSendMessage('078059152'))
        #line_bot_api.push_message(uid, reg_message)
        return 0  
#-----------------------------------------------------------------------------    
    elif user_message.find('小港醫院語音掛號專線') != -1:                               
        line_bot_api.reply_message(event.reply_token,TextSendMessage('078070210'))
        #line_bot_api.push_message(uid, reg_message)
        return 0      
###############################################################################
#                              掛號XXX醫生
#                 user_message= '掛號郭昭宏醫師' 
#                 user_message= '掛號陳俊鴻醫師'
#                 user_message= '掛號樟柯醫師'
###############################################################################
#     elif user_message.find('掛號') != -1:        
#         if user_message.find('醫師')!= -1:            
            
#             PA=user_message.find('掛號')
#             PB=user_message.find('醫師')
#             name_len=PB-PA
#             if name_len >= 5:
                
#                 Doc_Name = user_message[PB-3:PB] #Reg 參數
#             else:
#                 Doc_Name = user_message[PB-2:PB] #Reg 參數
            
#             # Doc_Name='陳泰良'
#             # Doc_Name='陳俊鴻'
#             # Doc_Name='李美月'
#             # import KMSH_DoctorDB_Inquiry
#             doc_found= False          
#             doc_info=KMSH_DoctorDB_Inquiry.response(Doc_Name)
            
#             if len(doc_info)!=0:
#                 doc_found=True
                
#                 #在此設定例外參數
#                 pno= doc_info[0]['pno'].lstrip()
#                 dept_code= doc_info[0]['dept_code'].lstrip()
#                 DeptNo = doc_info[0]['DeptNo'].lstrip()
#                 DocNo=doc_info[0]['DocNo'].rstrip()
            
# # ------------------------根據醫生參數網要找資料--------------------------------
#             if  doc_found: 
      
#                 clinic_timeinfo_title = ''
#                 clinic_timeinfo_title ='[' + Doc_Name +'醫師，門診時間表]\n' 
            
#                 line_bot_api.reply_message(event.reply_token,TextSendMessage('要等耐心我一下喔!幫您查詢門診掛號時段需要一點時間!6秒後沒回覆代表我累嘞，請使用其他服務!'))
#                 url1='http://www.kmsh.org.tw/pro/search_data2.asp?'    
#                 url_KMSH =url1 + 'pno=' + pno + '&dept_code='+ dept_code  
                
#                 #呼叫doc_jobstr副程式，爬取醫生網站，並搜尋醫生之工作資料字串
#                 find_str = doc_jobstr.Find(url_KMSH)
     
#                 #測試find_str='姓名：洪志興CHIH-HSING HUNG 科別：小兒科 地址：高雄市小港區山明路 482號  院內分機：3252  現任：小港醫院副院長高雄醫學大學小兒科學教授台灣兒童過敏及免疫科專科醫師台灣兒童過敏氣喘及免疫學會理事 上一頁  學　歷  1986/08-1993/07國防醫學院 醫學系 醫學士 2002-2003 年 美國約翰霍普金斯大學 (Johns Hopkins university) 氣喘暨過敏病中心研究員2006-2009 年 高雄醫學大學醫學研究所博士  醫學訓練 高雄醫學大學醫學研究所博士，高雄醫學大學小兒科學教授，高雄醫學大學附設醫院小兒過敏及免疫科主治醫師，台灣兒童過敏氣喘及免疫學會理事、美國約翰霍普金斯大學氣喘暨過敏病中心研究員  臨床專業 過敏學、免疫學、小兒科學 學術職位  教授  醫院職位  小港醫院副院長高雄醫學大學小兒科學教授高雄醫學大學附設醫院小兒過敏及免疫科主治醫師 門診時間表  上午診  看診日期：1090828　星期 5　診間號：兒科一診(A302) 看診日期：1090904　星期 5　診間號：兒科一診(A302) 看診日期：1090911　星期 5　診間號：兒科一診(A302) 下午診  查無看診日期 夜診  看診日期：1090901　星期 2　診間號：兒科二診(A301) 看診日期：1090908　星期 2　診間號：兒科二診(A301) 看診日期：1090915　星期 2　診間號：兒科二診(A301)'            
#                 #取得上午診下午診與夜診之資料串:find_str，並進行工作時段(上午診/下午診/夜診)之字串切割
                
#                 find_str_lst=find_str.split('上午診')
#                 doc_job_str= find_str_lst[1]            
#                 doc_job_lst = doc_job_str.split('下午診')
#                 #---------上午診資料字串
#                 noon_job_str = doc_job_lst[0].lstrip() 
#                 #---------下午診資料字串
#                 afternoon_job_str=doc_job_lst[1].split('夜診')[0].lstrip()
#                 #---------夜晚診資料字串
#                 night_job_str=doc_job_lst[1].split('夜診')[1].lstrip()            
#                 #line_bot_api.push_message(uid, TextSendMessage(find_str))
                
#                 line_mark_0 = '**************************\n'
#                 line_mark = '-------------------------\n'
#     #--------------------------上午診日期資訊處理-------------------------------------                                      
#                 if len(noon_job_str) > 7:
#                     noon_clinic_timeinfo = line_mark_0 + '[上午診]\n'
#                     noon_job_list=noon_job_str.split('看診')    
#                     job_period=1  # 看診時段參數 FOR掛號使用   Reg   
                    
#                     job_state=[]
#                     # 設定第一筆的看診狀態
#                     if noon_job_list[0].find('滿')!=-1:
#                         job_state.append('額滿')
#                     elif noon_job_list[0].find('休')!=-1:
#                         job_state.append('額滿')
#                     else:
#                         job_state.append('可掛號')
#                     job_record=[]    
#                     i=1  
#                     while i < len(noon_job_list):        
#                         if noon_job_list[i].find('滿')!=-1:
#                             job_state.append('額滿')
#                             job_record.append(noon_job_list[i][:-5])
#                         elif noon_job_list[i].find('休診')!=-1:
#                             job_state.append('休診')
#                             job_record.append(noon_job_list[i][:-5])
#                         else:
#                             job_state.append('可掛號')
#                             job_record.append(noon_job_list[i])
#                         i=i+1
                        
#                     del job_state[i-1]  #刪除多餘看診狀態           
#                     #---------列印上午時段門診時間       
#                     k=0
#                     while k < len(job_state) :
#                         job_date=''
#                         if job_state[k]=='可掛號':
#                             job_date=job_record[k][3:10]
                            
#                             #掛診-日期參數取得
#                             job_yr=str(int(job_date[0:3])+1911)
#                             job_mnth=job_date[3:5]
#                             Job_day=job_date[5:9]
#                             reg_job_date=job_yr+'/'+job_mnth+'/'+Job_day  #Reg 
#                             # k=0
                            
#                             #Dept_Name參數取得
#                             #掛診-科別處理，A代表大樓號碼與位置
#                             #復健科與牙科要例外處理，因為沒有A的診間號碼
#                             if dept_code == '1800':
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('(5')
#                                 Dept_Name=job_record[k][pos1+2:pos2] #Reg
                                
#                             elif dept_code == '1300':  #牙科
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('(2')
#                                 Dept_Name=job_record[k][pos1+2:pos2] #Reg
                                
#                             else:    
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('A')
#                                 Dept_Name=job_record[k][pos1+2:pos2-1] #Reg
                             
#                           #   print (job_record[k]+job_state[k])
                            
#                             reg_site = DoctorInfo5.reg_url(reg_job_date,job_period,DeptNo,DocNo,Doc_Name,Dept_Name)
#                             clinic_rec= line_mark +'(' + job_state[k]+')'+ job_record[k] +reg_site +'\n'                            
#                             noon_clinic_timeinfo = noon_clinic_timeinfo + clinic_rec
#                         else:
#                             clinic_rec= line_mark +'(' +job_state[k]+')' + job_record[k]+'\n'
#                             noon_clinic_timeinfo = noon_clinic_timeinfo + clinic_rec
#                         k=k+1
#                     #line_bot_api.push_message(uid, TextSendMessage(noon_clinic_timeinfo))
#                 else:  #找不到看診資料     
#                     noon_clinic_timeinfo = line_mark_0 + '[上午診]:查無資料 \n'
#                     #line_bot_api.push_message(uid, TextSendMessage(noon_clinic_timeinfo))
    
#     #--------------------------下午診日期資訊處理-------------------------------------                                            
#                 if len(afternoon_job_str) > 7:
                    
#                       afn_clinic_timeinfo = line_mark_0 + '[下午診]\n'
#                       afternoon_job_list=afternoon_job_str.split('看診')    
#                       job_period = 2  #看診時段參數 FOR掛號使用   
                    
#                       job_state=[]
#                       # 設定第一筆的看診狀態
#                       if afternoon_job_list[0].find('滿')!=-1:
#                           job_state.append('額滿')
#                       elif afternoon_job_list[0].find('休')!=-1:
#                           job_state.append('額滿')
#                       else:
#                           job_state.append('可掛號')
#                       job_record=[]    
#                       i=1  
#                       while i < len(afternoon_job_list):        
#                           if afternoon_job_list[i].find('滿')!=-1:
#                               job_state.append('額滿')
#                               job_record.append(afternoon_job_list[i][:-5])
#                           elif afternoon_job_list[i].find('休診')!=-1:
#                               job_state.append('休診')
#                               job_record.append(afternoon_job_list[i][:-5])
#                           else:
#                               job_state.append('可掛號')
#                               job_record.append(afternoon_job_list[i])
#                           i=i+1
#                       del job_state[i-1] #刪除多餘看診狀態
                    
#                       #---------列印下午時段門診時間
#                       #print('[下午診]')
#                       k=0
#                       while k < len(job_state) :
#                           job_date=''
#                           if job_state[k]=='可掛號':
                             
#                               #掛診-日期參數取得
#                               job_date=job_record[k][3:10]
#                               job_yr=str(int(job_date[0:3])+1911)
#                               job_mnth=job_date[3:5]
#                               Job_day=job_date[5:9]
#                               reg_job_date=job_yr+'/'+job_mnth+'/'+Job_day
                             
#                               #Dept_Name參數取得
#                               #掛診-科別處理，A代表大樓號碼與位置
#                               #復健科與牙科要例外處理，因為沒有A的診間號碼
#                               if dept_code == '1800':
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('(5')
#                                 Dept_Name=job_record[k][pos1+2:pos2] #Reg
                                
#                               elif dept_code == '1300':  #牙科
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('(2')
#                                 Dept_Name=job_record[k][pos1+2:pos2] #Reg
                                
#                               else:    
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('A')
#                                 Dept_Name=job_record[k][pos1+2:pos2-1] #Reg
#                               # pos1=job_record[k].find('號')
#                               # pos2=job_record[k].find('A')
#                               # Dept_Name=job_record[k][pos1+2:pos2-1]
                             
#                               #print (job_record[k]+job_state[k])
                             
#                               reg_site = DoctorInfo5.reg_url(reg_job_date,job_period,DeptNo,DocNo,Doc_Name,Dept_Name)
#                               clinic_rec= line_mark +'(' + job_state[k]+')'+ job_record[k] +reg_site +'\n'
#                               afn_clinic_timeinfo = afn_clinic_timeinfo + clinic_rec
#                           else:
#                               clinic_rec= line_mark +'(' +job_state[k]+')' + job_record[k]+'\n'
#                               afn_clinic_timeinfo = afn_clinic_timeinfo + clinic_rec        
#                           k=k+1
                     
#                       #line_bot_api.push_message(uid, TextSendMessage(afn_clinic_timeinfo))  
                
#                 else:    #找不到看診資料 
#                       afn_clinic_timeinfo = line_mark_0 + '[下午診]:查無資料 \n'
#                     # line_bot_api.push_message(uid, TextSendMessage(afn_clinic_timeinfo))
#       # #--------------------------晚診診日期資訊處理-------------------------------------                            
#                 if len(night_job_str) > 7:
#                       night_clinic_timeinfo = line_mark_0 +'[夜診]\n'
#                       night_job_list=night_job_str.split('看診')    
#                       job_period=3   #看診時段參數 FOR掛號使用
                         
#                       job_state=[]    
#                       # 設定第一筆的看診狀態
#                       if night_job_list[0].find('滿')!=-1:
#                           job_state.append('額滿')
#                       elif night_job_list[0].find('休')!=-1:
#                           job_state.append('額滿')
#                       else:
#                           job_state.append('可掛號')
                    
#                       job_record=[]    
#                       i=1 
                    
#                       while i < len(night_job_list):        
#                           if night_job_list[i].find('滿')!=-1:
#                               job_state.append('額滿')
#                               job_record.append(night_job_list[i][:-5])
#                           elif night_job_list[i].find('休診')!=-1:
#                               job_state.append('休診')
#                               job_record.append(night_job_list[i][:-5])
#                           else:
#                               job_state.append('可掛號')
#                               job_record.append(night_job_list[i])
#                           i=i+1
#                       del job_state[i-1] # #刪除多餘看診狀態
#                       #---------列印下午時段門診時間
                    
#                       #print('[夜晚診]')
#                       k=0
#                       while k < len(job_state) :
#                           job_date=''
#                           if job_state[k]=='可掛號':
                             
#                               #掛診-日期參數取得
#                               job_date=job_record[k][3:10]
#                               job_yr=str(int(job_date[0:3])+1911)
#                               job_mnth=job_date[3:5]
#                               Job_day=job_date[5:9]
#                               reg_job_date=job_yr+'/'+job_mnth+'/'+Job_day
                             
#                               #Dept_Name參數取得
#                               #掛診科別處理，A代表大樓號碼與位置
#                               #復健科與牙科要例外處理，因為沒有A的診間號碼
#                               if dept_code == '1800':
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('(5')
#                                 Dept_Name=job_record[k][pos1+2:pos2] #Reg
                                
#                               elif dept_code == '1300':  #牙科
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('(2')
#                                 Dept_Name=job_record[k][pos1+2:pos2] #Reg
                                
#                               else:    
#                                 pos1=job_record[k].find('號')
#                                 pos2=job_record[k].find('A')
#                                 Dept_Name=job_record[k][pos1+2:pos2-1] #Reg
                              
                              
#                               # pos1=job_record[k].find('號')
#                               # pos2=job_record[k].find('A')
#                               # Dept_Name=job_record[k][pos1+2:pos2-1]
#                             # print (job_record[k]+job_state[k])
                             
#                               reg_site = DoctorInfo5.reg_url(reg_job_date,job_period,DeptNo,DocNo,Doc_Name,Dept_Name)
#                               clinic_rec= line_mark +'(' + job_state[k]+')'+ job_record[k] +reg_site +'\n'                             
#                               night_clinic_timeinfo = night_clinic_timeinfo + clinic_rec
#                           else:
#                               clinic_rec= line_mark +'(' +job_state[k]+')' + job_record[k]+'\n'
#                               night_clinic_timeinfo = night_clinic_timeinfo + clinic_rec        
#                           k=k+1
                         
#                       #line_bot_api.push_message(uid, TextSendMessage(night_clinic_timeinfo))    
                
#                 else:   #找不到看診資料   
#                       night_clinic_timeinfo = line_mark_0 +'[夜診]:查無資料\n'
#                       #line_bot_api.push_message(uid, TextSendMessage(night_clinic_timeinfo))            
                            
#                 all_clinic_timeinfo = clinic_timeinfo_title + noon_clinic_timeinfo + afn_clinic_timeinfo +night_clinic_timeinfo 
                
                
#                 line_bot_api.push_message(uid, TextSendMessage(all_clinic_timeinfo)) # 花點時間回應，所以用PUSH
#             else:
#                 line_bot_api.reply_message(event.reply_token,TextSendMessage('找不到您要掛號的醫師的名字!!!'))
       
#         else:    # 假如"掛號後面之敘述不是要找醫生
#             line_bot_api.reply_message(event.reply_token,TextSendMessage('想掛號甚麼?醫師還是科別'))
                                                                
#         return 0        
####################################################################################
##        user_message= '簡介張科醫師'
##        # import KMSH_DoctorDB_Inquiry
################################################################################        
    elif user_message.find('簡介') != -1 and user_message.find('醫師')!= -1 :            
        PA=user_message.find('簡介')
        PB=user_message.find('醫師')
        name_len=PB-PA
        
        if name_len >= 5:            
            Doc_Name = user_message[PB-3:PB] #Reg 參數
        else:
            Doc_Name = user_message[PB-2:PB] 
        
        doc_found= False
        doc_info=KMSH_DoctorDB_Inquiry.intro(Doc_Name)
        
        if len(doc_info)!=0:
            doc_found=True
            position= doc_info[0]['position'].lstrip()
            degree= doc_info[0]['degree'].lstrip()
            clinic_spec = doc_info[0]['clinic_spec'].lstrip()
            licen=doc_info[0]['licen'].rstrip()
            med_train=doc_info[0]['med_train'].rstrip()
        
        if  doc_found: 
            line_mark_0 = '\n**************************' 
            line_mark = '-------------------------'
            doc_introduction=''
            position='\n[現職]\n'+'- '+ position.replace('。','。\n-')
            degree='\n[學歷]\n'+'- ' + degree.replace('。','。\n-')
            licen= '\n[醫師執照]\n'+'- ' + licen.replace('。','。\n-')
            med_train='\n[醫學訓練]\n' + '- ' + med_train.replace('。','。\n-')
            clinic_spec='\n[臨床主治]\n' + clinic_spec.replace('。','。\n')
            doc_introduction='['+ Doc_Name + '醫師簡介]'+line_mark_0 + position + line_mark + degree + line_mark+ med_train +  line_mark + clinic_spec
            
            #line_bot_api.push_message(uid, TextSendMessage(doc_introduction))
            line_bot_api.reply_message(event.reply_token,TextSendMessage(doc_introduction))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage('找不到您要了解的醫師的名字!!!'))
        return 0
#################################################################################    
##                            內科看診進度選單 
###############################################################################
    elif user_message.find('內科看診進度選單') != -1:
        care_message = TemplateSendMessage(
            alt_text='內科門診看診進度查詢表單',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='內科門診看診進度-1/4',
                        text='請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='所有內科看診進度',
                                text='全內科看診進度'
                            ),
                            MessageTemplateAction(
                                label='胃腸內科看診號碼',
                                text='胃腸內科看診進度'
                            ),
                            MessageTemplateAction(
                                label='肝膽胰內科看診號碼',
                                text='肝膽胰內科看診進度'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='內科門診看診進度-2/4',
                        text='請按以下連結查詢',
                        actions=[
                            MessageTemplateAction(
                                label='胸腔內科看診號碼',
                                text='胸腔內科看診進度'
                            ),
                            MessageTemplateAction(
                                label='心臟血管內科看診號碼',
                                text='心臟血管內科看診進度'
                            ),
                            MessageTemplateAction(
                                label='內分泌新陳代謝內科看診號碼',
                                text='分泌科看診進度'
                            )                            
                        ]
                    ), 
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='內科門診看診進度-3/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='血液腫瘤內科看診號碼',
                                text='血液科看診進度'
                            ),
                              MessageTemplateAction(
                                label='過敏免疫風濕內科看診號碼',
                                text='過敏科看診進度'
                            ),
                              MessageTemplateAction(
                                label='腎臟內科看診號碼',
                                text='腎臟科看診進度'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='內科門診看診進度-4/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='感染內科看診號碼',
                                text='感染科看診進度'
                            ),
                              MessageTemplateAction(
                                label='神經內科看診號碼',
                                text='神內科看診進度'
                            ),
                              MessageTemplateAction(
                                label='失智症整合門診看診號碼',
                                text='失智科看診進度'
                            )                            
                        ]
                    )
                    #------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage 
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0 
##############################################################################
#                          外科看診進度選單
###############################################################################
    elif user_message.find('外科看診進度選單') != -1:
        care_message = TemplateSendMessage(
            alt_text='外科門診看診進度查詢表單',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='外科門診看診進度-1/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='全部外科看診號碼',
                                text='全外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='腦神經外科看診號碼',
                                text='腦神經外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='心臟血管外科看診號碼',
                                text='心臟血管外科看診進度'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='外科門診看診進度-2/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='胸腔外科看診號碼',
                                text='胸腔外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='胃腸及一般外科看診號碼',
                                text='胃腸及一般外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='肝膽胰外科看診號碼',
                                text='肝膽胰外科看診進度'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='外科門診看診進度-3/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='乳房外科特診看診號碼',
                                text='乳房外科特診看診進度'
                            ),
                              MessageTemplateAction(
                                label='整形外科看診號碼',
                                text='整形外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='美容門診(完全自費)看診號碼',
                                text='美容科看診進度'
                            )                            
                        ]
                    ),  
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='外科門診看診進度-4/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='耳鼻喉頭頸外科看診號碼',
                                text='耳鼻喉頭頸外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='口腔顎面外科看診號碼',
                                text='口腔顎面外科看診進度'
                            ),
                              MessageTemplateAction(
                                label='全部外科看診號碼',
                                text='全外科看診進度'
                            )                            
                        ]
                    )                    
#------------------------------------------------------------------------------                    
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage 
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0                     
##############################################################################
#                          特別門診看診進度選單
###############################################################################
    elif user_message.find('特別門診看診進度選單') != -1:
        care_message = TemplateSendMessage(
            alt_text='特別門診看診進度選單',
            template=CarouselTemplate(
                columns=[
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='特別門診看診進度-1/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='全部門診看診號碼',
                                text='整合門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='更年期特別門診看診號碼',
                                text='更年門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='高齡特別門診看診號碼',
                                text='高齡門診看診號碼'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='特別門診看診進度-2/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='戒菸門診看診號碼',
                                text='戒菸門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='減重塑身門診看診號碼',
                                text='減重門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='旅遊醫學門診看診號碼',
                                text='旅遊門診看診號碼'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='特別門診看診進度-3/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='失智症整合門診看診號碼',
                                text='失智門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='美容門診(完全自費)看診號碼',
                                text='美容門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='三高整合門診看診號碼',
                                text='三高門診看診號碼'
                            )                            
                        ]
                    ),  
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='特別門診看診進度-4/4',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='咀嚼吞嚥困難特別門診看診號碼',
                                text='咀嚼門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='戒菸門診看診號碼',
                                text='戒菸門診看診號碼'
                            ),
                              MessageTemplateAction(
                                label='全部門診看診號碼',
                                text='整合門診看診號碼'
                            )                            
                        ]
                    )                    
#------------------------------------------------------------------------------                    
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage 
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0  
###############################################################################
#                            所有科別看診進度選單
#                    user_message='看診進度查詢'        
###############################################################################
    elif user_message.find('看診進度選單') != -1:
        care_message = TemplateSendMessage(
            alt_text='門診看診進度查詢表單I',
            template=CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='門診看診進度-1/6',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='全部看診號碼',
                                text='全部看診進度'
                            ),
                              MessageTemplateAction(
                                label='內科看診號碼-選單',
                                text='內科看診進度選單'
                            ),
                              MessageTemplateAction(
                                label='外科看診號碼-選單',
                                text='外科看診進度選單'
                            )                            
                        ]
                    ),                        

#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='門診看診進度-2/6',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='特別門診看診進度-選單',
                                text='特別門診看診進度選單'
                            ),
                              MessageTemplateAction(
                                label='小兒科看診號碼',
                                text='兒科看診進度'
                            ),
                              MessageTemplateAction(
                                label='婦產科看診號碼',
                                text='婦產科看診號碼'
                            )                            
                        ]
                    ),                                                                

#------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='門診看診進度-3/6',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='神經內科看診號碼',
                                text='神內看診進度'
                            ),
                              MessageTemplateAction(
                                label='精神科看診號碼',
                                text='精神科看診進度'
                            ),
                              MessageTemplateAction(
                                label='牙科看診號碼',
                                text='牙科看診進度'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='門診看診進度-4/6',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='皮膚科看診號碼',
                                text='皮膚科看診進度'
                            ),
                              MessageTemplateAction(
                                label='眼科看診號碼',
                                text='眼科看診號碼'
                            ),
                              MessageTemplateAction(
                                label='泌尿科看診號碼',
                                text='泌尿科看診號碼'
                            )                            
                        ]
                    ),  
#------------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='  ',
                        title='門診看診進度-5/6',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='家庭醫學科看診號碼',
                                text='家醫科看診號碼'
                            ),
                              MessageTemplateAction(
                                label='職業病科看診號碼',
                                text='職業科看診進度'
                            ),
                              MessageTemplateAction(
                                label='骨科看診號碼',
                                text='骨科看診號碼'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
#                        thumbnail_image_url='   ',
                        title='門診看診進度-6/6',
                        text='請按以下連結查詢',
                        actions=[
                              MessageTemplateAction(
                                label='復健科看診號碼',
                                text='復健科看診號碼'
                            ),
                              MessageTemplateAction(
                                label='放射科看診號碼',
                                text='放射科看診號碼'
                            ),
                              MessageTemplateAction(
                                label='全部看診號碼',
                                text='全部看診進度'
                            )                            
                        ]
                    ), 
                                                           
#------------------------------------------------------------------------------
                ]
            )
        )         # 結束MESSAGE-TemplateSendMessage 
        line_bot_api.reply_message(event.reply_token,care_message)
        #line_bot_api.reply_message(event.reply_token,care_message2)
        #line_bot_api.push_message(uid, care_message)
        #line_bot_api.push_message(uid, care_message2)
        return 0             
###############################################################################  
#   辦判斷是否含有關鍵詞'看診進度'，並取出查詢科別之前兩關鍵字源，
#   以查詢目前開設科別之看診進度
#   # user_message='胸腔科看診進度'        
###############################################################################   
    elif user_message.find('看診進度') !=-1:
        user_message=user_message.lstrip()  #去除前面空白字元
       
        if user_message.find('科')!=-1:
            dept_pos= user_message.find('科') 
            Qdept=user_message[dept_pos-2:dept_pos]
        elif user_message.find('門診')!=-1:
            dept_pos= user_message.find('門診') 
            Qdept=user_message[dept_pos-2:dept_pos] 
        else:
            dept_pos=user_message.find('看診進度')
            Qdept=user_message[dept_pos-2:dept_pos]                     
       
        # 例外與特別字元與常用字串處理 
        if user_message.find('兒') !=-1:
            Qdept='兒科'        
        elif user_message.find('骨') !=-1:
            Qdept='骨科'            
        elif user_message.find('牙') !=-1:
            Qdept='牙'
        elif user_message.find('全外') !=-1:
            Qdept='外' 
        elif user_message.find('全內') !=-1:
            Qdept='內' 
        elif user_message.find('眼') !=-1:
            Qdept='眼科'
        elif user_message.find('戒菸') !=-1:
            Qdept='戒煙'            
        elif user_message.find('腦神經') != -1:
            Qdept='神經'
        elif user_message.find('神內') != -1:
            Qdept='神內'            
        elif user_message.find('整合') !=-1:
            Qdept='門診'
        elif user_message.find('所有') !=-1:
            Qdept=''        
        elif user_message.find('全部') !=-1:
            Qdept=''            
        elif user_message.find('小港醫院') !=-1:
            Qdept=''
        line_mark0='************************'
        line_mark='------------------------'
        if clinic_time.avaiable():            
            #line_bot_api.reply_message(event.reply_token,TextSendMessage('要等耐心我一下喔!幫您查詢候診號碼需要一點時間!6秒後沒回覆代表我累嘞，請使用其他服務!>_<'))
            Response_Info = QWaitList.answer(Qdept)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_Info))
            #line_bot_api.push_message(uid, TextSendMessage(Response_Info))
        else:
            clinic_period_info='高雄市立小港醫院門診時間如下:\n'+line_mark0 +'\n[早上診]\n時間:08:30~12:00。\n[下午診]\n時間:13:30~17:00。\n[夜晚診]\n時間:18:00~20:30。\n'+ line_mark +'\n其餘時間不提供門診看診號碼查詢喔!(星期六只有早上看診，星期日全天休診)'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(clinic_period_info))            
                
        return 0 
#----------------------------看診號----------------------------------------    
    elif user_message.find('看診號') !=-1:
        user_message=user_message.lstrip()
        if user_message.find('科')!=-1:
            dept_pos= user_message.find('科') 
            Qdept=user_message[dept_pos-2:dept_pos]
        elif user_message.find('門診')!=-1:
            dept_pos= user_message.find('門診') 
            Qdept=user_message[dept_pos-2:dept_pos] 
        else:
            dept_pos=user_message.find('看診號')
            Qdept=user_message[dept_pos-2:dept_pos]                       
       
        # 例外與特別字元與常用字串處理 
        if user_message.find('兒') !=-1:
            Qdept='兒科'        
        elif user_message.find('骨') !=-1:
            Qdept='骨科'            
        elif user_message.find('牙') !=-1:
            Qdept='牙'
        elif user_message.find('全外') !=-1:
            Qdept='外' 
        elif user_message.find('全內') !=-1:
            Qdept='內' 
        elif user_message.find('眼') !=-1:
            Qdept='眼科'
        elif user_message.find('戒菸') !=-1:
            Qdept='戒煙'            
        elif user_message.find('腦神經') != -1:
            Qdept='神經'
        elif user_message.find('神內') != -1:
            Qdept='神內' 
        elif user_message.find('整合') !=-1:
            Qdept='門診'    
        elif user_message.find('所有') !=-1:
            Qdept=''        
        elif user_message.find('全部') !=-1:
            Qdept=''            
        elif user_message.find('小港醫院') !=-1:
            Qdept=''
        line_mark0='************************'
        line_mark='------------------------'
        if clinic_time.avaiable():            
            #line_bot_api.reply_message(event.reply_token,TextSendMessage('要等耐心我一下喔!幫您查詢候診號碼需要一點時間!6秒後沒回覆代表我累嘞，請使用其他服務!>_<'))
            Response_Info = QWaitList.answer(Qdept)
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_Info))
            #line_bot_api.push_message(uid, TextSendMessage(Response_Info))
        else:
            clinic_period_info='高雄市立小港醫院門診時間如下:\n'+line_mark0 +'\n[早上診]\n時間:08:30~12:00。\n[下午診]\n時間:13:30~17:00。\n[夜晚診]\n時間:18:00~20:30。\n'+ line_mark +'\n其餘時間不提供門診看診號碼查詢喔!(星期六只有早上看診，星期日全天休診)'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(clinic_period_info))            
        return 0 
############################ 就診建議的狀態下的 文字命令#########################################
    elif user_message.find('症狀') !=-1:
        Confirm_Dig.Qry(uid)
    elif user_message.find('H') !=-1 or user_message.find('N') !=-1 or user_message.find('U') !=-1 or user_message.find('L') !=-1 or user_message.find('A') !=-1:
        Confirm_Dig.Qry(uid)  
##############################################################################    
    elif user_message.find('院內指引') !=-1:
        
        reg_message = TemplateSendMessage(
            alt_text='院內指引',
            template = CarouselTemplate(
                columns=[
#------------------------------------------------------------------------------                    
                CarouselColumn(                    
                    image_aspect_ratio='square',
                    thumbnail_image_url='https://lh3.googleusercontent.com/Q8rSHC9Y7Ag1WBICr5b3x6kyv-CvQvGbwCifo4Z5rxl9jcJeH6beg9v4sqrrkW04OynQtbVqnYZAOCiRVtMyDU_oASVskYuQFTZkTam-WafzF545gzVHzeGSGQU-r3bKgZhgDZE6PA=w1200',
                    title='小港醫院資訊服務APP',
                    text= '院內路徑指引',
                    actions= [
                        URITemplateAction(
                            label= '院內路徑指引',
                            uri= 'http://service.smartappscreator.com/h5/403229135/html5'
                            ),
                        # URITemplateAction(
                        #     label= '小港醫院醫療資訊APP',
                        #     uri= 'http://service.smartappscreator.com/h5/979021789/html5'
                        #     ),
                        
                       
                           ]
                      ),
#------------------------------------------------------------------------------                    
                CarouselColumn(                    
                    image_aspect_ratio='square',
                    thumbnail_image_url='https://lh3.googleusercontent.com/9u3vasyodU6kdUKknqdWXTM9yCpuL9PtYktbhQVxobZXRLTJp-UAzU8o3k6_LsT8QjYs9TyjPaugK2saRgureGZsxisWkvNLeC_ZYB0OV_ggjy5eFDJyNN6UoUNki10fF3Niyew-Gg=w1200',
                    title='小港醫院資訊服務APP',
                    text= 'Hospital Navigation ',
                    actions= [
                        URITemplateAction(
                            label= 'Hospital Navigation',
                            uri= 'http://service.smartappscreator.com/h5/285021074/html5'
                            ),
                        # URITemplateAction(
                        #     label= '小港醫院醫療資訊APP',
                        #     uri= 'http://service.smartappscreator.com/h5/979021789/html5'
                        #     ),
                        
                       
                           ]
                      ),                
#------------------------------------------------------------------------------                
               ]
           )
        )
        
        line_bot_api.reply_message(event.reply_token,reg_message) 
                               
        return 0          
##############################################################################     
#                     都找不到就回答看不懂，回客服電話訊息
#############################################################################        
    else:  
        reg_message = TemplateSendMessage(
            alt_text='電話掛號服務',
            template = CarouselTemplate(
                image_aspect_ratio='square',
                thumbnail_image_url='https://lh3.googleusercontent.com/9yPKsQk1n-LO4Yo1hETOr0T5IBLeZJi42HU3dEiRVXe2ynwJsaw-1Sp3tGMT7qX8CqB1b7Vv86NxQvnwUku4KjmYmOMJE9kZpJpVrMY2vG3iSiLo_sWBnILZfURdpI6S-glJ5atuUg=w400',
                title='小港醫院電話掛號服務',
                text= '無法了解您的意思! ≧ω≦ \n請打電話給客服中心，\n請按以下連結查詢:',
                actions= [
                    MessageTemplateAction(
                        label= '總機電話號碼',
                        text= '小港醫院電話號碼'
                        ),
                    MessageTemplateAction(
                        label= '人工掛號電話(只到下午4點)',
                        text= '小港醫院人工掛號專線'
                        ),
                    MessageTemplateAction(
                        label= '語音掛號專線',
                        text= '小港醫院語音掛號專線'
                        ),
                   
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,reg_message) 
        
        # S0='無法了解您的意思! ≧ω≦ \n請打電話給客服中心:078036783 \n-------------------\n'             
        # Response_Info=S0
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_Info))        
        return 0
                                
#--------------------------------------------------------------
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 27017))
    app.run(host='0.0.0.0', port=port)

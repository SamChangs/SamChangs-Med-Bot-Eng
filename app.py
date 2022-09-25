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
line_bot_api = LineBotApi('Q65IelWgsFiWzJL7srk++OKbP70q9OzqVJXAY3+iXKOOb/E0tVZ2+xJxgrfdN0jbmYmcz2SQEQIFugb0WMmSYkbO3odUAhS/NSVKdmCK60lk6omrnKTWc34zfSjAwoHVCf9ebnmd62zjdFyfE9EWfwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('cbaa8a628d50ff5c58ea16bad479bfa1')
#'cbaa8a628d50ff5c58ea16bad479bfa1'
# LINE BOT 開發者預設ID，以接收啟動信息 
# line_bot_api.push_message('Ub719dea14f41f0e9ac414e5b95435c9c', TextSendMessage(text='OK,I am DR. Echo! May I help you? ｡^‿^｡'))

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
            print(message)
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
            Response_info = 'OK. Translation Function terminated!'
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
                    Response_info='(1)OK. Switch to ['+new_lang_name +'翻譯]!\n(2)To stop the translation, please type the text command: [Cancel translation function], [Quit], or [quit]!\n(3)The speech translation takes about 6-8 seconds! Please be patient.'
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
                alt_text='Foreign language translation menu',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/FtA-p01ZiAP1eA-8WOTFAlU793Q4smX7OgGxjD0svgWKR-3nmiIwADfRqSezAQSPlaHOHP0FHayqz2Hu2i1zlazGeC0GuPgqwq_-IZhb7pNRgv8Nk-ePBe7GSTdPcr-zsS9mHaG6NQ=w600',
                            title='Foreign language translation menu-1/10',
                            text='Asian language translation(1/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='English',
                                    text='翻譯英語'
                                ),
                                MessageTemplateAction(
                                    label='Japanese',
                                    text='翻譯日語'
                                ),
                                MessageTemplateAction(
                                    label='Korean',
                                    text='翻譯韓語'
                                )                            
                            ]
                        ),                        
    # -----------------------------------------------------------------------------
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/FKSRSGWwJttJXxWqGVQh1NK_B6Y0coj7zjIsfBw2zCLOXqyCoJdEc3p1QfrslhUH_vLJAch9duWwh_4qSJ2rQzYzMXVGqIp9RKmfdUVLTtNhhKwAtBDUw_m6hJthgssXy8mqYY9BvQ=w600',
                            title='Foreign language translation menu-2/10',
                            text='Asian language translation(2/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='Vietnamese',
                                    text='翻譯越南語'
                                ),
                                MessageTemplateAction(
                                    label='Malaysian',
                                    text='翻譯馬來西亞語'
                                ),
                                MessageTemplateAction(
                                    label='Indonesian',
                                    text='翻譯印尼語'
                                )                            
                            ]
                        ), 
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/ii9yNKlFFIHKc8JS3Lp0xJJbbFVZxF-IIXAo9UgaUXBMzgmu2eR57Q8yfroKg084mRd-ooBLjvxwBeZRVdYRIDNqm6gW2bDOyUFVT6zD9h4GOu0lMjux1QfeGiUblBNs1Lahwffjjw=w600',
                            title='Foreign language translation menu-3/10',
                            text='Asian language translation(3/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='Thai',
                                    text='翻譯泰語'
                                ),
                                MessageTemplateAction(
                                    label='Hindi',
                                    text='翻譯印度語'
                                ),
                                MessageTemplateAction(
                                    label='Arab',
                                    text='翻譯阿拉伯語'
                                )                            
                            ]
                        ),
    # -----------------------------------------------------------------------------
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/Dg7oaQ7DqWg9VKjb0jlIJIoEeWXsxMnj5LBUU_Go3kyf2M64LYYjtKW03hTiibqyvhX-GO-ApNWR0M_4htARzptPyNBKvreuxwaP_4yt2xsc_-jD7mbd-J_vXBDjxDV4leZLMuujeQ=w600',
                            title='Foreign language translation menu-4/10',
                            text='歐Asian language translation(4/4)',
                            actions=[
                                MessageTemplateAction(
                                    label='Hebrew (Israel)',
                                    text='翻譯希伯來語'
                                ),
                                MessageTemplateAction(
                                    label='Turkish',
                                    text='翻譯土耳其語'
                                ),
                                MessageTemplateAction(
                                    label='Bulgarian',
                                    text='翻譯保加利亞語'
                                )                            
                            ]
                        ), 
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/lYYC3KONJ-r8MPuO6NlR92JQocBqioz6d4L_IJMfcWVuZ54IT4jnOGrRB4Nbfm-B-eolh5ijP7tuJCIdPprH3VGf_6zcuDyWrWJGqS5maLxdyyRLaOy3TcKoOlDc3mSE3g599ANr2Q=w600',
                            title='Foreign language translation menu-5/10',
                            text='European language translation(1/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='English',
                                    text='翻譯英語'
                                ),
                                MessageTemplateAction(
                                    label='French',
                                    text='翻譯法語'
                                ),
                                MessageTemplateAction(
                                    label='German',
                                    text='翻譯德語'
                                )                            
                            ]
                        ),
    #-----------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/EboLBmHXVpQlk3hrpdHZlLEzjnGGAvjuCGsI32si5ekjX-t6CcUWe6AX1o0lElKvj4pfKLINxMKDzaWFFjliDHMzgTk35M1ShkRlT0S8CrUctVVAHC51Y0zFgVlmRMcdp_U4lC8kgw=w600',
                            title='Foreign language translation menu-6/10',
                            text='European language translation(2/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='Spanish',
                                    text='翻譯西班牙語'
                                ),
                                MessageTemplateAction(
                                    label='Portuguese',
                                    text='翻譯葡萄牙語'
                                ),
                                MessageTemplateAction(
                                    label='Brazilian',
                                    text='翻譯巴西語'
                                )                            
                            ]
                        ),                                          
    #------------------------------------------------------------------------------
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/_rparADUnbJJnpb65H7ayhR1AGVm3NWNbDBZiyjnnzxZP6kgvWe4Umhbom9n4ux9IqLJw4f11FTNuSqiWEtGgUvCpPKztQPqWHVPdRJw3QuLfT7eDEo6oFNZCRES9HCeVESSGC3Dpw=w600',
                            title='Foreign language translation menu-7/10',
                            text='European language translation(3/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='Italian',
                                    text='翻譯Greek'
                                ),
                                MessageTemplateAction(
                                    label='Greek',
                                    text='翻譯希臘語'
                                ),
                                MessageTemplateAction(
                                    label='Hungarian',
                                    text='翻譯匈牙利語'
                                )                            
                            ]
                        ),                        
     
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/5ihsLofivptsynCymdVOH4mVJSU_BVkkCV3G9FuDVRbB-94f11bxTYiWJ9FinDcFkuHZbfgaPbdDEwaprd9eLsoZWV6i6er0zklomk035VXUwke0mCjtK2Ljm6pBd_1YRx3vkvvQ_A=w600',
                            title='Foreign language translation menu-8/10',
                            text='European language translation(4/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='Polish',
                                    text='翻譯波蘭語'
                                ),
                                MessageTemplateAction(
                                    label='Danish',
                                    text='翻譯丹麥語'
                                ),
                                MessageTemplateAction(
                                    label='Dutch',
                                    text='翻譯荷蘭語'
                                )                            
                            ]
                        ),
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/-2lYj7IxjNABSjyP-YhmFakXpuWuI-1sxc6Bms2vH2qHXcLs6nM_OTW9caDURCwcteDgP72jn-naFj074hyP5GvLXWXRekkPwAZDfIaNyP76QjOz7a96i90WrZy93BExUFEOOQxjgA=w600',
                            title='Foreign language translation menu-9/10',
                            text='European language translation(5/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='Swedish',
                                    text='翻譯瑞典語'
                                ),
                                MessageTemplateAction(
                                    label='Finnish',
                                    text='翻譯芬蘭語'
                                ),
                                MessageTemplateAction(
                                    label='Norwegian',
                                    text='翻譯挪威語'
                                )                            
                            ]
                        ),                    
    #------------------------------------------------------------------------------                    
                        CarouselColumn(
                            thumbnail_image_url='https://lh3.googleusercontent.com/ixYCUmAcRByFRZtPSmljEScE3rFss1BqiflLUUX4UHqHwOTlIuzREIG3WzH2D-ltmWgxUnnaKL7urxLOngzoPcXxmiUKrDBOiTMJtnybrsJQuifwY84YitAFrA1RfOoQ-V5x0GRTFw=w600',
                            title='Foreign language translation menu-10/10',
                            text='European language translation(6/6)',
                            actions=[
                                MessageTemplateAction(
                                    label='Russian',
                                    text='翻譯俄羅斯語'
                                ),
                                MessageTemplateAction(
                                    label='Czech',
                                    text='翻譯捷克語'
                                ),
                                MessageTemplateAction(
                                    label='Romanian',
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
        if user_message.find('Cancel a visit') != -1 or user_message.find('Leave the Medical Department') != -1:
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)  
            Response_info='OK, leave the [Medical Department Recommendation] function!'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
        elif  user_message.find('Medical Department Recommendation') != -1:
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
                                label='Head',
                                text='Head Symptoms'
                            ),
                            MessageTemplateAction(
                                label='Neck',
                                text='Neck Symptoms'
                            ),
                            MessageTemplateAction(
                                label='Limbs',
                                text='Symptoms of Limbs'
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
            base_url='https://lh3.googleusercontent.com/d/1ve05vp5guSg1qa-QLTJhZMVkYq7d5Dye=w1600-h1600?authuser=0',
            base_size=BaseSize(height=1040, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='Head Symptoms',
                        area=ImagemapArea(
                            x=0, y=0, width=520, height=320
                        )
                    ),
                    MessageImagemapAction(
                        text='Neck Symptoms',
                        area=ImagemapArea(
                            x=0, y=320, width=520, height=260
                        )
                    ),
                    MessageImagemapAction(
                        text='Symptoms of Limbs',
                        area=ImagemapArea(
                            x=0, y=580, width=520, height=460
                        )
                    ),
                    MessageImagemapAction(
                        text='General Symptoms',
                        area=ImagemapArea(
                            x=520, y=0, width=520, height=320
                        )
                    ),
                    MessageImagemapAction(
                        text='Upper Abdomen Symptoms',
                        area=ImagemapArea(
                            x=520, y=320, width=520, height=320
                        )
                    ),
                    MessageImagemapAction(
                        text='Lower Abdomen Symptoms',
                        area=ImagemapArea(
                            x=520, y=640, width=520, height=400
                        )
                    ),

                ]
            )
            #line_bot_api.push_message(uid, diagnosis_message)
            line_bot_api.push_message(uid, imagemap_message)
                                                
############################### 頭部症狀判斷 #######################################
        elif  user_message.find('Head Symptoms') != -1:
            Symptom.Head(uid) 
            
        elif  user_message == 'H1' :
            s1='H1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))             
            Symptom.Head2(uid)
        
        elif  user_message == 'H2' :
            s1='H2'
            KMSH_UserDB_Con.set_s1(uid, s1)
            H1_sym_message='Your current symptom:\n[H2:Difficulty swallowing and eating]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))            
            Symptom.Head3(uid) 
       
        elif  user_message == 'H3' : 
            s1='H3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H3:Neck deformation / pain / numbnes]。'+ line_mark +'Recommended clinic:[Orthopedics]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))

            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                   
        elif  user_message == 'H4' : 
            s1='H4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H4:Yellow sclera]。'+ line_mark +'Recommended clinic:[Hepatic-biliary-pancreatic Medicine]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號肝膽胰內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                                          
        elif  user_message == 'H5' : 
            s1='H5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H5:Acne / Hair loss / Dark skin]。'+ line_mark +'Recommended clinic:[Dermatology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                     
        elif  user_message == 'H6' : 
            s1='H6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H6:Head impact / back of neck pain]。'+ line_mark +'Recommended clinic:[Neurosurgery]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腦神經外科'
            Rig_Option.Ask(uid,rig_dept) 
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
            
        elif  user_message == 'H7' : 
            s1='H7'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H7:Sore throat or hoarseness / hearing impairment / Neck lump ]。'+ line_mark +'Recommended clinic:[ENT Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                        
        elif  user_message == 'H8' : 
            s1='H8'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H8:Blurred vision / dry eyes / foreign body sensation]。'+ line_mark +'Recommended clinic:[Ophthalmology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號眼科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        

        elif  user_message == 'H9' : 
            s1='H9'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H9:Eye floater/ eye pain / itchy eyes]。'+ line_mark +'Recommended clinic:[Ophthalmology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))  
            rig_dept='掛號眼科'
            Rig_Option.Ask(uid,rig_dept) 
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)              

        elif  user_message == 'H10' : 
            s1='H10'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H10:Teeth sensitivity / Soreness / Bad breath or yellow teeth]。'+ line_mark +'Recommended clinic:[Dentistry Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號牙科一診'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)

        elif  user_message == 'H11' : 
            s1='H11'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H11:Red and swollen gums / large gaps between teeth]。'+ line_mark +'Recommended clinic:[Dentistry Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號牙科一診'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)             
                        
        elif  user_message == 'H12' : 
            s1='H12'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[H12:Oral ulcer/ ulcer]。'+ line_mark +'Recommended clinic:[ENT Dept. / Dentistry Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)            
#--------------------頭部症狀 H1頭痛/頭暈/頭沉重 之 第二種症狀----------------------------------------            
        elif  user_message == 'H13' : 
            s2='H13'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]、\n[H13:High blood pressure / fainting]。'+ line_mark +'Recommended clinic:[Cardiology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                      
                        
        elif  user_message == 'H14' : 
            s2='H14'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]、\n[H14:Fever / rash / general muscle pain / arthralgia]。'+ line_mark +'Recommended clinic:[Infectious Disease]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號感染內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                       
             
        elif  user_message == 'H15' : 
            s2='H15'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]、\n[H15:Tinnitus/nasal discharge/sore throat/hearing impairment]。'+ line_mark +'Recommended clinic:[ENT Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        
 
        elif  user_message == 'H16' : 
            s2='H16'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]、\n[H16:Neck lump / hoarse voice]。'+ line_mark +'Recommended clinic:[ENT Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                       
                        
        elif  user_message == 'H17' : 
            s2='H17'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]、\n[H17:Tinnitus / memory loss / skewed mouth]。'+ line_mark +'Recommended clinic:[Neurology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號神經內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        
             
        elif  user_message == 'H18' : 
            s2='H18'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H1:Headache / dizziness / heavy head]、\n[H18:Insomnia / anxiety / depression / fear / anger]。'+ line_mark +'Recommended clinic:[Psychiatry]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號精神科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                             
#-------------------------頭部症狀 H2吞嚥進食困難 之 第二種症狀---------------------------------------  
        elif  user_message == 'H19' : 
            s2='H19'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H2:Difficulty swallowing and eating]、\n[H19:Epigastric pain / bloating/ vomiting]。'+ line_mark +'Recommended clinic:[Gastroenterology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                      
            
        elif  user_message == 'H20' : 
            s2='H20'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H2:Difficulty swallowing and eating]、\n[H20:Burning chest]。'+ line_mark +'Recommended clinic:[Gastroenterology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)                        
            
        elif  user_message == 'H21' : 
            s2='H21'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[H2:Difficulty swallowing and eating]、\n[H21:Neck pain / numbness / tightness]。'+ line_mark +'Recommended clinic:[Rehabilitation]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號復健科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
                                  
########################## 頸部症狀 ############################################
        elif  user_message.find('Neck Symptoms') != -1:
            Symptom.Neck(uid)
            
        elif  user_message == 'N1' : 
            s1='N1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[N1:Head impact / back of neck pain]。'+ line_mark +'Recommended clinic:[Neurosurgery]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號腦神經外科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
            
        elif  user_message == 'N2' : 
            s1='N2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[N2:Neck deformation / pain / numbness]。'+ line_mark +'Recommended clinic:[Orthopedics]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
            
        elif  user_message == 'N3' : 
            s1='N3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[N3:Neck lump ]。'+ line_mark +'Recommended clinic:[ENT Dept.]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message)) 
            rig_dept='掛號耳鼻喉科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)            
################################# 上腹部症狀 ###################################                  
        elif  user_message.find('Upper Abdomen Symptoms') != -1:
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypAtSd5Q-p65CtrZ8WR78vD1AIchkplM3sHnkUQfkFVjEvKO5WyXifYEpzXfQRDopsP24RaUypw6JjxaKUn7mjN3_kxuBtdTzFH-uxYQDYuhexNfJJN2rlWQiQYm1pIpDTd_4kXQY8pKtBjnS0r0FIGe-LZlVE2yLELXA4Al1_QNjYN81zbKxdrK3B5K9fNX1Y_dlabbQzlCYcDiNCXmLHP5kXODmxs1fOqyDyr8N86n_aknCySTQcedieV-CLEGWqPc5lO9jidUF8gs2vYl4xDEaF0gUHJI4xGlrUvl4shdefYKrJ348un5WeQpnnYnSspPHNAoGy03543_DsULtFdYdCw39wC9-P3h1HufpTOhSCCD2NovvTvPNMK09h6gBxPkPuOcx8Dc23PEdqbA1a7JeWt0Eq6MLqp6omN-ZzNjMWIb8vUp6SGO3NneHDRBiZdFCPXmnirimm2cos03I4tom_TtOPPP21FHXBLdJpTw8BRovHg_Qk-8h6-QCnQedMid0sbCViN8j6oTcrIZFuLfw0mhK5DZf1XhqqckVQut3jpm64KTIDtr-3Rms-Hk9bgsLSMEx03q4_7iGl66YdnkVC9L3n7Rz3LmTsqJLBdcjjwRUFJajm2x-RgOlyMED4oo-mT4-QGQbAZeVOUuk-63DMPCLiBmc-l9NDSz81IQykH3I9qeta-W1osKGdCLlrY1iw3jlHJFbzUdr_S4jDcUk-uL9Ki5aO4KNFS_TRA1bZr-p3yxdBgwk_j93W_xh2xtl1glphyTJneqsvJ51VtxNhdNt94M0HDHkJceWF9qmQ8SY1S-1u-fdb_7k3mwarPVr8M6haUWVgKbLgZfA6veSwMpSKo0X_SqmHlzWaSOJaSjupzJTTgAJEf9ezJPKxoeciKpuZGb4js61rKKis5PRstKsVYvmQRtIl8hIXEzNL73aGimeDKt6G_BXJGM-BmIU42gkVw6CVW_rx15rSvWKI_DOkjpGUHRNDz1n11BlYA_NSluAf41plOZKgqT20FuKoCKjye0wJvsY065Ibt19NjdzHHZw2XV1-Q_mxPu28CkXxsxEpaQM3JSl88l7zYLKbUfy8F-dhz-bWr4U6mLE_KADBx3cDZ9Fzmq8SbIlAPCpU9hp8jgXrjnD06BpjQHjQdp7AirWhwe3gzE9Zd2w5ZkGlGGFNKsPVGV8ZFsSKwMSGUcRX1ShQtfVwzccSHCIv2uacWP11wJnOFyFZ-SD251r_BhPdH2eJz_-l0YpF4ZUq0jvDKXscKiXast2YgUmRrQ_bKGM0rsKDQ-iLqPBbi2QRftQ4nspNboZA=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=700, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='U1',
                        area=ImagemapArea(
                            x=0, y=120, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='U2',
                        area=ImagemapArea(
                            x=0, y=240, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='U3',
                        area=ImagemapArea(
                            x=0, y=510, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='U4',
                        area=ImagemapArea(
                            x=600, y=120, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='U5',
                        area=ImagemapArea(
                            x=600, y=270, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='U6',
                        area=ImagemapArea(
                            x=600, y=510, width=600, height=150
                        )
                    )
                ]
            )
            # line_bot_api.reply_message(event.reply_token,clinic_message)
            line_bot_api.push_message(uid, sym_message)
            return 0
#-----------------------------------------------------------------------------            
        elif  user_message =='U1':
            s1='U1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='Your current symptom:\n[Upper abdominal pain]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypCom08i0PvyT5Cuzf2-SJR6pur29IyY95_8YOc0zE-r6LpHGAUxHinS6uHKVGicuHqVXJM-j1z7kc1zyH1cD6OHKLrV6CZsMM8R9jjL8YDplJ2hSMq1kReAoHFkQOzo0SHxJ8DzHW-2sQOBbXHLINnDfUkB3jZi4lkjQ0YusI_Bo7PL8fc_QlmV0g0RrOn-WNR-U6uML6SmCAQBfqtzTJekSNTjyV4OZyU7SWFE--a2mUcejqtRy-tADOs4f-aveN2Vx5Jg0Fr-wJEZPbWIt8zRJzYX2PzQl4fbMEbLjFOePCMHds_FiQR2vpZml3bT4MxICIi_DTj7kr-PUSgZ9EHa8D-yrNBaG3DrKiXpS0bPJHGRC-Yl75EhJY2ZyOjUQYZ__IwH5a6_jpeh20WYTRq3Wy6ybghV69_yQrxNKLDykmTdUdTeYYBLLWlNQ7sQR7GJqsjULcDL7OOVlWjrP646chLQf4Jxc-d_qCDAyj_VYJ5N4Eo6cQa8YBvtqsClgDny6pVLlasNMTMIWRDnc24ZccR3_Zy9kHLmuM2FBvSyzQskAgsRn-mb4dGDgrZl0CyvABertfmmYfkmW92eb9xMjC8J-NnaUwki5qPVf_xZeWm7SYgU3NJXieb6p8RsJ8J1ZzORyxgQtYJqeKsCxhFqBdCin125QAfX923idB50hlVNVRvEdsyiGNP3WoRd2b3z7revSZ1u08G3VkQoqzaoJKFFmgPxZuDa24aLWu7TxpQX22yJv5FGCV5CJjLR0boHpbBbScZ-aio35FnnPECyu8M30uTQvUPaCzrcV_9FmdTQG5PJPO42b67djluQfUrnlXOULPAU8YEnsdEAA2MlyWCJi_V-CutLul95HH6YSzmPAOO1poTIHhJeYcyO4x-qn3bsBP4-r-uiV8b6HKZhF_LaQYymItf1iqQQ7KI9bktoTV_3dF375N7Gy64aC4DJsfhqJosF6_Br4zLqi5RhZe41tLqDk92bWSL96bCmhAvIpuiu1pIkg2RYT0hijORmmvKkPiWr4FU89yX69JXsFvIOC9B0iQp_5ky2CqV2x9V_P7OdiQT5oZjtoyX2R4aIcs1Q7kvr-OuQkGjzXBljQLRzOEpd6l1NF7VB7-gE9oZpTasiVupBGIXjMuXrVBrY1YjnaKr66Xut8DZO22GOBOunGiIoNGejLp1RcYZ3GvYPaJz2MPl2Bq2w7IWQyC1JU-NRjSjLYP8HrQsDsS8GDgr3-6pXALS5_jTA5s_v0feXkN86axFtiWKHaJIr9R_J_NqxtyB5sAw5cIs9b0Y819etJWCN21f90Zp0LX1vzA=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=700, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='U7',
                        area=ImagemapArea(
                            x=230, y=140, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='U8',
                        area=ImagemapArea(
                            x=230, y=290, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='U9',
                        area=ImagemapArea(
                            x=230, y=500, width=600, height=150
                        )
                    )
                ]
            )
            # line_bot_api.reply_message(event.reply_token,clinic_message)
            line_bot_api.push_message(uid, sym_message)
            return 0
#-----------------------------------------------------------------------------            
        elif  user_message == 'U2':
            s1='U2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='Your current symptom:\n[Chest pain / Chest tightness / Wheezing / Coughing]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypDjDtuvpJBxIRnTUSeGXScQ_WbXkLVYWdzOno-NyhD64BO2a6tL6hjfq2YScFh5YU44nfEHdZiqCcJE3Nx3Rir86pKe5cjwBP8kSA5mR-GmEIPYWaDhGtmC8sI1IraEi4BRtZsRaiZ5AUBS7fJZEkeb7MPqaU9uzcAzVDdhOwSn6HIEpkYQWrPhJuVTA1y6OpksROy6HnUu2eXqvZbose_wLUSSwyg23naSGp6s2iT1fiQ4wGATAAZmaM__GbAJ93oCQ5JIks7ldm5cSsILVCKl8rXvUEhZmmf0yMBL0mO4r4UqlWqpWa9nrhesYMrZUThlSJJxnS5cV9Qo2MquVjXNo-VQId5qqL_ehTAjuKFoktVhLUZ90un4HLQ0KdlJslX7OwcX0NlByBOtEPfTFGGWeecXGC3UFSTQbJmWlZg005yps1Mpe3UxwLvsynkG7wCjpfW56TDUcCOYj1AhWtMak7d6HgfE6R4DSK1DylkVV6CDdjKrJ3m4Y0GhxPF0upotiooHtqoo-y4WStn6H8JlvJqY3JRg5TTWiRLlEWNw2oGnWKu8aCCy5RyobYBtbJgAnepN1iAKS0lUoe1SMQGhgp_YQpj-gBOFwZ1dfrjzVDH12JddjcwK6CAjLoDKCJ4yNjF3Q1OD6TsmdD8Ht6iwTV9bPqVvvxMPE5LmnQa4QxT_FriFrk2y2TZUmZio8u03kG4G_g4UTE72J5UsIxvHS0bEEiJ4JsunncdItutyjiOq-VimfoqZyQ1_SspwfWfeYOXBW1AI2GXV7UHEbhpogwc1t5oyBOqp4bJgW7dRhOa56a2geeTbJIuVSikmpLwKCdd2e3b10g1cFCzhYu5iDXgACMJ7swEfHQr1QJ_7RKlZctMwEwI1fr7YX0IwsuSRT6GSaPYi3AyrFgWGeNM957GILaetZJX377vKtivx0gvdmb3ne03WE2ZAEixNA1KZLsv-z8jett8fUHebet5H-P5SZQER8-4qm-HvZ_06QeOEqYONE3NRTKXZGD8sopn1mcEJJqYVXYM44STLs2jQF5iHgd1KSK8h2INYd-yqyMN2OlMF4FpYHWOItO-meXhrEkPu-7_b20jYw2JCDm3FoiL5Y1ydyAc1lujhEDaGODTFiIRrEQ7VjNPXhhOJKIuyYkApDFrw_-hDBafglplBCIz7T06BGcuRxx2yTKCmPmthcSJMCExnZVN9dKpSRV4yszPd1MNXP1E9krv8Uq3EG17lGeX62aiab6vqYQSBrW5uEP1rf4qg8m3sCxECPuTeDtZ__5C3pGKmL7JWmOnXg1fYun9nhAhGcBwfsQ=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=700, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='U10',
                        area=ImagemapArea(
                            x=230, y=160, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='U11',
                        area=ImagemapArea(
                            x=230, y=400, width=600, height=150
                        )
                    )
                ]
            )
            # line_bot_api.reply_message(event.reply_token,clinic_message)
            line_bot_api.push_message(uid, sym_message)
            return 0
#----------------------------------------------------------------------------            
        elif  user_message.find('U3') != -1:
            s1='U3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[U3:Poor mobility / shrinking of body parts]。'+ line_mark +'Recommended clinic:[Orthopedics]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U4') != -1:
            s1='U4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[U4:Deformation / Pain / Weakness of body]。'+ line_mark +'Recommended clinic:[Orthopedics]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科A'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U5') != -1:
            s1='U5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[U5:Palpitations / Shaking hands / Bulging eyes / Thirst / Eating more]。'+ line_mark +'Recommended clinic:[Endocrinology and Metabolism]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號內分泌科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)  
        elif  user_message.find('U6') != -1:
            s1='U6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[U6:Neck deformity / Pain / Numbness]。'+ line_mark +'Recommended clinic:[Orthopedics]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科A'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U7') != -1:
            s2='U7'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[U1:Upper abdominal pain]、\n[U7:Jaundice]。'+ line_mark +'Recommended clinic:[Hepatic-biliary-pancreatic Medicine]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號肝膽胰內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)    
        elif  user_message.find('U8') != -1:
            s2='U8'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[U1:Upper abdominal pain]、\n[U8:Lower abdominal pain / diarrhea / constipation / vomiting]。'+ line_mark +'Recommended clinic:[Gastroenterology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)    
        elif  user_message.find('U9') != -1:
            s2='U9'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[U1:Upper abdominal pain]、\n[U9:Abdominal distension / chest burning sensation / black stool or bloody stool]。'+ line_mark +'Recommended clinic:[Gastroenterology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message.find('U10') != -1:
            s2='U10'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[U2:Chest pain / Chest tightness / Wheezing / Coughing]、\n[U10:Fever / cough with sputum]。'+ line_mark +'Recommended clinic:[Pulmonary Medicine]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胸腔內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message.find('U11') != -1:
            s2='U11'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[U2:Chest pain / chest tightness / wheezing / coughing]、\n[U11:High blood pressure / fainting / palpitations]。'+ line_mark +'Recommended clinic:[Cardiology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)               
############################### 下腹部症狀 ###################################
        elif  user_message.find('Lower Abdomen Symptoms') != -1:
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypBHEs0ZExTi7P8KpVmk4MqLoO9AkL6ffqgwUAlNqZHLVccb-X1fD5Q_tAbXArBpwKQ4Uep91E9GQS8GkaUOMJ8HIvbhJRWIbm7Foa8SYgQPOHbq3kPqPJfGdUAwF_JFQR8lv5AmUk8uPTBJ01yo9Gxx10q5dTBPlX9jas7YHdpmh6g9k6L8QQ4t7BikjxHQUVmAKZm0mN13Q6vH4_POrsxnv8EqxSig2W9Gb62gHybtSKLXFae-L_yPIceH4Gaa7tkzPQ3QGVOz3w6uezeEJSSocgMDKXh6U80K8CAnVkFiVFA8-D939cl4X_e44-Q9fLk_74qdj6z7IZ3xLzq9aXIMOeJ62ugtBqnJ6cl83zrDcY7Vyj0Bf7-hueISOQhQcyVr7VZUfQ1W1XTOF-UiY3xzlQmGrsXg7oKQPh3Tagfs1Hs_ThDUmMlBE_stLz1ff968MT0s4EkWQwWRUfaZIn4zYiex7Ljmf5LjxV0iZro-O1I5-ISPpqasXduAd5vtKEm5OKMcIG7D8ERfO9lPlQCgDNZKpCC8SU8RCQQBZE98ASKJV7Ibly_nfi9mV64w3i7VEyF-jLJycL3gADRQtQ0mBP4tvCskqXLYg5spHJ-wm9Y_aUrRyDykY7cpWl5PCCj2cxTVQo9u3AR11v3duSXu0S1tsc_4Slg6pyvIYuLTqbB3Zh8D_n-iX0o2bXk31dKNPM5PtzJeNvHFFOvx2MPmjdLSHfKsiPfnHdtNtghhBmlfl5FhG_Pb_b6NnuTimA-dwbthHoAZ93iCTSb61hLG3rZXwB0jAB1Zyd4zaJ6gT3g9OvU4yuFzc4edVhoxpFx0gX3zmeY9zkDps09pqKGs712R7Xpxh7hAwb1jOY8czMk7UAQIZC8WohiZV0ypN5kmLQ2r2qgPyryBRF86ZCJb4EESZLBaOfdX91XvjPYa7zM184AtawaXu9yFALDo-2W1dnAuYM2rHIbqgWqVxBwDQacHZuy594ZOhNbHnWt_L0jXnsulsOHv-8TGqBQenkrkPE_-lRfq7ZGy6-7NBe5bmol3dxwOIV3wnPfZh5w70-i1c0s5KBeyXBhu-Epj9zemjbyWqD3GQmz3G-5-9fqPUKDcJ3QTQRCuB_isoJZwPaRAv_vTtOe-r28Xts8xJamklX5OHwcmjv5o4VC7VGnXW9WYWKBdEKxjdWJ1KBZESJftLv06NhgtNPMg4oy_66dIFQcODSqsD4Box0ou-lcCrscEHmMPyhw4YdzA4CUExwis51ndFPV7LGgN3WKM4ss97FnDJg3qnLTh2zzDFZfB5WojeeBeVypUfOKTgA=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=700, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='L1',
                        area=ImagemapArea(
                            x=0, y=120, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='L2',
                        area=ImagemapArea(
                            x=0, y=270, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='L3',
                        area=ImagemapArea(
                            x=0, y=420, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='L4',
                        area=ImagemapArea(
                            x=600, y=120, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='L5',
                        area=ImagemapArea(
                            x=600, y=270, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='L6',
                        area=ImagemapArea(
                            x=600, y=420, width=600, height=150
                        )
                    )
                ]
            )
            # line_bot_api.reply_message(event.reply_token,clinic_message)
            line_bot_api.push_message(uid, sym_message)
            return 0
#----------------------------------------------------------------------------            
        elif  user_message =='L1':
            s1='L1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[L1:Lower abdominal pain / Diarrhea / Constipation ]。'+ line_mark +'Recommended clinic:[Gastroenterology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胃腸內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L2':
            s1='L2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[L2:Bubble in urine / Decreased urine output]。'+ line_mark +'Recommended clinic:[Nephrology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腎臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L3':
            s1='L3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[L3:Vaginal itch / Excessive vaginal discharge / Vaginal bleeding]。'+ line_mark +'Recommended clinic:[Obstetrics and Gynecology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號婦產科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L4':
            s1='L4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[L4:Lower back pain / Hematuria / Frequent urination / Painful urination]。'+ line_mark +'Recommended clinic:[Urology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號泌尿科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='L5':
            s1='L5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[L5:Reduced mobility / Atrophy and deformation / Pain and weakness]。'+ line_mark +'Recommended clinic:[Orthopedics]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號骨科A'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='L6':
            s1='L6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[L6:Lower abdomen numbness / Weakness / Tightness]。'+ line_mark +'Recommended clinic:[Rehabilitation]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號復健科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)              

############################### 四肢症狀 ###################################
        elif  user_message.find('Symptoms of Limbs') != -1:
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypCl5DJytBeGDjCFkJQfzcSP-msb5Rhp5Aoqpyc46yzrVJZnka9asEhwl5rYrjhFOBr68qN7jUr36jB4UNB8Bm0y7iJ9o010qhFZRUImvmHFPgAND7ZpKFioMVtNYGn9tiJpPBVx29GpvTfd3DnI6D-eQ42I5svGnZIGYTRJ_NAxhtZyJVQ3IeqVlIC-5ELYXpnlgCKsYKAe86tW0Kx4RzGHkG3hQ85vqbOoORg9Aet5Y4dJQnU8nZ9yGW0MLZb5i_g5rhtmCYLR89zO2E4bZMaCMLmNJ9LpcXy5vODjlE5oqeo56drKoNeq9YWa6k-wnXb7sDCxdcaKqpetby-zGSlXYrCV6Nzc7OL8JAsqkzeXxr9kEyhH_XiD5CNGASFbY5DwLDnriLwavLFFzrBWJl4YksimsgKwqzfg1Ts65h3bKcEmyZZkPI9VYd3VMAvidtKp8PPit0qTQ5FmxfAdnVIg8rH5bnzzY37kjigcv0aUl2LKQcp3A2k6Y1v5oTDmeMGnUO6sohvWEAkO9dfu3j22kqFS7gkpestX4-6tvkn457y7-52ei26Q8VDPjrwYA1mS0l2_iseOFx5FTbcRvjvBXYC5ICCi8urRjSe7Wbnda2Nsq1TL9WUqdxzJdPQFyvJyjN-HthYyyZ0sGZSzjhB9YHpp8CfJKw43nf9Yfp7iI0M3wXvQyVKV7oZOuKFGI1KgmfPlTuTiXY2aA33QFLtBhtaE_F55xrmxH0xijq3jytaBx6XzXLRvcmDPSc6GYB-AxgkJCJqzblKEAOPQIicn7nAC8y32OgqvpxElrzvbv70Cwa6hz5QMOu-MEwBfHM6ZjDT5ZRx1FAVG_YrKFGyfvQIDmiSp5Ob31iyevyopz6o2Xht3mWW0_DY54V1LGQhJK19tHNGZmitR-2LJddB7iwjZV7SyX_8PzlftCL-yrneD6lnSFGzxwIijq-WtZMYrEe3_mXvGo1bFy_Zdj2bneXiBQ6h71IK818845aICogw2yVnEqiEW6ZYjBsWMZ9XyWZ7oIZkqylW7BjptiU2GMtiaRCh5zJ2AztWVcosdT_JtSVQ8Sy1k-b_oZyTvbSGPKEa-HpI37bt93vTqrJE0A2PwVxIXbB9G86TH7yUtBi0jqNFANKLjdSdjZC-d4JNgClZ2aeLWhrcJ3aKawGgMq9LgSMgF84pfvIFnWIhbJuKZdTnhmoNfEkUqe9mw5Ltp6wMJyyEbbtU-11jdlpF7GoDKQ61hnsbkNjAsT0Fk5dl76UC_2x35_jp-07x6dzY1-I8RLxxtDM1c1ldgl6llQPVUNTUOeerePU-BVA=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=700, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='LB1',
                        area=ImagemapArea(
                            x=230, y=140, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='LB2',
                        area=ImagemapArea(
                            x=230, y=260, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='LB3',
                        area=ImagemapArea(
                            x=230, y=410, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='LB4',
                        area=ImagemapArea(
                            x=230, y=560, width=600, height=120
                        )
                    )
                ]
            )
            line_bot_api.push_message(uid, sym_message)
            return 0
   #--------------------------------------------------------------------------         
        elif  user_message=='LB1':
            s1='LB1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='Your current symptom:\n[LB1:Calf edema / Foot swelling]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))
#----------------------------------------------------------------------------            
        elif  user_message =='LB2':
            s1='LB2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[LB2:Difficulty walking / Numbness / Ache]。'+ line_mark +'Recommended clinic:[Neurology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號神經內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='LB3':
            s1='LB3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[LB3:Sore and numb limbs / Limb weakness / Tightness ]。'+ line_mark +'Recommended clinic:[Neurology / Rehabilitation]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            #rig_dept='掛號復健科'
            #Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='LB4':
            s1='LB4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[LB4:Problems with nails]。'+ line_mark +'Recommended clinic:[Dermatology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)              
        elif  user_message =='LB5':
            s2='LB5'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[LB1:Calf edema / Foot swelling]、\n[LB5:High blood pressure / Fainting]。'+ line_mark +'Recommended clinic:[Cardiology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)   
        elif  user_message =='LB6':
            s2='LB6'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[LB1:Calf edema / Foot swelling]、\n[LB6:Palpitations chest pain / Chest tightness / Wheezing / Coughing]。'+ line_mark +'Recommended clinic:[Cardiology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='LB7':
            s2='LB7'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[LB1:Calf edema / Foot swelling]、\n[LB7:Whole body edema / Bubbles in urine / Decreased urine output]。'+ line_mark +'Recommended clinic:[Nephrology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腎臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)               
##############################################################################
        elif  user_message.find('General Symptoms') != -1:
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypCl4d2VvGBRdUo2NZrQD-7RuWjAb-EvLPiCdzdQTtav04uogvAD7sNvNcSoh3wXbRDDP-MZIbq_2_G1rufCz1CkiKHF_oYeXJ8a96K6AzSE4_MLalTvItiOofiW-Snz1qfrO3HhFDVEiN7XQZpDy0UJpIs2ISGu67P4wRPvhGeXTaPQZSKpafau3SELw1QJTsrmMyEw66NRJoVeU8owucFoATMLfqGVRQbbc7oF3_QpxfcIGOrmkwzSkUwgXUn-4XXtMWXlsheR8iyTCxE3a5UY3vG-jmWDVU-vzUR5FPetNMIOvY8euJKVHssuALukb6tZF-GKCoxkjuwxnJ4MzlXURLk6CSwEs1XcxBg4Oh141m6ZHFF7a_JJXqkSDAbe9sSA2NC6j3lvMh_2giRvRLyJ3r860_yfnOJQXqZhnlD72tSYZ3sxxzWIK_JvI_Oz_HEG-Ei28nP6X0ARjtDAuTS4GQJ_qagI6n3apJRAiQJ5aAh0eLTDwugJjq-OVA7J18X95TRdxfoYPdMOhVZelaRPexJrtizzSYfn82arq3KmGVefIH5ZazfBqw7chW-P2hRpUfSMP1X1ybt-Ec8P2Qt5VCTQQ75fonYWcSUekzDRHvAAIgKXQeBnKQEUvvqu3YPOhH72z2sxi0N3h2TkVM3Wy4DEkQxQAvF9SD1R1qlrrUumM871LN_VA1Z9mj5hsjqSfMd1iO9wBhB8yiMHwN5bxKzx5IpiZ4b7ZRO1VN-KgR6MuqmjFsmUZJ7JzBVUfjEXhUmrOlIwvgeri7vcfcWxKqLqDEGkujMrw3OAU9_1F0uizL0oJVu6jae8qqqgqOA-jcRqzxdUPBz1IDytn9pbUq1yEw8Ntv7Hknw3lskPle5b3LItbVK4BJLfNOSOwXpto90l13U7Onc5yOpKYwsOpDc9XcMAWGt4HKDLZaRGgbqzoyAktqBnjYyfhco86TDLpIsPS3bMEJunbmebZFwSIt50gIqvv4TO9YXtLkHE7ySwVxcbnaMquV38E4JaIhSx-f2Ws3dcHPq0PRwW0KbxLTfjf9W2Pgvy5JEDbcjq82mkTqCzODoQwrdyVZCkrl0GuykSeOvpcp90vWkr8hY1kMlc6wcC33x5f-tBAth4HgocGpjg-A2MRgdVut7Di8tckfye1dOc6kc9-NYTC7XXoOLD6tKVdswKlCFCiPiFuBoOjy5DPcU-LjTSZttx-oR_qAniktjuDh8R30onbqs70Ho_x73PL6uZsdMPOFsYDfXnNXweXB2cTfM1bP4MBgHdCLeCHKHTvEWF5YR2pJBQwtyxVPT1ZuMzfX_aKQ=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=1040, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='A1',
                        area=ImagemapArea(
                            x=0, y=120, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='A2',
                        area=ImagemapArea(
                            x=0, y=240, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='A3',
                        area=ImagemapArea(
                            x=0, y=390, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='A4',
                        area=ImagemapArea(
                            x=0, y=540, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='A5',
                        area=ImagemapArea(
                            x=0, y=660, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='A6',
                        area=ImagemapArea(
                            x=0, y=810, width=600, height=120
                        )
                    ), MessageImagemapAction(
                        text='A7',
                        area=ImagemapArea(
                            x=600, y=120, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='A8',
                        area=ImagemapArea(
                            x=600, y=240, width=600, height=120
                        )
                    ),
                    MessageImagemapAction(
                        text='A9',
                        area=ImagemapArea(
                            x=600, y=360, width=600, height=150
                        )
                    )
                ]
            )
            # line_bot_api.reply_message(event.reply_token,clinic_message)
            line_bot_api.push_message(uid, sym_message)
            return 0
#-----------------------------------------------------------------------------            
        elif  user_message=='A1':
            s1='A1'
            KMSH_UserDB_Con.set_s1(uid,s1)
            responese_info='Your current symptom:\n[fever]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(responese_info))
            sym_message = ImagemapSendMessage(
                base_url='https://lh3.googleusercontent.com/fife/AAbDypBLsRsEPctv5c9_LHUnBmaAf0RrosstKDScXtp5hKZWHpoyCRbTJ3dwmuM8ZfW0XYMEqf66ZI8i-6HNlXzK2JmaMWb1JTBBQVHz5tv2zciefJlHxmHtj_mCMLdfNkN7Bl5Ta3SdcZW_rHi5shmxpe8osKtnq4WmDILDO0sfiL7FVdWhg9zf_3-IAwgLATUwsfvM5uEHImG3L7SPGwlj5sqJ-7DNtoizrPA4_BY7GFAjH9rtx1xKo4kQUpmw9XoL0Xn7fwh6dawelH1h2Evv4G03TwCX4DgXTXyw-lzLy4FAbiLp1tpJLKuQjnI76EFicsvSOyRRtts5AswwM03hklTcH-1r33mKgMaTUZ7iResCj2rQVrvTN79CNVXnfBw1_GFgG18ltc31hiO_t217rM8K2rYVyTuSYcLBVuskBYhum9D-cC9uCPqncNYkC_MH4F7lsYwwFErRdkYS9z76PbeTHkfuq8DmRf9UG221ev43_UtyIMJesKbAZlcmg7ZVKSCP4P1ECLbHhbP3LOJ9_OIjD2DTH3mzub_taDcM22ajiw_2gSHjEkqM1Z8QJOuCEe6LsEtemYBvYM58f4qv0IizmN4t63ynuHsPF3JmKDpNFBhu0FnlAfpgK6YZ0Cs1ft3CimlFIQjickCwyOIn3ZtPyTrhV39F2WGtWltEoLnoHDIKg1Np6L_aG7jlpVMsTCqUG6yDpV1avlmwqDa0Xio97dnLSBLnqD2_6j-WCik0d1fLdcAd-RwZ_A5_1bqN3pKIu_O8EFAOcNyk1h72vaLguypcO8utmMN6TvSUZJZBFRw22ahEsrhlN8gEQQD3aBC57BAUciOViHyYUue7roqrmCvKXifgmV1oBByqXzr_gjmoGuPHGxqybYQ6vZgiL_SarOH8gI4whAu29luXfNHPS14xTc9uA_noBd7sU53Vg2z0jlVkjpKO1SKdcV4v1b9iz8RwJJJ1mAFWTHKXit3zUIRVlb1gZGNO7UBdmOcA6_XJPwjwg8RLsfE-21cakXfE6i9JtJVcHH4MLfJntELokOr_KDtaJNkRGvWIMRYRlhWwYV4XsF2C0qcEuC2PMxCCNyYSEGzE-QWwCT94cL88ChDA1HROPkvdM0bmao-mor6xPS6wZg-K8Z_pii2F52lu0yWpQT_WoY5fg9mkfufNeGA9yMERybIp_Au78Q7BtSml68OVqvSCjjQ61mNkojbdbAg1xVvm9WU_ftTckbQontswwP65jLubN_fg9zjeFGY1IqkBXWO5z_Pxusm2vGqMGXOg2a0HmN_iMAmYQOg-4frOQDHMHXBmf8BbBw=w1600-h1600?authuser=0',
                alt_text='imagemap',
                base_size=BaseSize(height=700, width=1200),
                actions=[
                    MessageImagemapAction(
                        text='A10',
                        area=ImagemapArea(
                            x=230, y=140, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='A11',
                        area=ImagemapArea(
                            x=230, y=290, width=600, height=150
                        )
                    ),
                    MessageImagemapAction(
                        text='A12',
                        area=ImagemapArea(
                            x=230, y=500, width=600, height=150
                        )
                    )
                ]
            )
            # line_bot_api.reply_message(event.reply_token,clinic_message)
            line_bot_api.push_message(uid, sym_message)
            return 0
#-----------------------------------------------------------------------------            
        elif  user_message =='A2':
            s1='A2'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A2:Whole body edema / Bubbles in urine / Decreased urine output]。'+ line_mark +'Recommended clinic:[Nephrology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號腎臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A3':
            s1='A3'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A3:Easy to get nervous / Excessive sweating / Insomnia]。'+ line_mark +'Recommended clinic:[Endocrinology and Metabolism]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號內分泌科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A4':
            s1='A4'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A4:Insomnia / anxiety / depression / fear / anger]。'+ line_mark +'Recommended clinic:[Psychiatry]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號精神科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)  
        elif  user_message =='A5':
            s1='A5'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A5:Acne / Dark Spots / Immune System Disorders]。'+ line_mark +'Recommended clinic:[Dermatology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A6':
            s1='A6'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A6:Skin wound / itch / redness / tightness]。'+ line_mark +'Recommended clinic:[Dermatology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號皮膚科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A7':
            s1='A7'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A7:High blood pressure / Fainting]。'+ line_mark +'Recommended clinic:[Cardiology]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號心臟內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A8':
            s1='A8'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A8:Jaundice]。'+ line_mark +'Recommended clinic:[Hepatic-biliary-pancreatic Medicine]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號肝膽胰內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A9':
            s1='A9'
            KMSH_UserDB_Con.set_s1(uid,s1)
            H1_sym_message='Your current symptom:\n[A9:Body aches and numbness/ weakness / tightness]。'+ line_mark +'Recommended clinic:[Rehabilitation]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號復健科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能) 
        elif  user_message =='A10':
            s2='A10'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[A1:fever]、\n[A10:Chest pain / wheezing / coughing with sputum]。'+ line_mark +'Recommended clinic:[Pulmonary Medicine]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胸腔內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A11':
            s2='A11'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[A1:fever]、\n[A11:Headache / rash / muscle aches / arthralgia]。'+ line_mark +'Recommended clinic:[Infectious Disease]'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(H1_sym_message))
            rig_dept='掛號胸腔內科'
            Rig_Option.Ask(uid,rig_dept)
            lang ='中'
            KMSH_UserDB_Con.dis_trmode(uid,lang)  #取消看診模式，回到一般查詢模式(門診掛號功能)
        elif  user_message =='A12':
            s2='A12'
            KMSH_UserDB_Con.set_s2(uid,s2)
            H1_sym_message='Your current symptom:\n[A1:fever]、\n[A12:Dizziness / tinnitus / running nose / sore throat]。'+ line_mark +'Recommended clinic:[ENT Dept.]'
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
            Response_info='Unable to understand the symptoms you selected, you are currently in the [Medical Department Recommendation] function! Continue to use or leave this function?'
            line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
            Confirm_Dig.Ask(uid)
                    
        return 0

############################# 導航附近醫院模式 #############################
    if work_mode[0] == 'M':
        # -----------------------# 取消導航功能-----------------------
        if user_message.find('Leave Search') != -1 or user_message.find('取消搜尋') != -1 or user_message.find('Quit') != -1 or user_message.find('quit') != -1:
            lang = '中'
            KMSH_UserDB_Con.dis_trmode(uid, lang)
            Response_info = 'OK! Cancel [Hospital Search] function. You can use other functions!'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))
        # user_message='我要翻譯韓語' user_message='我要波斯語翻譯'    #user_message='翻譯馬來西亞語' user_message='翻譯羅馬尼亞語'
        # ----------------------變更翻譯語言種類--------------------------
        elif user_message.find("Hospital Search") != -1:
            Response_info = Quick_text()
            line_bot_api.reply_message(event.reply_token, Response_info)

        elif user_message.find('My Hospital') != -1:
            my_Hospital = KMSH_UserDB_Con.read_my_Hospital(uid)
            Response_info = reply_Hospital(my_Hospital)
            line_bot_api.reply_message(event.reply_token, Response_info)

        elif user_message.find('07') != -1:
            Response_info = 'Please click the number to dial'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))

        else:
            Response_info = 'You are currently in the [Hospital Search] function! Continue to use or exit this function?'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))
            Confirm_Dig.Sit(uid)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))

#################################### 一般查詢狀態 ##############################
##     user_message='離開看診'    
    elif user_message.find('Leave the Medical Department') !=-1:
        
        Response_info='You have left the function of [diagnosis advice]! You can use other functions!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))
    elif user_message.find('Cancel a visit') !=-1:
        
        Response_info='You have left the function of [diagnosis advice]! You can use other functions!'
        line_bot_api.reply_message(event.reply_token,TextSendMessage(Response_info))    
    # test template

    elif user_message.find('Medical Department Recommendation') !=-1:
        lang ='中'
        KMSH_UserDB_Con.set_trmode_d(uid,lang)
        
        Response_info='You have entered the function of [Consultation Suggestion]!\nTo leave this function, please enter the text command of [Leave Consultation Advice] or [Cancel Consultation Advice]!'
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
                                label='Head',
                                text='Head Symptoms'
                            ),
                            MessageTemplateAction(
                                label='Neck',
                                text='Neck Symptoms'
                            ),
                            MessageTemplateAction(
                                label='Limbs',
                                text='Symptoms of Limbs'
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
            base_url='https://lh3.googleusercontent.com/d/1ve05`vp5guSg1qa-QLTJhZMVkYq7d5Dye=w1600-h1600?authuser=0',
            alt_text='imagemap',
            base_size=BaseSize(height=1040, width=1200),
            actions=[
                MessageImagemapAction(
                    text='Head Symptoms',
                    area=ImagemapArea(
                        x=0, y=0, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='Neck Symptoms',
                    area=ImagemapArea(
                        x=0, y=320, width=520, height=260
                    )
                ),
                MessageImagemapAction(
                    text='Symptoms of Limbs',
                    area=ImagemapArea(
                        x=0, y=580, width=520, height=460
                    )
                ),
                MessageImagemapAction(
                    text='General Symptoms',
                    area=ImagemapArea(
                        x=520, y=0, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='Upper Abdomen Symptoms',
                    area=ImagemapArea(
                        x=520, y=320, width=520, height=320
                    )
                ),
                MessageImagemapAction(
                    text='Lower Abdomen Symptoms',
                    area=ImagemapArea(
                        x=520, y=640, width=520, height=400
                    )
                ),

            ]
        )
        # line_bot_api.push_message(uid, diagnosis_message)
        line_bot_api.push_message(uid, imagemap_message)
        return 0
        #line_bot_api.push_message(uid, diagnosis_message)
        line_bot_api.push_message(uid, imagemap_message)                                        
        return 0
###################################################################################    
  # user_message='我要翻譯韓語' user_message='我要馬來西亞語翻譯'    #user_message='翻譯亞語'       
    elif user_message.find('外語選單') != -1:
#         lang_menu = TemplateSendMessage(
#             alt_text='Foreign language translation menu',
#             template=CarouselTemplate(
#                 columns=[
#                     CarouselColumn(
# #                        thumbnail_image_url='  ',
#                         title='Foreign language translation menu-1/4',
#                         text='Asian language translation',
#                         actions=[
#                             MessageTemplateAction(
#                                 label='English',
#                                 text='翻譯英語'
#                             ),
#                             MessageTemplateAction(
#                                 label='Japanese',
#                                 text='翻譯Japanese'
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
#                         title='Foreign language translation menu-2/4',
#                         text='European language translation',
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
#                         title='Foreign language translation menu-3/4',
#                         text='Asian language translation',
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
#                         title='Foreign language translation menu-4/4',
#                         text='Asian language translation',
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
            alt_text='Foreign language translation menu',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/FtA-p01ZiAP1eA-8WOTFAlU793Q4smX7OgGxjD0svgWKR-3nmiIwADfRqSezAQSPlaHOHP0FHayqz2Hu2i1zlazGeC0GuPgqwq_-IZhb7pNRgv8Nk-ePBe7GSTdPcr-zsS9mHaG6NQ=w600',
                        title='Foreign language translation menu-1/10',
                        text='Asian language translation(1/4)',
                        actions=[
                            MessageTemplateAction(
                                label='English',
                                text='翻譯英語'
                            ),
                            MessageTemplateAction(
                                label='Japanese',
                                text='翻譯日語'
                            ),
                            MessageTemplateAction(
                                label='Korean',
                                text='翻譯韓語'
                            )                            
                        ]
                    ),                        
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/FKSRSGWwJttJXxWqGVQh1NK_B6Y0coj7zjIsfBw2zCLOXqyCoJdEc3p1QfrslhUH_vLJAch9duWwh_4qSJ2rQzYzMXVGqIp9RKmfdUVLTtNhhKwAtBDUw_m6hJthgssXy8mqYY9BvQ=w600',
                        title='Foreign language translation menu-2/10',
                        text='Asian language translation(2/4)',
                        actions=[
                            MessageTemplateAction(
                                label='Vietnamese',
                                text='翻譯越南語'
                            ),
                            MessageTemplateAction(
                                label='Malaysian',
                                text='翻譯馬來西亞語'
                            ),
                            MessageTemplateAction(
                                label='Indonesian',
                                text='翻譯印尼語'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/ii9yNKlFFIHKc8JS3Lp0xJJbbFVZxF-IIXAo9UgaUXBMzgmu2eR57Q8yfroKg084mRd-ooBLjvxwBeZRVdYRIDNqm6gW2bDOyUFVT6zD9h4GOu0lMjux1QfeGiUblBNs1Lahwffjjw=w6000',
                        title='Foreign language translation menu-3/10',
                        text='Asian language translation(3/4)',
                        actions=[
                            MessageTemplateAction(
                                label='Thai',
                                text='翻譯泰語'
                            ),
                            MessageTemplateAction(
                                label='Hindi',
                                text='翻譯印度語'
                            ),
                            MessageTemplateAction(
                                label='Arab',
                                text='翻譯阿拉伯語'
                            )                            
                        ]
                    ),
# -----------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/Dg7oaQ7DqWg9VKjb0jlIJIoEeWXsxMnj5LBUU_Go3kyf2M64LYYjtKW03hTiibqyvhX-GO-ApNWR0M_4htARzptPyNBKvreuxwaP_4yt2xsc_-jD7mbd-J_vXBDjxDV4leZLMuujeQ=w600',
                        title='Foreign language translation menu-4/10',
                        text='Asian language translation(4/4)',
                        actions=[
                            MessageTemplateAction(
                                label='Hebrew (Israel)',
                                text='翻譯希伯來語'
                            ),
                            MessageTemplateAction(
                                label='Turkish',
                                text='翻譯土耳其語'
                            ),
                            MessageTemplateAction(
                                label='Bulgarian',
                                text='翻譯保加利亞'
                            )                            
                        ]
                    ), 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/lYYC3KONJ-r8MPuO6NlR92JQocBqioz6d4L_IJMfcWVuZ54IT4jnOGrRB4Nbfm-B-eolh5ijP7tuJCIdPprH3VGf_6zcuDyWrWJGqS5maLxdyyRLaOy3TcKoOlDc3mSE3g599ANr2Q=w600',
                        title='Foreign language translation menu-5/10',
                        text='European language translation(1/6)',
                        actions=[
                            MessageTemplateAction(
                                label='English',
                                text='翻譯英語'
                            ),
                            MessageTemplateAction(
                                label='French',
                                text='翻譯法語'
                            ),
                            MessageTemplateAction(
                                label='German',
                                text='翻譯德語'
                            )                            
                        ]
                    ),
#-----------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/EboLBmHXVpQlk3hrpdHZlLEzjnGGAvjuCGsI32si5ekjX-t6CcUWe6AX1o0lElKvj4pfKLINxMKDzaWFFjliDHMzgTk35M1ShkRlT0S8CrUctVVAHC51Y0zFgVlmRMcdp_U4lC8kgw=w600',
                        title='Foreign language translation menu-6/10',
                        text='European language translation(2/6)',
                        actions=[
                            MessageTemplateAction(
                                label='Spanish',
                                text='翻譯西班牙語'
                            ),
                            MessageTemplateAction(
                                label='Portuguese',
                                text='翻譯葡萄牙語'
                            ),
                            MessageTemplateAction(
                                label='Brazilian',
                                text='翻譯巴西語'
                            )                            
                        ]
                    ),                                          
#------------------------------------------------------------------------------
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/_rparADUnbJJnpb65H7ayhR1AGVm3NWNbDBZiyjnnzxZP6kgvWe4Umhbom9n4ux9IqLJw4f11FTNuSqiWEtGgUvCpPKztQPqWHVPdRJw3QuLfT7eDEo6oFNZCRES9HCeVESSGC3Dpw=w600',
                        title='Foreign language translation menu-7/10',
                        text='European language translation(3/6)',
                        actions=[
                            MessageTemplateAction(
                                label='Italian',
                                text='翻譯義大利語'
                            ),
                            MessageTemplateAction(
                                label='Greek',
                                text='翻譯希臘語'
                            ),
                            MessageTemplateAction(
                                label='Hungarian',
                                text='翻譯匈牙利語'
                            )                            
                        ]
                    ),                        
 
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/5ihsLofivptsynCymdVOH4mVJSU_BVkkCV3G9FuDVRbB-94f11bxTYiWJ9FinDcFkuHZbfgaPbdDEwaprd9eLsoZWV6i6er0zklomk035VXUwke0mCjtK2Ljm6pBd_1YRx3vkvvQ_A=w600',
                        title='Foreign language translation menu-8/10',
                        text='European language translation(4/6)',
                        actions=[
                            MessageTemplateAction(
                                label='Polish',
                                text='翻譯波蘭語'
                            ),
                            MessageTemplateAction(
                                label='Danish',
                                text='翻譯丹麥語'
                            ),
                            MessageTemplateAction(
                                label='Dutch',
                                text='翻譯荷蘭語'
                            )                            
                        ]
                    ),
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/-2lYj7IxjNABSjyP-YhmFakXpuWuI-1sxc6Bms2vH2qHXcLs6nM_OTW9caDURCwcteDgP72jn-naFj074hyP5GvLXWXRekkPwAZDfIaNyP76QjOz7a96i90WrZy93BExUFEOOQxjgA=w600',
                        title='Foreign language translation menu-9/10',
                        text='European language translation(5/6)',
                        actions=[
                            MessageTemplateAction(
                                label='Swedish',
                                text='翻譯瑞典語'
                            ),
                            MessageTemplateAction(
                                label='Finnish',
                                text='翻譯芬蘭語'
                            ),
                            MessageTemplateAction(
                                label='Norwegian',
                                text='翻譯挪威語'
                            )                            
                        ]
                    ),                    
#------------------------------------------------------------------------------                    
                    CarouselColumn(
                        thumbnail_image_url='https://lh3.googleusercontent.com/ixYCUmAcRByFRZtPSmljEScE3rFss1BqiflLUUX4UHqHwOTlIuzREIG3WzH2D-ltmWgxUnnaKL7urxLOngzoPcXxmiUKrDBOiTMJtnybrsJQuifwY84YitAFrA1RfOoQ-V5x0GRTFw=w600',
                        title='Foreign language translation menu-10/10',
                        text='European language translation(6/6)',
                        actions=[
                            MessageTemplateAction(
                                label='Russian',
                                text='翻譯俄羅斯語'
                            ),
                            MessageTemplateAction(
                                label='Czech',
                                text='翻譯捷克語'
                            ),
                            MessageTemplateAction(
                                label='Romanian',
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
    elif user_message.find('Hospital Search') != -1:
        lang = '中'
        KMSH_UserDB_Con.set_trmode_m(uid, lang)

        Response_info = 'You have entered the [Hospital Search] function!\nTo leave this function, please enter the text command [Leave Hospital Search] or [Cancel Hospital Search]!'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(Response_info))
        Response_Quick = Quick_text()
        line_bot_api.push_message(uid, Response_Quick)

############################## 顯示使用者所儲存的醫院 ######################
    elif user_message.find('My Hospital') != -1:
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
    elif user_message.find('Taiwan Epidemic News') != -1:

        Flu_message = TemplateSendMessage(
            alt_text='台灣疫情',
            template=ButtonsTemplate(
                title="Taiwan'"+ "s" + " Epidemic News",
                text='View the status of the epidemic and related announcements',
                actions=[
                    URITemplateAction(
                        label='Enter the website',
                        uri="https://www.cdc.gov.tw/En"
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

# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 13:11:24 2020

@author: wenzao
"""
lang_db=[       
       {'lang':'英(美)語','lang_code':'英','vlang':'en'},
       {'lang':'英(美)語','lang_code':'美','vlang':'en'},
       {'lang':'日本語','lang_code':'日','vlang':'ja'},
       {'lang':'韓語','lang_code':'韓','vlang':'ko'},
       {'lang':'法語','lang_code':'法','vlang':'fr'},
       {'lang':'德語','lang_code':'德','vlang':'de'},
       {'lang':'西班牙語','lang_code':'西','vlang':'es'},
       {'lang':'印尼語','lang_code':'印','vlang':'id'},
       {'lang':'泰語','lang_code':'泰','vlang':'th'},
       {'lang':'越南語','lang_code':'越','vlang':'vi'},
       {'lang':'印度語','lang_code':'度','vlang':'hi'},
       {'lang':'菲律賓語','lang_code':'菲','vlang':'fil'},
       {'lang':'馬來西亞語','lang_code':'馬','vlang':'id'},
       {'lang':'阿拉伯語','lang_code':'阿','vlang':'ar'},
       {'lang':'義大利語','lang_code':'義','vlang':'it'},
       {'lang':'俄羅斯語','lang_code':'俄','vlang':'ru'},
       {'lang':'波蘭語','lang_code':'波','vlang':'pl'},
       {'lang':'葡萄牙語','lang_code':'葡','vlang':'pt'},
       {'lang':'荷蘭語','lang_code':'荷','vlang':'nl'},
       {'lang':'瑞典語','lang_code':'瑞','vlang':'sv'},
       {'lang':'捷克語','lang_code':'捷','vlang':'cs'},
       {'lang':'孟加拉語','lang_code':'孟','vlang':'bn'},
       {'lang':'希臘語','lang_code':'希','vlang':'el'},
       {'lang':'愛爾蘭語','lang_code':'愛','vlang':'ga'},
       {'lang':'挪威語','lang_code':'挪','vlang':'no'},
       {'lang':'土耳其語','lang_code':'土','vlang':'tr'},
       {'lang':'烏克蘭語','lang_code':'烏','vlang':'uk'},
       {'lang':'匈牙利語','lang_code':'匈','vlang':'hu'},
       {'lang':'海地語','lang_code':'海','vlang':'ht'},
       {'lang':'芬蘭語','lang_code':'芬','vlang':'fi'},
       {'lang':'丹麥語','lang_code':'丹','vlang':'da'},
       {'lang':'波斯語','lang_code':'斯','vlang':'fa'},
       {'lang':'羅馬尼亞語','lang_code':'羅','vlang':'ro'},
       {'lang':'希伯來語','lang_code':'伯','vlang':'he'},
       {'lang':'巴西語','lang_code':'巴','vlang':'br'},
       {'lang':'保加利亞語','lang_code':'保','vlang':'bg'},
        ]
#user_lang='牙'
#----------------------------------------------------------------------------
def getcode(user_message): #取得語言縮寫代碼           
    if user_message.find('英語')!=-1 or user_message.find('英文')!=-1:       
        new_lang_code='英'
        
    elif user_message.find('美語')!=-1 or user_message.find('美文')!=-1:
        new_lang_code='英'
        
    elif user_message.find('日語')!=-1 or user_message.find('日文')!=-1:
        new_lang_code='日' 
        
    elif user_message.find('韓語')!=-1 or user_message.find('韓文')!=-1:       
        new_lang_code='韓'
        
    elif user_message.find('法語')!=-1 or user_message.find('法文')!=-1:      
        new_lang_code='法' 
        
    elif user_message.find('德語')!=-1 or user_message.find('德文')!=-1:      
        new_lang_code='德'         
        
    elif user_message.find('西班牙')!=-1 :       
        new_lang_code='西' 
        
    elif user_message.find('印尼')!=-1:       
        new_lang_code='印' 
        
    elif user_message.find('泰語')!=-1 or user_message.find('泰文')!=-1:      
        new_lang_code='泰'  
        
    elif user_message.find('越南')!=-1 :       
        new_lang_code='越' 
        
    elif user_message.find('印度')!=-1 :       
        new_lang_code='度' 
        
    elif user_message.find('菲律賓')!=-1 :        
        new_lang_code='菲' 
        
    elif user_message.find('馬來西亞')!=-1 :        
        new_lang_code='馬' 
        
    elif user_message.find('阿拉伯')!=-1 :       
        new_lang_code='阿' 
        
    elif user_message.find('義大利')!=-1 :       
        new_lang_code='義'
        
    elif user_message.find('俄羅斯')!=-1 :       
        new_lang_code='俄' 

    elif user_message.find('波蘭')!=-1 :       
        new_lang_code='波' 

    elif user_message.find('葡萄牙')!=-1 :        
        new_lang_code='葡' 
        
    elif user_message.find('荷蘭')!=-1 :       
        new_lang_code='荷'
        
    elif user_message.find('瑞典')!=-1 :       
        new_lang_code='瑞' 
        
    elif user_message.find('捷克')!=-1 :       
        new_lang_code='捷' 
        
    elif user_message.find('孟加拉')!=-1 :       
        new_lang_code='孟'
        
    elif user_message.find('希臘')!=-1 :       
        new_lang_code='希' 

    elif user_message.find('愛爾蘭')!=-1 :       
        new_lang_code='愛' 
        
    elif user_message.find('挪威')!=-1 :       
        new_lang_code='挪' 
        
    elif user_message.find('土耳其')!=-1 :       
        new_lang_code='土' 
                          
    elif user_message.find('烏克蘭')!=-1 :      
        new_lang_code='烏'

    elif user_message.find('匈牙利')!=-1 :      
        new_lang_code='匈'
        
    elif user_message.find('海地')!=-1 :       
        new_lang_code='海'
        
    elif user_message.find('芬蘭')!=-1 :       
        new_lang_code='芬'
        
    elif user_message.find('丹麥')!=-1 :      
        new_lang_code='丹'
        
    elif user_message.find('波斯')!=-1 :       
        new_lang_code='斯' 
        
    elif user_message.find('羅馬尼亞')!=-1 :      
        new_lang_code='羅' 
        
    elif user_message.find('希伯來')!=-1 :      
        new_lang_code='伯' 
        
    elif user_message.find('巴西')!=-1 :      
        new_lang_code='巴' 

    elif user_message.find('保加利亞')!=-1 :      
        new_lang_code='保'               
    else:
        new_lang_code=''
                                             
    return(new_lang_code)
#---------------------------------------------    
def getname(new_lang_code): #取得語言名稱全名        
    target_lang_name=''    
    for i in lang_db:
        if i['lang_code'] == new_lang_code:
            target_lang_name= i['lang']
            
    return(target_lang_name)    
#-----------------------------------------------    
def getvoicecode(new_lang_code): #取得語GOOGLE語種合成編碼        
    target_vcode=''    
    for i in lang_db:
        if i['lang_code'] == new_lang_code:
            target_vcode= i['vlang']
            
    return(target_vcode)  
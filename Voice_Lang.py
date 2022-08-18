# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 18:03:45 2020

@author: toocool
"""
     #lang1='英'
def get_voicelang(lang1):
    
    voicelang_db=[
           {'lang':'英','vlang':'en'},
           {'lang':'日','vlang':'ja'},
           {'lang':'韓','vlang':'ko'},
           {'lang':'法','vlang':'fr'},
           {'lang':'德','vlang':'de'},
           {'lang':'西','vlang':'es'},
           {'lang':'印','vlang':'id'},
           {'lang':'泰','vlang':'th'},
           {'lang':'越','vlang':'vi'},
           {'lang':'度','vlang':'hi'},
           {'lang':'菲','vlang':'fil'},
           {'lang':'馬','vlang':'id'},
           {'lang':'阿','vlang':'ar'},
            ]
    
    voice_lang=''
    for i in voicelang_db:
        if i['lang'] == lang1:
            voice_lang=i['vlang']
            
    return(voice_lang)

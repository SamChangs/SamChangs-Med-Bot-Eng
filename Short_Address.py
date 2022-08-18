# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 18:36:08 2020

@author: toocool
"""
import bitly_api      #短網址呼叫使用，Python 程式模組

def Ans(url_addr):
    BITLY_ACCESS_TOKEN ="3dbeb87cbad45df1014b241134f0b13bc9cf8737"
    b = bitly_api.Connection(access_token = BITLY_ACCESS_TOKEN)
    B_Response = b.shorten(url_addr)
    short_addr= B_Response['url']
    
    return(short_addr)
        
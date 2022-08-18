# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 01:25:04 2021

@author: wenzao
"""

import bitly_api

# url="https://www.kmsh.org.tw" 

def ans(url):
    
    short_addr=''
    BITLY_ACCESS_TOKEN ="3dbeb87cbad45df1014b241134f0b13bc9cf8737" 
    b = bitly_api.Connection(access_token = BITLY_ACCESS_TOKEN)
    response = b.shorten(url)
    short_addr= response['url']
    
    return(short_addr)
    
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
    sym_message = ImagemapSendMessage(
            base_url='https://lh3.googleusercontent.com/d/1clM41IBsO525gl9vIsjz-2sCE3G2GT5m=w1600-h1600?authuser=0',
            alt_text='imagemap',
            base_size=BaseSize(height=1040, width=1200),
               actions=[
                MessageImagemapAction (
                    text='H1',
                    area=ImagemapArea(
                        x=0, y=120, width=600, height=120
                    )
                ),
                MessageImagemapAction (
                    text='H2',
                    area=ImagemapArea(
                        x=0, y=240, width=600, height=120
                    )
                ),
                MessageImagemapAction (
                    text='H3',
                    area=ImagemapArea(
                        x=0, y=360, width=600, height=150
                    )
                ),
                MessageImagemapAction (
                    text='H4',
                    area=ImagemapArea(
                        x=0, y=510, width=600, height=150
                    )
                ),
                MessageImagemapAction (
                    text='H5',
                    area=ImagemapArea(
                        x=0, y=660, width=600, height=150
                    )
                ),
                MessageImagemapAction (
                    text='H6',
                    area=ImagemapArea(
                        x=0, y=810, width=600, height=120
                    )
                ),MessageImagemapAction (
                    text='H7',
                    area=ImagemapArea(
                        x=600, y=120, width=600, height=120
                    )
                ),
                MessageImagemapAction (
                    text='H8',
                    area=ImagemapArea(
                        x=600, y=240, width=600, height=120
                    )
                ),
                MessageImagemapAction (
                    text='H9',
                    area=ImagemapArea(
                        x=600, y=360, width=600, height=150
                    )
                ),
                MessageImagemapAction (
                    text='H10',
                    area=ImagemapArea(
                        x=600, y=510, width=600, height=150
                    )
                ),
                MessageImagemapAction (
                    text='H11',
                    area=ImagemapArea(
                        x=600, y=660, width=600, height=150
                    )
                ),
                MessageImagemapAction (
                    text='H12',
                    area=ImagemapArea(
                        x=600, y=810, width=600, height=120
                    )
                )
                ]
            )
    #line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)    
    return 0
##############################################################################
def Head2(uid):
    sym_message = ImagemapSendMessage(
        base_url='https://lh3.googleusercontent.com/fife/AAbDypBHEs0ZExTi7P8KpVmk4MqLoO9AkL6ffqgwUAlNqZHLVccb-X1fD5Q_tAbXArBpwKQ4Uep91E9GQS8GkaUOMJ8HIvbhJRWIbm7Foa8SYgQPOHbq3kPqPJfGdUAwF_JFQR8lv5AmUk8uPTBJ01yo9Gxx10q5dTBPlX9jas7YHdpmh6g9k6L8QQ4t7BikjxHQUVmAKZm0mN13Q6vH4_POrsxnv8EqxSig2W9Gb62gHybtSKLXFae-L_yPIceH4Gaa7tkzPQ3QGVOz3w6uezeEJSSocgMDKXh6U80K8CAnVkFiVFA8-D939cl4X_e44-Q9fLk_74qdj6z7IZ3xLzq9aXIMOeJ62ugtBqnJ6cl83zrDcY7Vyj0Bf7-hueISOQhQcyVr7VZUfQ1W1XTOF-UiY3xzlQmGrsXg7oKQPh3Tagfs1Hs_ThDUmMlBE_stLz1ff968MT0s4EkWQwWRUfaZIn4zYiex7Ljmf5LjxV0iZro-O1I5-ISPpqasXduAd5vtKEm5OKMcIG7D8ERfO9lPlQCgDNZKpCC8SU8RCQQBZE98ASKJV7Ibly_nfi9mV64w3i7VEyF-jLJycL3gADRQtQ0mBP4tvCskqXLYg5spHJ-wm9Y_aUrRyDykY7cpWl5PCCj2cxTVQo9u3AR11v3duSXu0S1tsc_4Slg6pyvIYuLTqbB3Zh8D_n-iX0o2bXk31dKNPM5PtzJeNvHFFOvx2MPmjdLSHfKsiPfnHdtNtghhBmlfl5FhG_Pb_b6NnuTimA-dwbthHoAZ93iCTSb61hLG3rZXwB0jAB1Zyd4zaJ6gT3g9OvU4yuFzc4edVhoxpFx0gX3zmeY9zkDps09pqKGs712R7Xpxh7hAwb1jOY8czMk7UAQIZC8WohiZV0ypN5kmLQ2r2qgPyryBRF86ZCJb4EESZLBaOfdX91XvjPYa7zM184AtawaXu9yFALDo-2W1dnAuYM2rHIbqgWqVxBwDQacHZuy594ZOhNbHnWt_L0jXnsulsOHv-8TGqBQenkrkPE_-lRfq7ZGy6-7NBe5bmol3dxwOIV3wnPfZh5w70-i1c0s5KBeyXBhu-Epj9zemjbyWqD3GQmz3G-5-9fqPUKDcJ3QTQRCuB_isoJZwPaRAv_vTtOe-r28Xts8xJamklX5OHwcmjv5o4VC7VGnXW9WYWKBdEKxjdWJ1KBZESJftLv06NhgtNPMg4oy_66dIFQcODSqsD4Box0ou-lcCrscEHmMPyhw4YdzA4CUExwis51ndFPV7LGgN3WKM4ss97FnDJg3qnLTh2zzDFZfB5WojeeBeVypUfOKTgA=w1600-h1600?authuser=0',
        alt_text='imagemap',
        base_size=BaseSize(height=700, width=1200),
        actions=[
            MessageImagemapAction(
                text='H13',
                area=ImagemapArea(
                    x=0, y=120, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='H14',
                area=ImagemapArea(
                    x=0, y=270, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='H15',
                area=ImagemapArea(
                    x=0, y=420, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='H16',
                area=ImagemapArea(
                    x=600, y=120, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='H17',
                area=ImagemapArea(
                    x=600, y=270, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='H18',
                area=ImagemapArea(
                    x=600, y=420, width=600, height=150
                )
            )
        ]
    )
    # line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)
    return 0
###############################################################################    
def Head3(uid):
    sym_message = ImagemapSendMessage(
        base_url='https://lh3.googleusercontent.com/fife/AAbDypDsYDJ5UMT_WT05fXrMv016g6p33WiJUoC28UqUqgUNOj0N5hgQUCBl7a6vRoHnkHJq9RbHrU0HI0aBaAsyt_vbnxdu-BuahKmVWdIYf05ZHluZGjoboIogW-JAia_ntEfV695UZaeqypZ6zrjf9PfFeRYB0kmHLSYLX4lUWhCj3zMGv8NuXFqp4UHjBP6hSFDyupfduEf2nYW9ItMa8PW8WCeOMKOt1nuXFrotGCOJofaBk6ZgyjdgzkzBwC2tIgXG4VzwmPChD1MjZIdcCtqq6dvTDTPSlkx0keKhbzUQaqvZPjuI0KimdfIKeQRIHUikdq8irl6SOId2yGHVhTMjYeZa1Jm50n3DlThahP0hbo5lOw7AeTJB-Bha6aCyYbaISdhWQcxdqy7GK_1-pgj5CJDVmCnl1s5RxhUxFws8SRdXLoGghZHZKRoaixN_KjSit5gpEIKqwEzNlXje1yXGKYiqXhkAVxRWgpE_f17xscCnItcPg7JZdcsGk7At9QsNQG999PdBjfK5xG0Cz18xp4vll56Dpj_JKDnCxQvL2dxBDRnqiw_noK-l3k-CFGh1WoVTYU9-G25TpwWx6QG6NeU_l2L_THfCJU9trTjs2wtCAPFU7CyKPnjYJnCskkKkmJgO6Ri8I0187NsgKRsmJNgASAdy3JOJj-5MfoqgjJE0A73VNMS3KW5HKEsScgurQRBlqcGWO3ntrhqoQJ5ugYbDOWZ_LAkpdYimP2g15dvkh7hy86JM5JP2yRXa2WaClbeRnWP15d6qybvEXRTqm0Ine0ECo7ZvWkWldq5LS9-CvPjJuE8ZhMtK0Z4KqFqhMCwJBfMkzcuFuSHtouibiWybLw0IPjEQ6jcmTSH0irNTF-8O7DajbRzjb_RY-iQ6e-cGCEsUZER5spfaudUCgNUWSFU_P6h4r3jFPcVkFgEkiO3VVjhypLUyPXKDSgtHuOPU_UNEV9yl9wvTtLMuEe6_wSjxMTmXQ8kl9XB1Cc1H0ao98iIAqxdSWoUAegiZKGN0fkCKTxhsEIpDHXYDQTJ0GRddiNyqaNtTV6YdWdwtsjzb70Y0LqokOYkwyKinbjO5UC8tjLiqyJYZt6cOU6tXjzC61iCVCsnm6FSKCtXDFaxwkMUorPrWsu04FP1-vzzJl941Ok2_nChNlqxPUdOX79gpp-HkiijVZwAmDeKatwIfw-iVyKscJkPBF9Y84-E4x3med9Tut92Adx6Ge9fYV3soyMuRojyeg4vbNDtOXjJofAhtF2fWMVRy7-SWgrLH7m0MRc7Q95bk23bZEE8homePutJJTRnt-Q=w1600-h1600?authuser=0',
        alt_text='imagemap',
        base_size=BaseSize(height=700, width=1200),
        actions=[
            MessageImagemapAction(
                text='H19',
                area=ImagemapArea(
                    x=230, y=140, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='H20',
                area=ImagemapArea(
                    x=230, y=290, width=600, height=120
                )
            ),
            MessageImagemapAction(
                text='H21',
                area=ImagemapArea(
                    x=230, y=500, width=600, height=150
                )
            )
        ]
    )
    # line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)
    return 0

###############################################################################    
def Neck(uid):
    sym_message = ImagemapSendMessage(
        base_url='https://lh3.googleusercontent.com/fife/AAbDypCNFEDMYVdzHr8fo3fnmJnpKHHDKgXF-6NRWEZyPYpwaCG02-ANaqy1VqCN5-ugtMIjkVFy8ETRuRn7nYijE5JG2MfhacAdIVe3zf5dGUuzod7HxoQHeJ6y_iED4DN9kG7FuzxmF0rDwqTnN5ZxhZcHStaaZQ13InT9ylLz_sCoDTMIqma7ysTLnMY50UK5cXGwGj8SwieurO6vQYH0W6S3vGetRq-FraloMnD3dglpqVmhs75aTSKySHj-rUh07DhZll9CG_xvPqBxj2m-JxpyIsJ67OMt8zX8vfvZ4f_w7TKzivVmS3aW7pxe6oB6do51D2mUDlwi4YqeTfucp-dX-Zl0pZW9OYWM3jDNkOmhbrug8l8eXtslKbyhTlUHNrPcT7QdfFoZheZsmefXF3hT-w1rKaAPJmM9Ln3LWaM8uLqRC5bnIK-DCVNLmIJV2Q_IaLK1Lw5E9TnsMQrMjmrUv3SVRrInBjJD4PYTcAFm293dUWciIxzuFUthPagosm0rlKzEefYJVGNmj_XFMu5tNDKwKAuIxYoH2s7fYELjv3R-HYJZbZN6x1rE_O7m23P48CUk9MZl0Hr-XKIPbgV0UjGStpR03uWUAnFnYz2QaarGiyyaOoYuYpFfYtpC3NXe-WHnzsP36zIJrXaQWjXRlwbVwx1QPRt1YOPduu866pWfBxpECc5i-bOXF13H9Aj_ZSijLuxDb1WXfvQtNVZvNM8cdRe1MMg6Ca0DvQB0aJuiNAXK92Cn2sc_O2Lk18tKOMVW7whZE6528ibqrz9P8pqBLSN1njUJIJBsVH1uxe6JXP3tPdFqMb_aO7z5cirXFsef5YHPWPgeU05Q6_fMMqd6bto9bCyXCD7JGkZz8pLglbiImbqxwQeTYNbI36OYvOll4XElBDynZcmKAu0xcoH7RbmuV2CYVvIl7NUTm7wN8knBUbvqtJRQoYDHqcg811aBj0tvJOyOaJ-i4SalLrJG1DH_FfAEQY-KneiRPidk9mPBvQGwHR9daFM5lU7IUmtKWnb1HBnz9hEy4OsCsmXtEQpRUjM5P8yeH0js1p9lV5BRq5VYjHqYRgPV0E3rSkwh9A_pwYu0XfEfZPd5xsMTR91M1X7Fkoc7OzxY6ufKzKo_oMiNsb5giNCF-zqg6ouEt9il-MzVZ25appCjGGqS58HhjvvhSRqprisWfHc2cKtCEDSYL1soXMXiILaphTJMI_JbDSOJ75hRzQmKcCJY3KUKvjSuBCk2X_6DG1pLWp6xaH3KnHC0LoirmnaqoL1XTmltgxb0hnLMYowN7sfeOcL5p7CkOFy4xQ=w1600-h1600?authuser=0',
        alt_text='imagemap',
        base_size=BaseSize(height=700, width=1200),
        actions=[
            MessageImagemapAction(
                text='N1',
                area=ImagemapArea(
                    x=230, y=140, width=600, height=150
                )
            ),
            MessageImagemapAction(
                text='N2',
                area=ImagemapArea(
                    x=230, y=290, width=600, height=120
                )
            ),
            MessageImagemapAction(
                text='N3',
                area=ImagemapArea(
                    x=230, y=500, width=600, height=150
                )
            )
        ]
    )
    # line_bot_api.reply_message(event.reply_token,clinic_message)
    line_bot_api.push_message(uid, sym_message)
    return 0

    
    

from KMSH_UserDB_Con import District_hp_db, Regional_hp_db, clinic_hp_db, medicine_hp_db, pharmacy_hp_db
from Str_format import str_Format
from linebot.models import *

def Type_of_visit(address_type):
    flex_message = FlexSendMessage(
        alt_text='查詢看診類別',
        contents=BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url="https://cdn.pixabay.com/photo/2017/08/18/12/23/building-2654823__340.jpg",
                margin="none",
                size="full",
                aspect_ratio="1.51:1",
                aspect_mode="cover",
                background_color="#FFE8E8FF"
            ),
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="看診類別",
                                  weight="bold",
                                  size="xl",
                                  wrap=True,
                                  color="#138105FF",
                                  align="start"),
                    SeparatorComponent(margin="md",
                                       color="#000000FF"),
                    ButtonComponent(action=PostbackAction(
                                    label='地區醫院',
                                    display_text='查詢地區醫院',
                                    data="action=search,{lan},{long},地區醫院"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='區域醫院',
                                    display_text='查詢區域醫院',
                                    data="action=search,{lan},{long},區域醫院"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='診所',
                                    display_text='查詢診所',
                                    data="action=search,{lan},{long},診所"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='醫學中心',
                                    display_text='查詢醫學中心',
                                    data="action=search,{lan},{long},醫學中心"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='藥局',
                                    display_text='查詢藥局',
                                    data="action=search,{lan},{long},藥局"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    )
                ]
            ),
        )
    )
    return  flex_message

def Search_address(lat,long,address_type):
    if address_type == "地區醫院":
         name = "地區"
         hs_Name = 'Name'
         address = "Address"
         db_type = District_hp_db
         Vs_time = "固定看診時段"
         Org_species = "特約類別"
         Treatment_type = "診療科別"
         db_type_name = "District_hp_db"

    elif address_type == "區域醫院":
         name = "區域"
         hs_Name = 'Name'
         address = "Address"
         db_type = Regional_hp_db
         Vs_time = "固定看診時段"
         Org_species = "特約類別"
         Treatment_type = "診療科別"
         db_type_name = "Regional_hp_db"

    elif address_type == "診所":
         name = "診所"
         hs_Name = 'Name'
         address = "Address"
         Vs_time = "固定看診時段 "
         Org_species = "特約類別"
         Treatment_type = "診療科別 "
         db_type = clinic_hp_db
         db_type_name = "clinic_hp_db"

    elif address_type == "醫學中心":
         name = "醫學"
         hs_Name = 'Name'
         address = "Address"
         Vs_time = "固定看診時段"
         Org_species = "特約類別"
         Treatment_type = "診療科別"
         db_type = medicine_hp_db
         db_type_name = "medicine_hp_db"

    elif address_type == "藥局":
         name = "藥局"
         hs_Name = 'Name'
         address = "Address"
         Vs_time = "固定看診時段"
         Org_species = "特約類別"
         Treatment_type = "診療科別"
         db_type = pharmacy_hp_db
         db_type_name = "pharmacy_hp_db"
    else:
        raise NameError("Error address_type name")

    contents = dict()
    contents['type'] = 'carousel'
    bubbles = []
    x = 1

    cellection = db_type()
    for i in cellection.find():
        if x <= 5:
            if name == "醫學":
                contents = BubbleContainer(
                    header=BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        height="100px",
                        background_color="#59B98CFF",
                        contents=[
                            TextComponent(
                                text=i[hs_Name],
                                weight="regular",
                                size="xl",
                                color="#FFFFFFFF",
                                align="center",
                                wrap=True,
                                offset_top="10px"
                            )
                        ]
                    ),
                    body=BoxComponent(
                        layout="vertical",
                        offset_bottom="20px",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                width="290px",
                                offset_end="21px",
                                contents=[
                                    BoxComponent(
                                        layout="vertical",
                                        height="52px",
                                        padding_end="34px",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/1XMhQjM/1.png",
                                                size="xxs",
                                                position="absolute",
                                                offset_top="8px",
                                            ),
                                            TextComponent(
                                                text=i[address],
                                                wrap=True,
                                                offset_top="15px",
                                                offset_start="35px",
                                                size="sm",
                                                color="#000000",
                                            ),
                                        ],
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0",
                                        margin="none"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/vY4Wpd1/1.png",
                                                size="xxs",
                                                position="absolute"
                                            ),
                                            TextComponent(
                                                text=i[Org_species],
                                                offset_start="40px",
                                                contents=[],
                                                size="sm",
                                                color="#000000",
                                                offset_top="14px"
                                            )
                                        ],
                                        height="40px"
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/wd9Sv3m/image.png",
                                                size="xxs",
                                                position="absolute"
                                            ),
                                            TextComponent(
                                                text=i["電話"],
                                                offset_start="40px",
                                                contents=[],
                                                flex=3,
                                                offset_top="14px",
                                                color="#000000",
                                            )
                                        ],
                                        height="40px"
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        padding_bottom="25px",
                                        padding_end="34px",
                                        offset_top="10px",
                                        contents=[
                                            ImageComponent(
                                                url= "https://i.ibb.co/Byx5sJT/list-document-interface-symbol.png",
                                                size="30px",
                                                offset_top="3px",
                                                offset_start="2px",
                                                position="absolute",
                                            ),
                                            TextComponent(
                                                text= i[Treatment_type],
                                                wrap=True,
                                                offset_start="34px",
                                                color="#000000"
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    ),
                    footer=BoxComponent(
                        layout="vertical",
                        backgroundColor="#59B98CFF",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                backgroundColor="#FFFFFFFF",
                                contents=[
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=MessageAction(
                                        label="連絡電話",
                                        text=i["電話"]+ "\n" +i[hs_Name])
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='看診時間',
                                        display_text='看診時段',
                                        data="action=time,{hs_Name},{Vs_time}"
                                            .format(hs_Name=i[hs_Name],Vs_time=i[Vs_time])
                                        )
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=URIAction(
                                        label="導航目的地",
                                        uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                            lat=i["經度E"], long=i["緯度N"])),
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='加入我的醫院',
                                        display_text='{hs_Name}已加入我的醫院'.format(hs_Name=i[hs_Name]),
                                        data="action=add,{db_type_name},{hs_Name}"
                                            .format(db_type_name=db_type_name, hs_Name=i[hs_Name])
                                        ),
                                    )
                                ]
                            )
                        ]
                    )
                )
                bubbles.append(contents)
                x+=1
            elif abs(lat - i['經度E']) < 0.01 and abs(long - i['緯度N']) < 0.01 and name != "地區":
                contents = BubbleContainer(
                    header=BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        height="100px",
                        background_color="#59B98CFF",
                        contents=[
                            TextComponent(
                                text=i[hs_Name],
                                weight="regular",
                                size="xl",
                                color="#FFFFFFFF",
                                align="center",
                                wrap=True,
                                offset_top="10px"
                            )
                        ]
                    ),
                    body=BoxComponent(
                        layout="vertical",
                        offset_bottom="20px",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                width="290px",
                                offset_end="21px",
                                contents=[
                                    BoxComponent(
                                        layout="vertical",
                                        height="52px",
                                        padding_end="34px",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/1XMhQjM/1.png",
                                                size="xxs",
                                                position="absolute",
                                                offset_top="8px",
                                            ),
                                            TextComponent(
                                                text=i[address],
                                                wrap=True,
                                                offset_top="15px",
                                                offset_start="35px",
                                                size="sm",
                                                color="#000000",
                                            ),
                                        ],
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0",
                                        margin="none"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/vY4Wpd1/1.png",
                                                size="xxs",
                                                position="absolute"
                                            ),
                                            TextComponent(
                                                text=i[Org_species],
                                                offset_start="40px",
                                                contents=[],
                                                size="sm",
                                                color="#000000",
                                                offset_top="14px"
                                            )
                                        ],
                                        height="40px"
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/wd9Sv3m/image.png",
                                                size="xxs",
                                                position="absolute"
                                            ),
                                            TextComponent(
                                                text=i["電話"],
                                                offset_start="40px",
                                                contents=[],
                                                flex=3,
                                                offset_top="14px",
                                                color="#000000",
                                            )
                                        ],
                                        height="40px"
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        padding_bottom="25px",
                                        padding_end="34px",
                                        offset_top="10px",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/Byx5sJT/list-document-interface-symbol.png",
                                                size="30px",
                                                offset_top="3px",
                                                offset_start="2px",
                                                position="absolute",
                                            ),
                                            TextComponent(
                                                text=i[Treatment_type],
                                                wrap=True,
                                                offset_start="34px",
                                                color="#000000"
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    ),
                    footer=BoxComponent(
                        layout="vertical",
                        backgroundColor="#59B98CFF",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                backgroundColor="#FFFFFFFF",
                                contents=[
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=MessageAction(
                                        label="連絡電話",
                                        text=i["電話"]+ "\n" +i[hs_Name])
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='看診時間',
                                        display_text='看診時段',
                                        data="action=time,{hs_Name},{Vs_time}"
                                            .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                                    )
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=URIAction(
                                        label="導航目的地",
                                        uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                            lat=i["經度E"], long=i["緯度N"])),
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='加入我的醫院',
                                        display_text='{hs_Name}已加入我的醫院'.format(hs_Name=i[hs_Name]),
                                        data="action=add,{db_type_name},{hs_Name}"
                                            .format(db_type_name=db_type_name, hs_Name=i[hs_Name])
                                    ),
                                    )
                                ]
                            )
                        ]
                    )
                )
                bubbles.append(contents)
                x += 1
            elif abs(lat - i['經度E']) < 0.02 and abs(long - i['緯度N']) < 0.02 and name == "地區":  # 地區小於0.1會找不到，所以指定地區為小於0.02
                contents = BubbleContainer(
                    header=BoxComponent(
                        layout="vertical",
                        spacing="sm",
                        height="100px",
                        background_color="#59B98CFF",
                        contents=[
                            TextComponent(
                                text=i[hs_Name],
                                weight="regular",
                                size="xl",
                                color="#FFFFFFFF",
                                align="center",
                                wrap=True,
                                offset_top="10px"
                            )
                        ]
                    ),
                    body=BoxComponent(
                        layout="vertical",
                        offset_bottom="20px",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                width="290px",
                                offset_end="21px",
                                contents=[
                                    BoxComponent(
                                        layout="vertical",
                                        height="52px",
                                        padding_end="34px",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/1XMhQjM/1.png",
                                                size="xxs",
                                                position="absolute",
                                                offset_top="8px",
                                            ),
                                            TextComponent(
                                                text=i[address],
                                                wrap=True,
                                                offset_top="15px",
                                                offset_start="35px",
                                                size="sm",
                                                color="#000000",
                                            ),
                                        ],
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0",
                                        margin="none"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/vY4Wpd1/1.png",
                                                size="xxs",
                                                position="absolute"
                                            ),
                                            TextComponent(
                                                text=i[Org_species],
                                                offset_start="40px",
                                                contents=[],
                                                size="sm",
                                                color="#000000",
                                                offset_top="14px"
                                            )
                                        ],
                                        height="40px"
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/wd9Sv3m/image.png",
                                                size="xxs",
                                                position="absolute"
                                            ),
                                            TextComponent(
                                                text=i["電話"],
                                                offset_start="40px",
                                                contents=[],
                                                flex=3,
                                                offset_top="14px",
                                                color="#000000",
                                                actions=[
                                                    URIAction(
                                                        label='連絡電話',
                                                        uri="tel:" + i["電話"]
                                                    ),
                                                ]
                                            )
                                        ],
                                        height="40px"
                                    ),
                                    SeparatorComponent(
                                        color="#C0C0C0"
                                    ),
                                    BoxComponent(
                                        layout="vertical",
                                        padding_bottom="25px",
                                        padding_end="34px",
                                        offset_top="10px",
                                        contents=[
                                            ImageComponent(
                                                url="https://i.ibb.co/Byx5sJT/list-document-interface-symbol.png",
                                                size="30px",
                                                offset_top="3px",
                                                offset_start="2px",
                                                position="absolute",
                                            ),
                                            TextComponent(
                                                text=i[Treatment_type],
                                                wrap=True,
                                                offset_start="34px",
                                                color="#000000"
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    ),
                    footer=BoxComponent(
                        layout="vertical",
                        backgroundColor="#59B98CFF",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                backgroundColor="#FFFFFFFF",
                                contents=[
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=MessageAction(
                                        label="連絡電話",
                                        text=i["電話"] + "\n" + i[hs_Name])
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='看診時間',
                                        display_text='看診時段',
                                        data="action=time,{hs_Name},{Vs_time}"
                                            .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                                    )
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=URIAction(
                                        label="導航目的地",
                                        uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                            lat=i["經度E"], long=i["緯度N"])),
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='加入我的醫院',
                                        display_text='{hs_Name}已加入我的醫院'.format(hs_Name=i[hs_Name]),
                                        data="action=add,{db_type_name},{hs_Name}"
                                            .format(db_type_name=db_type_name, hs_Name=i[hs_Name]),
                                        )
                                    ),
                                ]
                            )
                        ]
                    )
                )
                bubbles.append(contents)
                x += 1

    if x == 1:
        message = TextSendMessage(text="附近沒有相關看診科別")
        return message
    elif name == "區域":
        cellection = District_hp_db()
        for i in cellection.find():
            if x <= 5:
                if abs(lat - i['經度E']) < 0.02 and abs(long - i['緯度N']) < 0.02 :
                    contents = BubbleContainer(
                        header=BoxComponent(
                            layout="vertical",
                            spacing="sm",
                            height="100px",
                            background_color="#59B98CFF",
                            contents=[
                                TextComponent(
                                    text=i[hs_Name],
                                    weight="regular",
                                    size="xl",
                                    color="#FFFFFFFF",
                                    align="center",
                                    wrap=True,
                                    offset_top="10px"
                                )
                            ]
                        ),
                        body=BoxComponent(
                            layout="vertical",
                            offset_bottom="20px",
                            contents=[
                                BoxComponent(
                                    layout="vertical",
                                    width="290px",
                                    offset_end="21px",
                                    contents=[
                                        BoxComponent(
                                            layout="vertical",
                                            height="52px",
                                            padding_end="34px",
                                            contents=[
                                                ImageComponent(
                                                    url="https://i.ibb.co/1XMhQjM/1.png",
                                                    size="xxs",
                                                    position="absolute",
                                                    offset_top="8px",
                                                ),
                                                TextComponent(
                                                    text=i[address],
                                                    wrap=True,
                                                    offset_top="15px",
                                                    offset_start="35px",
                                                    size="sm",
                                                    color="#000000",
                                                ),
                                            ],
                                        ),
                                        SeparatorComponent(
                                            color="#C0C0C0",
                                            margin="none"
                                        ),
                                        BoxComponent(
                                            layout="vertical",
                                            contents=[
                                                ImageComponent(
                                                    url="https://i.ibb.co/vY4Wpd1/1.png",
                                                    size="xxs",
                                                    position="absolute"
                                                ),
                                                TextComponent(
                                                    text=i[Org_species],
                                                    offset_start="40px",
                                                    contents=[],
                                                    size="sm",
                                                    color="#000000",
                                                    offset_top="14px"
                                                )
                                            ],
                                            height="40px"
                                        ),
                                        SeparatorComponent(
                                            color="#C0C0C0"
                                        ),
                                        BoxComponent(
                                            layout="vertical",
                                            contents=[
                                                ImageComponent(
                                                    url="https://i.ibb.co/wd9Sv3m/image.png",
                                                    size="xxs",
                                                    position="absolute"
                                                ),
                                                TextComponent(
                                                    text=i["電話"],
                                                    offset_start="40px",
                                                    contents=[],
                                                    flex=3,
                                                    offset_top="14px",
                                                    color="#000000",
                                                )
                                            ],
                                            height="40px"
                                        ),
                                        SeparatorComponent(
                                            color="#C0C0C0"
                                        ),
                                        BoxComponent(
                                            layout="vertical",
                                            padding_bottom="25px",
                                            padding_end="34px",
                                            offset_top="10px",
                                            contents=[
                                                ImageComponent(
                                                    url="https://i.ibb.co/Byx5sJT/list-document-interface-symbol.png",
                                                    size="30px",
                                                    offset_top="3px",
                                                    offset_start="2px",
                                                    position="absolute",
                                                ),
                                                TextComponent(
                                                    text=i[Treatment_type],
                                                    wrap=True,
                                                    offset_start="34px",
                                                    color="#000000"
                                                )
                                            ],
                                        )
                                    ],
                                )
                            ],
                        ),
                        footer=BoxComponent(
                            layout="vertical",
                            backgroundColor="#59B98CFF",
                            contents=[
                                BoxComponent(
                                    layout="vertical",
                                    backgroundColor="#FFFFFFFF",
                                    contents=[
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=MessageAction(
                                            label="連絡電話",
                                            text=i["電話"]+ "\n" +i[hs_Name])
                                        ),
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=PostbackAction(
                                            label='看診時間',
                                            display_text='看診時段',
                                            data="action=time,{hs_Name},{Vs_time}"
                                                .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                                        )
                                        ),
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=URIAction(
                                            label="導航目的地",
                                            uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                                lat=i["經度E"], long=i["緯度N"])),
                                        ),
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=PostbackAction(
                                            label='加入我的醫院',
                                            display_text='{hs_Name}已加入我的醫院'.format(hs_Name=i[hs_Name]),
                                            data="action=add,{db_type_name},{hs_Name}"
                                                .format(db_type_name=db_type_name, hs_Name=i[hs_Name]),
                                        )
                                        ),
                                    ]
                                )
                            ]
                        )
                    )
                    bubbles.append(contents)
                    x += 1
        carousel_contaimer = CarouselContainer(contents=bubbles)
        message = FlexSendMessage(alt_text='查詢結果', contents=carousel_contaimer)
        return message
    else:
        carousel_contaimer = CarouselContainer(contents=bubbles)
        message = FlexSendMessage(alt_text='查詢結果', contents=carousel_contaimer)
        return message

def Visiting_Time(Vs_time):
    message = str_Format(Vs_time)

    return message

def Quick_text():
    """
    透過 QuickReply 的 LocationAction 讀取張當前使用者位置
    """
    Text_Message = TextSendMessage(
        text='傳送位置資訊',
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(action=LocationAction(label="選擇地點"))
            ]
       )
    )
    return Text_Message
#========================================
#將要 reply_Hospital 的資料先進行 db_type 的判斷，需要這樣是因為
# 當初儲存醫院的資料表的key沒有一致，以至於要先確認 db_type 後在帶key值進去
#========================================
def confirm_db_type(my_Hospital):
    global db_type, hs_Name, name, address, text_error, Org_species, Vs_time, db_type_name, Treatment_type

    if my_Hospital["db_type"] == "District_hp_db":
        hs_Name = '醫事機構名稱'
        address = "地 址 "
        name = "地區"
        Vs_time = "固定看診時段 "
        Org_species = "特約類別"
        Treatment_type = "診療科別 "

    elif my_Hospital["db_type"] == "Regional_hp_db":
        name = "區域"
        hs_Name = '醫事機構名稱'
        address = "地 址 "
        Vs_time = "固定看診時段 "
        Org_species = "特約類別"
        Treatment_type = "診療科別 "

    elif my_Hospital["db_type"] == "clinic_hp_db":
        name = "診所"
        hs_Name = '醫事機構名稱'
        address = "地址 "
        Vs_time = "固定看診時段 "
        Org_species = "特約類別"
        Treatment_type = "診療科別 "

    elif my_Hospital["db_type"] == "medicine_hp_db":
        name = "醫學"
        hs_Name = '醫事機構名稱'
        address = "地 址 "
        Vs_time = "固定看診時段"
        Org_species = "特約類別"
        Treatment_type = "診療科別 "

    elif my_Hospital["db_type"] == "pharmacy_hp_db":
        name = "藥局"
        hs_Name = '醫事機構名稱'
        address = "地址"
        Vs_time = "固定看診時段"
        Org_species = "特約類別"
        Treatment_type = "診療科別"

    else:
        raise NameError("Error address_type name")

def reply_Hospital(my_Hospital):
    contents = dict()
    contents['type'] = 'carousel'
    bubbles = []

    if my_Hospital == []:  #判斷我的醫院內陣列內是否有資料，沒有的話 return message
        message = TextSendMessage(text="尚未加入醫院")
        return message
    for i in my_Hospital:
        confirm_db_type(i)
        contents = BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                spacing="sm",
                height="100px",
                background_color="#59B98CFF",
                contents=[
                    TextComponent(
                        text=i[hs_Name],
                        weight="regular",
                        size="xl",
                        color="#FFFFFFFF",
                        align="center",
                        wrap=True,
                        offset_top="10px"
                    )
                ]
            ),
            body=BoxComponent(
                layout="vertical",
                offset_bottom="20px",
                contents=[
                    BoxComponent(
                        layout="vertical",
                        width="290px",
                        offset_end="21px",
                        contents=[
                            BoxComponent(
                                layout="vertical",
                                height="52px",
                                padding_end="34px",
                                contents=[
                                    ImageComponent(
                                        url="https://i.ibb.co/1XMhQjM/1.png",
                                        size="xxs",
                                        position="absolute",
                                        offset_top="8px",
                                    ),
                                    TextComponent(
                                        text=i[address],
                                        wrap=True,
                                        offset_top="15px",
                                        offset_start="35px",
                                        size="sm",
                                        color="#000000",
                                    ),
                                ],
                            ),
                            SeparatorComponent(
                                color="#C0C0C0",
                                margin="none"
                            ),
                            BoxComponent(
                                layout="vertical",
                                contents=[
                                    ImageComponent(
                                        url="https://i.ibb.co/vY4Wpd1/1.png",
                                        size="xxs",
                                        position="absolute"
                                    ),
                                    TextComponent(
                                        text=i[Org_species],
                                        offset_start="40px",
                                        contents=[],
                                        size="sm",
                                        color="#000000",
                                        offset_top="14px"
                                    )
                                ],
                                height="40px"
                            ),
                            SeparatorComponent(
                                color="#C0C0C0"
                            ),
                            BoxComponent(
                                layout="vertical",
                                contents=[
                                    ImageComponent(
                                        url="https://i.ibb.co/wd9Sv3m/image.png",
                                        size="xxs",
                                        position="absolute"
                                    ),
                                    TextComponent(
                                        text=i["電話"],
                                        offset_start="40px",
                                        contents=[],
                                        flex=3,
                                        offset_top="14px",
                                        color="#000000",
                                    )
                                ],
                                height="40px"
                            ),
                            SeparatorComponent(
                                color="#C0C0C0"
                            ),
                            BoxComponent(
                                layout="vertical",
                                padding_bottom="25px",
                                padding_end="34px",
                                offset_top="10px",
                                contents=[
                                    ImageComponent(
                                        url="https://i.ibb.co/Byx5sJT/list-document-interface-symbol.png",
                                        size="30px",
                                        offset_top="3px",
                                        offset_start="2px",
                                        position="absolute",
                                    ),
                                    TextComponent(
                                        text=i[Treatment_type],
                                        wrap=True,
                                        offset_start="34px",
                                        color="#000000"
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                backgroundColor="#59B98CFF",
                contents=[
                    BoxComponent(
                        layout="vertical",
                        backgroundColor="#FFFFFFFF",
                        contents=[
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=MessageAction(
                                label="連絡電話",
                                text=i["電話"] + "\n" + i[hs_Name])
                            ),
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=PostbackAction(
                                label='看診時間',
                                display_text='看診時段',
                                data="action=time,{hs_Name},{Vs_time}"
                                    .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                            )
                            ),
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=URIAction(
                                label="導航目的地",
                                uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                    lat=i["經度E"], long=i["緯度N"])),
                            ),
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=PostbackAction(
                                label='從我的醫院移除',
                                display_text='{hs_Name}已從我的醫院移除'.format(hs_Name=i[hs_Name]),
                                data="action=del,{hs_Name}"
                                    .format(hs_Name=i[hs_Name])
                                ),
                            )
                        ]
                    )
                ]
            )
        )
        bubbles.append(contents)
    carousel_contaimer = CarouselContainer(contents=bubbles)
    message = FlexSendMessage(alt_text='查詢結果', contents=carousel_contaimer)
    return message
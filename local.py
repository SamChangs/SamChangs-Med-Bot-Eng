from KMSH_UserDB_Con import District_hp_db, Regional_hp_db, clinic_hp_db, medicine_hp_db, pharmacy_hp_db
from Str_format import str_Format
from linebot.models import *

def Type_of_visit(address_type):
    flex_message = FlexSendMessage(
        alt_text='Search Consultation Category',
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
                    TextComponent(text="Consultation Category",
                                  weight="bold",
                                  size="xl",
                                  wrap=True,
                                  color="#138105FF",
                                  align="start"),
                    SeparatorComponent(margin="md",
                                       color="#000000FF"),
                    ButtonComponent(action=PostbackAction(
                                    label='District Hospital',
                                    display_text='Search District Hospital',
                                    data="action=search,{lan},{long},District Hospital"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='Regional Hospital',
                                    display_text='Search Regional Hospital',
                                    data="action=search,{lan},{long},Regional Hospital"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='Clinic Hospital',
                                    display_text='Search Clinic Hospital',
                                    data="action=search,{lan},{long},Clinic Hospital"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='Medical center',
                                    display_text='Search Medical center',
                                    data="action=search,{lan},{long},Medical center"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    ),
                    ButtonComponent(action=PostbackAction(
                                    label='Pharmacy',
                                    display_text='Search Pharmacy',
                                    data="action=search,{lan},{long},Pharmacy"
                                        .format(lan=address_type[0], long=address_type[1])
                                    ),
                    )
                ]
            ),
        )
    )
    return  flex_message

def Search_address(lat,long,address_type):
    if address_type == "District Hospital":
         name = "??????"
         hs_Name = 'Name'
         address = "Address"
         db_type = District_hp_db
         Vs_time = "??????????????????"
         Org_species = "facility type"
         Treatment_type = "Medical Specialty"
         db_type_name = "District_hp_db"

    elif address_type == "Regional Hospital":
         name = "??????"
         hs_Name = 'Name'
         address = "Address"
         db_type = Regional_hp_db
         Vs_time = "??????????????????"
         Org_species = "facility type"
         Treatment_type = "Medical Specialty"
         db_type_name = "Regional_hp_db"

    elif address_type == "Clinic Hospital":
         name = "??????"
         hs_Name = 'Name'
         address = "Address"
         Vs_time = "?????????????????? "
         Org_species = "facility type"
         Treatment_type = "Medical Specialty"
         db_type = clinic_hp_db
         db_type_name = "clinic_hp_db"

    elif address_type == "Medical center":
         name = "??????"
         hs_Name = 'Name'
         address = "Address"
         Vs_time = "??????????????????"
         Org_species = "facility type"
         Treatment_type = "Medical Specialty"
         db_type = medicine_hp_db
         db_type_name = "Medical Specialty"

    elif address_type == "Pharmacy":
         name = "??????"
         hs_Name = 'Name'
         address = "Address"
         Vs_time = "??????????????????"
         Org_species = "facility type"
         Treatment_type = "Medical Specialty"
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
            if name == "??????":
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
                                                text=i["??????"],
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
                                        label="Phone Number",
                                        text=i["??????"]+ "\n" +i[hs_Name])
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='Consultation time',
                                        display_text='Consultation period',
                                        data="action=time,{hs_Name},{Vs_time}"
                                            .format(hs_Name=i[hs_Name],Vs_time=i[Vs_time])
                                        )
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=URIAction(
                                        label="Navigation destination",
                                        uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                            lat=i["??????E"], long=i["??????N"])),
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='Join my hospital',
                                        display_text='{hs_Name}joined my hospital'.format(hs_Name=i[hs_Name]),
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
            elif abs(lat - i['??????E']) < 0.01 and abs(long - i['??????N']) < 0.01 and name != "??????":
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
                                                text=i["??????"],
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
                                        label="Phone Number",
                                        text=i["??????"]+ "\n" +i[hs_Name])
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='Consultation time',
                                        display_text='Consultation period',
                                        data="action=time,{hs_Name},{Vs_time}"
                                            .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                                    )
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=URIAction(
                                        label="Navigation destination",
                                        uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                            lat=i["??????E"], long=i["??????N"])),
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='Join my hospital',
                                        display_text='{hs_Name}joined my hospital'.format(hs_Name=i[hs_Name]),
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
            elif abs(lat - i['??????E']) < 0.02 and abs(long - i['??????N']) < 0.02 and name == "??????":  # ????????????0.1??????????????????????????????????????????0.02
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
                                                text=i["??????"],
                                                offset_start="40px",
                                                contents=[],
                                                flex=3,
                                                offset_top="14px",
                                                color="#000000",
                                                actions=[
                                                    URIAction(
                                                        label='Phone Number',
                                                        uri="tel:" + i["??????"]
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
                                        label="Phone Number",
                                        text=i["??????"] + "\n" + i[hs_Name])
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='Consultation time',
                                        display_text='Consultation period',
                                        data="action=time,{hs_Name},{Vs_time}"
                                            .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                                    )
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=URIAction(
                                        label="Navigation destination",
                                        uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                            lat=i["??????E"], long=i["??????N"])),
                                    ),
                                    SeparatorComponent(
                                        color="#CCCCCCFF"
                                    ),
                                    ButtonComponent(action=PostbackAction(
                                        label='Join my hospital',
                                        display_text='{hs_Name}joined my hospital'.format(hs_Name=i[hs_Name]),
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
        message = TextSendMessage(text="There are no related clinics nearby")
        return message
    elif name == "??????":
        cellection = District_hp_db()
        for i in cellection.find():
            if x <= 5:
                if abs(lat - i['??????E']) < 0.02 and abs(long - i['??????N']) < 0.02 :
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
                                                    text=i["??????"],
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
                                            label="Phone Number",
                                            text=i["??????"]+ "\n" +i[hs_Name])
                                        ),
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=PostbackAction(
                                            label='Consultation time',
                                            display_text='Consultation period',
                                            data="action=time,{hs_Name},{Vs_time}"
                                                .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                                        )
                                        ),
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=URIAction(
                                            label="Navigation destination",
                                            uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                                lat=i["??????E"], long=i["??????N"])),
                                        ),
                                        SeparatorComponent(
                                            color="#CCCCCCFF"
                                        ),
                                        ButtonComponent(action=PostbackAction(
                                            label='Join my hospital',
                                            display_text='{hs_Name}joined my hospital'.format(hs_Name=i[hs_Name]),
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
        message = FlexSendMessage(alt_text='????????????', contents=carousel_contaimer)
        return message
    else:
        carousel_contaimer = CarouselContainer(contents=bubbles)
        message = FlexSendMessage(alt_text='????????????', contents=carousel_contaimer)
        return message

def Visiting_Time(Vs_time):
    message = str_Format(Vs_time)

    return message

def Quick_text():
    """
    ?????? QuickReply ??? LocationAction ??????????????????????????????
    """
    Text_Message = TextSendMessage(
        text='Send location information',
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(action=LocationAction(label="Choose a location"))
            ]
       )
    )
    return Text_Message
#========================================
#?????? reply_Hospital ?????????????????? db_type ?????????????????????????????????
# ?????????????????????????????????key???????????????????????????????????? db_type ?????????key?????????
#========================================
def confirm_db_type(my_Hospital):
    global db_type, hs_Name, name, address, text_error, Org_species, Vs_time, db_type_name, Treatment_type

    if my_Hospital["db_type"] == "District_hp_db":
        hs_Name = 'Name'
        address = "Address"
        name = "??????"
        Vs_time = "??????????????????"
        Org_species = "facility type"
        Treatment_type = "Medical Specialty"

    elif my_Hospital["db_type"] == "Regional_hp_db":
        name = "??????"
        hs_Name = 'Name'
        address = "Address"
        Vs_time = "??????????????????"
        Org_species = "facility type"
        Treatment_type = "Medical Specialty"

    elif my_Hospital["db_type"] == "clinic_hp_db":
        name = "??????"
        hs_Name = 'Name'
        address = "Address"
        Vs_time = "??????????????????"
        Org_species = "facility type"
        Treatment_type = "Medical Specialty"

    elif my_Hospital["db_type"] == "medicine_hp_db":
        name = "??????"
        hs_Name = 'Name'
        address = "Address"
        Vs_time = "??????????????????"
        Org_species = "facility type"
        Treatment_type = "Medical Specialty"

    elif my_Hospital["db_type"] == "pharmacy_hp_db":
        name = "??????"
        hs_Name = 'Name'
        address = "Address"
        Vs_time = "??????????????????"
        Org_species = "facility type"
        Treatment_type = "Medical Specialty"

    else:
        raise NameError("Error address_type name")

def reply_Hospital(my_Hospital):
    contents = dict()
    contents['type'] = 'carousel'
    bubbles = []

    if my_Hospital == []:  #???????????????????????????????????????????????????????????? return message
        message = TextSendMessage(text="Not yet joined the hospital")
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
                                        text=i["??????"],
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
                                label="Phone Number",
                                text=i["??????"] + "\n" + i[hs_Name])
                            ),
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=PostbackAction(
                                label='Consultation time',
                                display_text='Consultation period',
                                data="action=time,{hs_Name},{Vs_time}"
                                    .format(hs_Name=i[hs_Name], Vs_time=i[Vs_time])
                            )
                            ),
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=URIAction(
                                label="Navigation destination",
                                uri='https://www.google.com/maps/search/?api=1&query={lat},{long}'.format(
                                    lat=i["??????E"], long=i["??????N"])),
                            ),
                            SeparatorComponent(
                                color="#CCCCCCFF"
                            ),
                            ButtonComponent(action=PostbackAction(
                                label='Removed from my hospital',
                                display_text='{hs_Name} has been removed from my hospital'.format(hs_Name=i[hs_Name]),
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
    message = FlexSendMessage(alt_text='????????????', contents=carousel_contaimer)
    return message
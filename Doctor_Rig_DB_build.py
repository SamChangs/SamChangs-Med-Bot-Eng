# -*- coding: utf-8 -*-
from pymongo import MongoClient
import pymongo
import urllib.parse
from datetime import datetime 
import xlrd



# =============================================================================
#                                 醫生掛號資料庫資訊
# =============================================================================

client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
#client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
##### 切換資料庫DoctorInfo #####
Authdb='KMSH-bot'
db = client[Authdb]
collid='DoctorInfo'
coll = db[collid]
# =============================================================================
# OPEN EXCEL
# =============================================================================
filename = 'doctor.xlsx'
book = xlrd.open_workbook(filename)
sheel_1 = book.sheet_by_index(0)
i=1

for i in range (1,181):
    c_name = sheel_1.cell_value(i,0).rstrip()
    pno = sheel_1.cell_value(i,2).rstrip()
    dept_code = sheel_1.cell_value(i,3).rstrip()    
    DocNo = sheel_1.cell_value(i,12).rstrip()
    DeptNo = sheel_1.cell_value(i,13).rstrip()
    Doc_info={'c_name':c_name,'pno':pno,'dept_code':dept_code,'DocNo':DocNo,'DeptNo':DeptNo,'creat_time':datetime.now()}
    coll.insert_one(Doc_info)

client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
#client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')


################################################ 切換資料庫 DoctorIntro####################
Authdb='KMSH-bot'
db = client[Authdb]
collid='DoctorIntro'
coll = db[collid] 
filename = 'doctor.xlsx'
book = xlrd.open_workbook(filename)
sheel_1 = book.sheet_by_index(0)

i=1   
for i in range (1,181):
    c_name = sheel_1.cell_value(i,0).rstrip()
    position = sheel_1.cell_value(i,5).rstrip()
    degree = sheel_1.cell_value(i,6).rstrip()    
    med_train = sheel_1.cell_value(i,7).rstrip()
    clinic_spec = sheel_1.cell_value(i,8).rstrip()
    licen = sheel_1.cell_value(i,9).rstrip()
    acad_pos= sheel_1.cell_value(i,10).rstrip()
    clinic=sheel_1.cell_value(i,11).rstrip()
    Doc_info={'c_name':c_name,'position':position,'degree':degree,'med_train':med_train,'clinic_spec':clinic_spec,'licen':licen,'acad_pos':acad_pos,'clinic':clinic,'creat_time':datetime.now()}
    
    coll.insert_one(Doc_info)    

###############################################################################
#                      上傳股市產業類別                    #
###############################################################################

##### 發出請求 #####
client = MongoClient('mongodb://stockrobot:tp6w94xu;6@cluster0-shard-00-00-yujl6.mongodb.net:27017,cluster0-shard-00-01-yujl6.mongodb.net:27017,cluster0-shard-00-02-yujl6.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
##### 切換資料庫 #####
dbname='StockDB'
db = client[dbname]

##### stock info collection #####
collid='marketinfo'  
coll = db[collid]               
                                      
market_info=[{'market_cass':'上市','stock_cass':'水泥工業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'化學工業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'半導體業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'貿易百貨業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'生技醫療業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'光電業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'汽車工業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'其他業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'其他電子業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'油電燃氣業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'金融保險業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'建材營造業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'玻璃陶瓷','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'食品工業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'紡織纖維','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'航運業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'造紙工業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'通信網路業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'資訊服務業','creat_time':datetime.now()},
              {'market_cass':'上市','stock_cass':'電子通路業','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'電子零組件業','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'電腦及週邊設備業','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'電器電纜','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'電機機械','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'橡膠工業','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'鋼鐵工業','creat_time':datetime.now()},
               {'market_cass':'上市','stock_cass':'觀光事業','creat_time':datetime.now()},
             {'market_cass':'上市','stock_cass':'塑膠工業','creat_time':datetime.now()}]
coll.insert_many(market_info)

# =============================================================================
# 
# =============================================================================


##### 注意下方的 coll 自己命名 #####
coll = db[collid]

stock_info={'stock_id':'1477','stock_name':'聚陽','stock_cass':'紡織纖維','creat_time':datetime.now()}
coll.insert_one(stock_info)


##### 轉成list #####

stock_info1 = [{'stock_id':'2301','stock_name':'光寶科','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2302','stock_name':'麗正','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2303','stock_name':'聯電','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2305','stock_name':'全友','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2308','stock_name':'台達電子','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2310','stock_name':'旭麗','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2311','stock_name':'日月光','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2312','stock_name':'金寶','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2313','stock_name':'華通','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2314','stock_name':'台揚','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2315','stock_name':'神達','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2316','stock_name':'楠梓電子','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2317','stock_name':'鴻海','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2318','stock_name':'佳錄','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2319','stock_name':'大眾','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2321','stock_name':'東訊','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2322','stock_name':'致福','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2323','stock_name':'中環','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2324','stock_name':'仁寶','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2325','stock_name':'矽品','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2326','stock_name':'亞瑟','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2327','stock_name':'國巨','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2328','stock_name':'廣宇','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2329','stock_name':'華泰','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2330','stock_name':'台積電','stock_cass':'資訊電子','creat_time':datetime.now()}
               ]
coll.insert_many(stock_info1)

stock_info2 = [{'stock_id':'2331','stock_name':'精英','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2332','stock_name':'友訊','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2333','stock_name':'碧悠','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2335','stock_name':'清三','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2336','stock_name':'致伸','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2337','stock_name':'旺宏','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2338','stock_name':'光罩','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2339','stock_name':'合泰','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2340','stock_name':'光磊','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2341','stock_name':'英群','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2342','stock_name':'茂矽','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2343','stock_name':'精業','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2344','stock_name':'華邦電子','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2345','stock_name':'智邦','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2347','stock_name':'聯強','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2348','stock_name':'力捷','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2349','stock_name':'錸德','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2350','stock_name':'環電','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2351','stock_name':'順德','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2352','stock_name':'明基','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2353','stock_name':'宏碁','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2354','stock_name':'華升','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2355','stock_name':'敬鵬','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2356','stock_name':'英業達','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2357','stock_name':'華碩','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2358','stock_name':'美格','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2359','stock_name':'所羅門','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2360','stock_name':'致茂','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2361','stock_name':'鴻友','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2362','stock_name':'藍天','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2363','stock_name':'矽統','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2364','stock_name':'倫飛','stock_cass':'資訊電子','creat_time':datetime.now()},
               {'stock_id':'2365','stock_name':'昆盈','stock_cass':'資訊電子','creat_time':datetime.now()}
               ]


coll.insert_many(stock_info2)

# =============================================================================
# 刪除特定股票ID
# =============================================================================

coll.delete_one({'stock_id':'1337'})




# =============================================================================
# 
# =============================================================================

usespeak='2330'

A = list(coll.find({'stock_id':usespeak}))
stock_name_q = A[0]['stock_name']

usespeak='台積電'
B = list(coll.find({'stock_name':usespeak}))
stock_id_q = B[0]['stock_id']




# =============================================================================
#    mongoDB資料庫操作教學
# =============================================================================
##### 插入 多行 #####
dic_list = [{'userid':'nrt345iofqnjwengtgg4387',
           'username':'jarry',
           'creattime':datetime.now(),
           'Note':'testuser'},
            {'userid':'jei45646hop4454op12387',
           'username':'ketio',
           'creattime':datetime.now(),
           'Note':'testuser'},
            {'userid':'rgmmemroemrm37237y4',
           'username':'zino',
           'creattime':datetime.strptime('2018-05-30 16:20:06',
                                         '%Y-%m-%d %H:%M:%S'), #輸入特定時間格式，轉字串
           'Note':'testuser'}]

coll.insert_many(dic_list)

##### 根據時間選擇 #####
start = datetime.strptime('2018-04-30 16:20:06',
                           '%Y-%m-%d %H:%M:%S')
end = datetime.strptime('2018-06-30 16:20:06',
                           '%Y-%m-%d %H:%M:%S')
list(coll.find({'creattime': {'$gte': start, '$lt': end}}))

A=list(coll.find({'stock_cass':'塑膠'}))

##### 針對特殊id 抓取 #####
from bson.objectid import ObjectId
list(coll.find({'_id':ObjectId('5bf2515d63d7d502d05b1b53')}))

##### 根據條件 整個取代 #####
coll.update({'username':'jarry'} ,
             {'Note':'updateuser'})

##### 根據條件 指取代其中一個 #####
coll.update({'stock_cass':'塑膠'},
            {'$set':{'stock_cass':'塑膠工業'}}) 



##### 移除單個 #####
coll.delete_one({'username':'ketio'})

##### 移除多個 #####
coll.delete_many({'Note':'testuser'}) 
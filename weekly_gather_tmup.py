from Apis import xasession
from Apis.xaquery import *
import time
import pandas as pd
import sqlite3
import pythoncom
import sys
import datetime
import telegram

def Waiting():
    start_time = time.time()
    while XAQueryEvents.status == False:
        if time.time() - start_time >= 10:
            break
        else: 
            pythoncom.PumpWaitingMessages()


bot = telegram.Bot(token = '888304273:AAFE-VXdeXDyJpDvCqvTz5GdjKzVaJ_P28M')
chatid = '821788432'

#
now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
message = 'weekly_gather_tm&up Start ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#
session = xasession.Session()
session.login(True)
#
bot.sendMessage(chat_id=chatid, text='로그인완료')
#


'''t8424_업종전체조회 시작'''
query = t8424()
query.Query(구분= '')
Waiting()
upcode_list = query.GetResult()

now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
upcode_list['적재일시'] = now_time

with sqlite3.connect('t8424.db') as conn:
    upcode_list.to_sql('업종코드', con=conn, if_exists='replace', index=False)
conn.close()

#
bot.sendMessage(chat_id=chatid, text='t8424_업종전체조회_적재완료')
#

#t1516

table_name = 't1516' +'.db'
with sqlite3.connect(table_name) as conn:

    for i in upcode_list['업종코드']:
        time.sleep(0.1)
        query = t1516()
        time.sleep(3)
        query.Query(업종코드=i)
        Waiting()
        df = query.GetResult()
        if df.shape[0] == 0:
            continue
        df = pd.DataFrame(df)
        data = DataFrame([], columns= ['종목명','현재가','전일대비구분','전일대비','등락율','누적거래량','시가','고가','저가','소진율','베타계수','PER','외인순매수','기관순매수','거래증가율','종목코드','시가총액','거래대금'])
        data = data.append(df)

        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)

        data['업종코드'] = i
        data['일자'] = today
        data.to_sql('업종별종목코드', con=conn, if_exists='append', index=False)
        print('t1516_업종별종목코드 : %s ----------- %s 적재완료' %(now_time, i))

conn.close()

#
bot.sendMessage(chat_id=chatid, text='t1516_업종별종목코드_적재완료')
#


'''t8425_전체테마조회 시작'''
query = t8425()
query.Query()
Waiting()
thema_list = query.GetResult()

now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
thema_list['적재일시'] = now_time

with sqlite3.connect('t8425.db') as conn:
    thema_list.to_sql('테마코드', con=conn, if_exists='replace', index=False)
conn.close()

#
bot.sendMessage(chat_id=chatid, text='t8425_전체테마조회_적재완료')
#

#t1537
table_name = 't1537' +'.db'
with sqlite3.connect(table_name) as conn:

    for i in thema_list['테마코드']:
        time.sleep(0.1)
        query = t1537()
        time.sleep(3)
        query.Query(테마코드=i)
        Waiting()
        df = query.GetResult()
        if df.shape[0] == 0:
            continue
        df = pd.DataFrame(df)
        data = DataFrame([], columns= ['종목명', '현재가', '전일대비구분', '전일대비', '등락율', '누적거래량', '전일동시간', '종목코드', '예상체결가', '시가', '고가', '저가',
                        '누적거래대금', '시가총액'])
        data = data.append(df)

        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)

        data['테마코드'] = i
        data['일자'] = today
        data.to_sql('테마별종목코드', con=conn, if_exists='append', index=False)
        print('t1537_테마별종목코드 : %s ----------- %s 적재완료' %(now_time, i))

conn.close()

#
bot.sendMessage(chat_id=chatid, text='t1537_테마별종목코드_적재완료')
#


#
now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
message = 'weekly_gather_tm&up End ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#

session.logout()
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
    while XAQueryEvents.status == False:
        pythoncom.PumpWaitingMessages()


bot = telegram.Bot(token = '888304273:AAFE-VXdeXDyJpDvCqvTz5GdjKzVaJ_P28M')
chatid = '821788432'
#
now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
message = 'daily_gather_t1305 Start ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#

session = xasession.Session()
session.login(True)

#
bot.sendMessage(chat_id=chatid, text='로그인완료')
#
query = t8430()
query.Query(구분= '0')
Waiting()
shcode_list = query.GetResult()

now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
shcode_list['적재일시'] = now_time

with sqlite3.connect('t8430.db') as conn:
    shcode_list.to_sql('종목코드', con=conn, if_exists='replace', index=False)

conn.close()

#
bot.sendMessage(chat_id=chatid, text='t8430_적재완료')
#

for i in shcode_list['종목코드']:
    time.sleep(0.1)
    query = t1305()
    time.sleep(3)
    query.Query(종목코드=i, 일주월구분='1', 날짜='',IDX='', 건수='1', 연속조회 = False)
    Waiting()
    df = query.GetResult()
    data = DataFrame([], columns= ['일자','시가','고가','저가','종가','전일대비구분','전일대비','등락율'
                                    ,'누적거래량','거래증가율','체결강도','소진율','회전율','외인순매수'
                                    ,'기관순매수','종목코드','누적거래대금','개인순매수','시가대비구분'
                                    ,'시가대비','시가기준등락율','고가대비구분','고가대비','고가기준등락율'
                                    ,'저가대비구분','저가대비','저가기준등락율','시가총액'])            
    data = data.append(df)
    data['종목코드'] = i
    table_name = 't1305' +'.db'
    with sqlite3.connect(table_name) as conn:
        data.to_sql('종목별체결조회', con=conn, if_exists='append', index=False)
            
    now = datetime.datetime.now()
    now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)

    print('t1305_종목별체결조회 : %s ----------- %s 적재완료' %(now_time, i))

conn.close()

#
now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
message = 'daily_gather_t1305 End ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#

session.logout()
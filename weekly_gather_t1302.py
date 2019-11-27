from Apis import xasession
from Apis.xaquery import *
import time
import pandas as pd
import sqlite3
import pythoncom
import sys
import datetime


def Waiting():
    while XAQueryEvents.status == False:
        pythoncom.PumpWaitingMessages()

session = xasession.Session()
session.login(True)



table_name = 't1302_10m' +'.db'

with sqlite3.connect(table_name) as conn:
    for i in shcode_list['종목코드']:
        time.sleep(0.1)
        query = t1305()
        time.sleep(2.91)
        query.Query(종목코드=i, 일주월구분='1', 날짜='',IDX='', 건수='300', 연속조회 = False)
        Waiting()
        df = query.GetResult()
        data = DataFrame([], columns= ['시간', '종가', '전일대비구분', '전일대비', '등락율', '체결강도',
                        '매도체결수량', '매수체결수량', '순매수체결량', '매도체결건수', '매수체결건수',
                        '순체결건수', '거래량', '시가', '고가', '저가', '체결량', '매도체결건수시간', 
                        '매수체결건수시간', '매도잔량', '매수잔량', '시간별매도체결량',
                        '시간별매수체결량']))            
        data = data.append(df)
        data['종목코드'] = i
        data.to_sql('종목별체결조회', con=conn, if_exists='append', index=False)
        now = datetime.datetime.now()
        now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
        print('t1302_10m_종목별체결조회 : %s ----------- %s 적재완료' %(now_time, i))
conn.close()

#
now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
message = 'weekly_gather_t1302_10m End ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#

session.logout()
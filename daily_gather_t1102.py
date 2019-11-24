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
message = 'daily_gather_t1102 Start ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#

session = xasession.Session()
session.login(True)

#
bot.sendMessage(chat_id=chatid, text='로그인완료')
#

'''t8430_주식종목코드 시작'''
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
bot.sendMessage(chat_id=chatid, text='t8430_주식종목코드_적재완료')
#


'''t1102'''
table_name = 't1102' +'.db'
with sqlite3.connect(table_name) as conn:

    for i in shcode_list['종목코드']:
        time.sleep(0.3)
        query = t1102()
        query.Query(종목코드=i)
        Waiting()
        df = query.GetResult()
        if df.shape[0] == 0:
            continue
        df = pd.DataFrame(df).transpose()
        data = DataFrame([], columns= ['한글명','현재가','전일대비구분','전일대비','등락율','누적거래량',
                                        '기준가_평가가격','가중평균','상한가_최고호가가격','하한가_최저호가가격',
                                        '전일거래량','거래량차','시가','시가시간','고가','고가시간','저가','저가시간',
                                        '최고가_52','최고가일_52','최저가_52','최저가일_52','소진율','PER','PBRX',
                                        '상장주식수_천','증거금율','수량단위','매도증권사코드1','매수증권사코드1',
                                        '매도증권사명1','매수증권사명1','총매도수량1','총매수수량1','매도증감1','매수증감1',
                                        '매도비율1','매수비율1','매도증권사코드2','매수증권사코드2',
                                        '매도증권사명2','매수증권사명2','총매도수량2','총매수수량2',
                                        '매도증감2','매수증감2','매도비율2','매수비율2','매도증권사코드3',
                                        '매수증권사코드3','매도증권사명3','매수증권사명3','총매도수량3',
                                        '총매수수량3','매도증감3','매수증감3','매도비율3','매수비율3',
                                        '매도증권사코드4','매수증권사코드4','매도증권사명4','매수증권사명4',
                                        '총매도수량4','총매수수량4','매도증감4','매수증감4','매도비율4',
                                        '매수비율4','매도증권사코드5','매수증권사코드5','매도증권사명5','매수증권사명5',
                                        '총매도수량5','총매수수량5','매도증감5','매수증감5','매도비율5','매수비율5',
                                        '외국계매도합계수량','외국계매도직전대비','외국계매도비율','외국계매수합계수량',
                                        '외국계매수직전대비','외국계매수비율','회전율','종목코드','누적거래대금',
                                        '전일동시간거래량','연중최고가','연중최고일자','연중최저가','연중최저일자',
                                        '목표가','자본금','유동주식수','액면가','결산월','대용가','시가총액',
                                        '상장일','전분기명','전분기매출액','전분기영업이익','전분기경상이익',
                                        '전분기순이익','전분기EPS','전전분기명','전전분기매출액',
                                        '전전분기영업이익','전전분기경상이익','전전분기순이익','전전분기EPS','전년대비매출액',
                                        '전년대비영업이익','전년대비경상이익','전년대비순이익','전년대비EPS','락구분',
                                        '관리_급등구분','정지_연장구분','투자_불성실구분','장구분','TPER','통화ISO코드',
                                        '총매도대금1','총매수대금1','총매도대금2','총매수대금2','총매도대금3','총매수대금3',
                                        '총매도대금4','총매수대금4','총매도대금5','총매수대금5','총매도평단가1','총매수평단가1',
                                        '총매도평단가2','총매수평단가2','총매도평단가3','총매수평단가3','총매도평단가4',
                                        '총매수평단가4','총매도평단가5','총매수평단가5','외국계매도대금','외국계매수대금',
                                        '외국계매도평단가','외국계매수평단가','투자주의환기','기업인수목적회사여부',
                                        '발행가격','배분적용구분코드','배분적용구분','단기과열_VI발동','정적VI상한가',
                                        '정적VI하한가','저유동성종목여부','이상급등종목여부','대차불가표시'])            
        data = data.append(df)
        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
        data['종목코드'] = i
        data['일자'] = today
        data.to_sql('종목별체결조회', con=conn, if_exists='append', index=False)
        print('t1102_종목별체결조회 : %s ----------- %s 적재완료' %(now_time, i))

conn.close()

#
bot.sendMessage(chat_id=chatid, text='t1102_종목별체결조회_적재완료')
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
'''
#t1516

table_name = 't1516' +'.db'
with sqlite3.connect(table_name) as conn:

    for i in upcode_list['업종코드'].iloc[:2]:
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
'''

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
'''
#t1537
table_name = 't1537' +'.db'
with sqlite3.connect(table_name) as conn:

    for i in thema_list['테마코드'].iloc[:2]:
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
'''

#
now = datetime.datetime.now()
now_time = '%s-%s-%s_%s:%s:%s' % ( now.year, now.month, now.day, now.hour, now.minute, now.second)
message = 'daily_gather_t1102_2 End ' + ' : ' + now_time
bot.sendMessage(chat_id=chatid, text=message)
#

session.logout()
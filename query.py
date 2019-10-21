import numpy as np
import pandas as pd
import datetime
import sqlite3



#0.종목코드열람
def query_shcode_list_today():
    conn = sqlite3.connect("t8430.db")
    cur = conn.cursor()
    query = "select distinct 종목명, 종목코드 \
            from 종목코드 ;"
            #where 종목코드 = '%s'; " % '000020'
    cur.execute(query)
    rows = cur.fetchall()
    shcode_list = pd.DataFrame(rows, columns = ['shname', 'shcode'])
    conn.close()
    return shcode_list



today = type(datetime.datetime.now().strftime("%Y%m%d"))

#1.시세데이터 뽑기_t1305

def query_ohlcv(shcode, fr = '20190101',to = today):
    
    conn = sqlite3.connect("t1305_1.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' \
            and 일주월구분 = '%s' ;" % (fr,to,shcode,'1')
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result, columns = ['date', 'open', 'high', 'low', 'close', 'volume'])
    daily = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return daily
    
def query_ohlcv_month(shcode, to = '20190101'):
    
    conn = sqlite3.connect("t1305_3.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            from 종목별체결조회 \
            where 1=1 \
            and 일자 <= '%s' \
            and 종목코드 = '%s' \
            ;" % (to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result, columns = ['date', 'open', 'high', 'low', 'close', 'volume'])
    monthly = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return monthly
    

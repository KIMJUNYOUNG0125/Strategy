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



today = datetime.datetime.now().strftime("%Y%m%d")

#1.시세데이터 뽑기_t1305_1

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
    
#2 기타정보뽑기 t1305_1

def query_t1305(shcode, fr = '20190101',to = today):
    
    conn = sqlite3.connect("t1305_1.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            , 체결강도,  소진율, 회전율, 외인순매수, 기관순매수, 개인순매수\
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' \
            and 일주월구분 = '%s' ;" % (fr,to,shcode,'1')
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'open', 'high', 'low', 'close', 'volume',
                                        'deal_f','burn_ratio','rotate_ratio','for_net_buy','com_net_buy','per_net_buy'])
    daily = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return daily
    
#1.시세데이터 뽑기_t1305_3

def query_ohlcv_month(shcode, to = today):
    
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
    

#2 기타정보뽑기 t1305_3
def query_t1305_month(shcode, to = today):
    
    conn = sqlite3.connect("t1305_3.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            , 체결강도,  소진율, 회전율, 외인순매수, 기관순매수, 개인순매수\
            from 종목별체결조회 \
            where 1=1 \
            and 일자 <= '%s' \
            and 종목코드 = '%s' \
            ;" % (to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'open', 'high', 'low', 'close', 'volume',
                                        'deal_f','burn_ratio','rotate_ratio','for_net_buy','com_net_buy','per_net_buy'])
    monthly = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return monthly
    
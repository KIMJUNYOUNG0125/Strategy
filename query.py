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


#1 일봉
#1-1.시세데이터 뽑기_t1305_1

def query_ohlcv(shcode, fr = '20190101',to = today):
    
    conn = sqlite3.connect("t1305_1.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result, columns = ['date', 'open', 'high', 'low', 'close', 'volume'])
    daily = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return daily
    
#1-2 기타정보뽑기 t1305_1

def query_t1305(shcode, fr = '20190101',to = today):
    
    conn = sqlite3.connect("t1305_1.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            , 체결강도,  소진율, 회전율, 외인순매수, 기관순매수, 개인순매수\
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'open', 'high', 'low', 'close', 'volume',
                                        'deal_f','burn_ratio','rotate_ratio','for_net_buy','com_net_buy','per_net_buy'])
    daily = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return daily
    

#2 주봉
#2-1.시세데이터 뽑기_t1305_2

def query_ohlcv_week(shcode, fr = '20180101', to = today):
    
    conn = sqlite3.connect("t1305_2.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result, columns = ['date', 'open', 'high', 'low', 'close', 'volume'])
    weekly = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return weekly
    

#2-2 기타정보뽑기 t1305_2
def query_t1305_week(shcode, fr = '20180101', to = today):
    
    conn = sqlite3.connect("t1305_2.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            , 체결강도,  소진율, 회전율, 외인순매수, 기관순매수, 개인순매수\
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'open', 'high', 'low', 'close', 'volume',
                                        'deal_f','burn_ratio','rotate_ratio','for_net_buy','com_net_buy','per_net_buy'])
    weekly = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return weekly


#3 월봉
#3-1.시세데이터 뽑기_t1305_3

def query_ohlcv_month(shcode, fr = '20180101', to = today):
    
    conn = sqlite3.connect("t1305_3.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result, columns = ['date', 'open', 'high', 'low', 'close', 'volume'])
    monthly = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return monthly
    

#3-2 기타정보뽑기 t1305_3
def query_t1305_month(shcode, fr = '20180101', to = today):
    
    conn = sqlite3.connect("t1305_3.db")
    cur = conn.cursor()
    query = "select 일자, 시가, 고가, 저가, 종가, 누적거래량 \
            , 체결강도,  소진율, 회전율, 외인순매수, 기관순매수, 개인순매수\
            from 종목별체결조회 \
            where 1=1 \
            and 일자 between '%s' and '%s' \
            and 종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'open', 'high', 'low', 'close', 'volume',
                                        'deal_f','burn_ratio','rotate_ratio','for_net_buy','com_net_buy','per_net_buy'])
    monthly = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return monthly


#4. 대표업종 추출
def query_up_distinct():
    
    conn = sqlite3.connect("t1516.db")
    cur = conn.cursor()
    query = "select distinct     max(일자) as 일자, min(CAST(업종코드 AS INT)) as 업종코드, 업종명, 종목코드, 현재가, 시가총액, 거래대금, PER \
            from                업종별종목코드 \
            where               1=1 \
            group by            종목코드, 현재가, 시가총액, 거래대금, PER \
            ;"
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'upcode', 'upname', 'shcode', 'now_p', 'total_value', 'trans_money', 'per'])
    fin_result = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return fin_result

#5. 대표테마 추출
def query_tm_distinct():
    
    conn = sqlite3.connect("t1537.db")
    cur = conn.cursor()
    query = "select distinct    max(일자) as 일자, max(CAST(테마코드 AS INT)) as 테마코드, 테마명, 종목코드, 종목명, 현재가, 시가총액\
            from                테마별종목코드 \
            where               1=1 \
            group by            종목코드, 종목명, 현재가, 시가총액 \
            ;"
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'tmcode', 'tmname', 'shcode', 'shname','now_p', 'total_value'])
    fin_result = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return fin_result


#6. 투자자별동향 추출
def query_jupo(shcode, fr = '2010101', to = today):
    
    conn = sqlite3.connect("t1717.db")
    cur = conn.cursor()
    query = "select     일자, 종목코드, 종가, 사모펀드_순매수, 증권_순매수, 보험_순매수, 투신_순매수, 은행_순매수,\
                        종금_순매수, 기금_순매수, 기타법인_순매수, 개인_순매수, 등록외국인_순매수, \
                        미등록외국인_순매수, 국가외_순매수, 기관_순매수, 외인계_순매수, 기타계_순매수, \
                        사모펀드_단가, 증권_단가, 보험_단가, 투신_단가, 은행_단가,\
                        종금_단가, 기금_단가, 기타법인_단가, 개인_단가, 등록외국인_단가, \
                        미등록외국인_단가, 국가외_단가, 기관_단가, 외인계_단가, 기타계_단가 \
            from        투자자별동향 \
            where       1=1 \
            and         일자 between '%s' and '%s' \
            and         종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'shcode', 'close',  
                                        'samo_vol', 'sec_vol', 'ins_vol', 'tusin_vol', 'bank_vol',
                                        'jong_vol', 'fund_vol', 'etcom_vol', 'per_vol', 'for_reg_vol',
                                        'for_noreg_vol', 'nat_no_vol', 'com_vol', 'for_vol', 'etc_vol',
                                        'samo_dan', 'sec_dan', 'ins_dan', 'tusin_dan', 'bank_dan',
                                        'jong_dan', 'fund_dan', 'etcom_dan', 'per_dan', 'for_reg_dan',
                                        'for_noreg_dan', 'nat_no_dan', 'com_dan', 'for_dan', 'etc_dan'])
    fin_result = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return fin_result

#6-1. 수량

def query_jupo_vol(shcode, fr = '2010101', to = today):
    
    conn = sqlite3.connect("t1717.db")
    cur = conn.cursor()
    query = "select     일자, 종목코드, 종가, 사모펀드_순매수, 증권_순매수, 보험_순매수, 투신_순매수, 은행_순매수,\
                        종금_순매수, 기금_순매수, 기타법인_순매수, 개인_순매수, 등록외국인_순매수, \
                        미등록외국인_순매수, 국가외_순매수, 기관_순매수, 외인계_순매수, 기타계_순매수\
            from        투자자별동향 \
            where       1=1 \
            and         일자 between '%s' and '%s' \
            and         종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'shcode', 'close',  
                                        'samo_vol', 'sec_vol', 'ins_vol', 'tusin_vol', 'bank_vol',
                                        'jong_vol', 'fund_vol', 'etcom_vol', 'per_vol', 'for_reg_vol',
                                        'for_noreg_vol', 'nat_no_vol', 'com_vol', 'for_vol', 'etc_vol'])
    fin_result = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return fin_result


#6-2. 단가

def query_jupo_dan(shcode, fr = '2010101', to = today):
    
    conn = sqlite3.connect("t1717.db")
    cur = conn.cursor()
    query = "select     일자, 종목코드, 종가, \
                        사모펀드_단가, 증권_단가, 보험_단가, 투신_단가, 은행_단가,\
                        종금_단가, 기금_단가, 기타법인_단가, 개인_단가, 등록외국인_단가, \
                        미등록외국인_단가, 국가외_단가, 기관_단가, 외인계_단가, 기타계_단가 \
            from        투자자별동향 \
            where       1=1 \
            and         일자 between '%s' and '%s' \
            and         종목코드 = '%s' \
            ;" % (fr,to,shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'shcode', 'close',  
                                        'samo_dan', 'sec_dan', 'ins_dan', 'tusin_dan', 'bank_dan',
                                        'jong_dan', 'fund_dan', 'etcom_dan', 'per_dan', 'for_reg_dan',
                                        'for_noreg_dan', 'nat_no_dan', 'com_dan', 'for_dan', 'etc_dan'])
    fin_result = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return fin_result


#7. 기타재무정보


def query_finance(shcode):
    
    conn = sqlite3.connect("t1102.db")
    cur = conn.cursor()
    query = "select     일자, 종목코드, 시가, 누적거래량, 누적거래대금,\
                        최고가_52, 최고가일_52, 최저가_52, 최저가일_52, 소진율, 회전율, PER,\
                        상장주식수_천, 증거금율, 수량단위, 시가총액\
            from        종목별체결조회 \
            where       1=1 \
            and         종목코드 = '%s' \
            ;"          % (shcode)
    cur.execute(query)
    query_result = cur.fetchall()
    fin_result = pd.DataFrame(query_result,
                                columns = ['date', 'shcode', 'close', 'volume', 'volume_money',
                                'high_52', 'high_52_day', 'high_52', 'high_52_day', 'rotate_ratio','burn_ratio', 'per',
                                'total_vol', 'ev_ratio', 'vol_scale', 'market_value'])
    fin_result = fin_result.sort_values(by = ['date']).reset_index(drop = True)
    conn.close()
    return fin_result
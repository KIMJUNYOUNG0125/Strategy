import talib
import numpy as np
import pandas as pd


'''
1.이동평균선

'sma_5_ratio', 'sma_10_ratio','sma_20_ratio','sma_60_ratio', 'sma_120_ratio'

'''

def sma(df):

    windows_sma = [5,10,20,60]
    for window in windows_sma:
        df['close_ma%d'% window] = talib.SMA(np.asarray(df['close'], dtype = 'f8'), window)
        #df['sma_%d_ratio'% window] = df['close'] / df['sma%d' % window]
    return df

def marking_cross_sma(df):
    
    prev_close_ma5 = df['close_ma5'].shift(1)
    prev_close_ma20 = df['close_ma20'].shift(1)
    
    golden_cross = np.where(((df['close_ma5'] >= df['close_ma20']) & (prev_close_ma5 <= prev_close_ma20)),df['close_ma5'],None)
    dead_cross = np.where(((df['close_ma5'] <= df['close_ma20']) & (prev_close_ma5 >= prev_close_ma20)),df['close_ma5'],None)

    df['ma_g_c'] = golden_cross
    df['ma_d_c'] = dead_cross
    
    return df

'''
2.거래량

'volume_ma5_ratio','volume_ma10_ratio', 'volume_ma20_ratio', 'volume_ma60_ratio', 'volume_ma120_ratio'
'''
def vma(df):
    windows_vol = [5,10,20,60]
    for window in windows_vol:
        df['volume_ma%d'% window] = talib.SMA(np.asarray(df['volume'], dtype = 'f8'), window)
        #df['volume_ma%d_ratio'% window] = df['volume'] / df['volume%d' % window]
    return df



'''
4.rsi구하기

'rsi14_sign' , 'rsi14_signal_ratio'
'''
def rsi(df):
    df['rsi14'] = talib.RSI(np.asarray(df['close'], dtype = 'f8'),14)
    #df['rsi14_sign'] = np.where(df['rsi14'] < 0.3 ,1 ,
    #                        np.where(df['rsi14'] > 0.7 , -1, 0))
    df['rsi14_signal'] = df['rsi14'].rolling(window=6).mean()
    #df['rsi14_signal_ratio'] = df['rsi14'] / df['rsi14_signal']
    return df

def marking_cross_rsi(df):
    
    prev_close_rsi14 = df['rsi14'].shift(1)
    prev_close_rsi14_signal = df['rsi14_signal'].shift(1)
    
    golden_cross = np.where(((df['rsi14'] >= df['rsi14_signal']) & (prev_close_rsi14 <= prev_close_rsi14_signal)),df['rsi14'],None)
    dead_cross = np.where(((df['rsi14'] <= df['rsi14_signal']) & (prev_close_rsi14 >= prev_close_rsi14_signal)),df['rsi14'],None)

    df['rsi_g_c'] = golden_cross
    df['rsi_d_c'] = dead_cross
    
    return df

'''
6.macd

'macd_signal_ratio'
'''

#이동평균 컨버전스/ 다이버전스
def macd(df):
    df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(np.asarray(df['close'], dtype = 'f8'),12,26,9)
    #df['macd_signal_ratio'] = df['macd'] / df['macd_signal']
    return df

def marking_cross_macd(df):
    
    prev_close_macd = df['macd'].shift(1)
    prev_close_macdsignal = df['macdsignal'].shift(1)
    
    golden_cross = np.where(((df['macd'] >= df['macdsignal']) & (prev_close_macd <= prev_close_macdsignal)),df['macd'],None)
    dead_cross = np.where(((df['macd'] <= df['macdsignal']) & (prev_close_macd >= prev_close_macdsignal)),df['macd'],None)

    df['macd_g_c'] = golden_cross
    df['macd_d_c'] = dead_cross
    
    return df



'''
8. Stochastic slow

'''
def stochastic(df):
    df['slowk'], df['slowd'] = talib.STOCH(high = np.asarray(df['high'], dtype = 'f8'),
                                            low = np.asarray(df['low'], dtype = 'f8'),
                                            close = np.asarray(df['close'], dtype = 'f8'),
                                            fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    return df

def marking_cross_stochastic(df):
    
    prev_close_slowk = df['slowk'].shift(1)
    prev_close_slowd = df['slowd'].shift(1)
    
    golden_cross = np.where(((df['slowk'] >= df['slowd']) & (prev_close_slowk <= prev_close_slowd)),df['slowk'],None)
    dead_cross = np.where(((df['slowk'] <= df['slowd']) & (prev_close_slowk >= prev_close_slowd)),df['slowk'],None)

    df['stoc_g_c'] = golden_cross
    df['stoc_d_c'] = dead_cross
    
    return df



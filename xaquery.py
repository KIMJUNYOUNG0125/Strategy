import pythoncom
import win32com.client
import datetime
import time
from Apis import xacom
from logger import Logger
from pandas import DataFrame, Series, Panel

log = Logger(__name__)

class XAQueryEvents(object):
    status = False

    def __init__(self):
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def OnReceiveMessage(self, systemError, messageCode, message):
        self.code = str(messageCode)
        self.msg = str(message)
        if self.code != "00000":
            log.debug(" - [%s:%s] OnReceiveMessage" % (self.code, self.msg))
        pass

    def OnReceiveData(self, szTrCode):
        if self.parent != None:
            self.parent.OnReceiveData(szTrCode)
        log.info(" - [%s:%s] OnReceiveData" % (szTrCode, xacom.parseTR(szTrCode)))
        XAQueryEvents.status = True


    def OnReceiveChartRealData(self, szTrCode):
        if self.parent != None:
            self.parent.OnReceiveChartRealData(szTrCode)

    def OnReceiveSearchRealData(self, szTrCode):
        if self.parent != None:
            self.parent.OnReceiveSearchRealData(szTrCode)


class XAQuery(object):
    TIMER = {}
    # TIMER_RESTRICT = {}

    def __init__(self, parent=None):
        self.parent = parent

        self.ActiveX = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEvents)
        self.ActiveX.set_parent(parent=self)

        self.RESDIR = 'C:\\eBEST\\xingAPI'

        self.MYNAME = self.__class__.__name__
        self.INBLOCK = "%sInBlock" % self.MYNAME
        self.INBLOCK1 = "%sInBlock1" % self.MYNAME
        self.OUTBLOCK = "%sOutBlock" % self.MYNAME
        self.OUTBLOCK1 = "%sOutBlock1" % self.MYNAME
        self.OUTBLOCK2 = "%sOutBlock2" % self.MYNAME
        self.OUTBLOCK3 = "%sOutBlock3" % self.MYNAME
        self.RESFILE = "%s\\Res\\%s.res" % (self.RESDIR, self.MYNAME)

    def QueryWaiting(self, howlong=100.0, limit_count=None, limit_seconds=600):
        NOW = datetime.datetime.now()
        DELTA = datetime.timedelta(milliseconds=howlong)
        result = XAQuery.TIMER.get(self.MYNAME, None)

        if result == None:
            XAQuery.TIMER[self.MYNAME] = NOW + DELTA # 이 시간이 지나야 다음 쿼리가 가능
            # if limit_count != None:
            #     XAQuery.TIMER_RESTRICT[self.MYNAME] = [NOW]
        else:
            # if limit_count != None:
            #     if len(XAQuery.TIMER_RESTRICT[self.MYNAME]) > limit_count-1:
            #         idx = limit_count-1
            #         if XAQuery.TIMER_RESTRICT[self.MYNAME][-idx] + datetime.timedelta(seconds=limit_seconds) >= datetime.datetime.now():
            #             DELTA = (XAQuery.TIMER_RESTRICT[self.MYNAME][-idx] + datetime.timedelta(seconds=limit_seconds) - datetime.datetime.now()).total_seconds()
            #             time.sleep(DELTA)
            if NOW > result:
                XAQuery.TIMER[self.MYNAME] = NOW + DELTA
                # if limit_count != None:
                #     XAQuery.TIMER_RESTRICT[self.MYNAME].append(NOW)
            else:
                diff = (result - NOW).total_seconds()
                time.sleep(diff)

                NOW = datetime.datetime.now()
                XAQuery.TIMER[self.MYNAME] = NOW + DELTA

                # if limit_count != None:
                #     XAQuery.TIMER_RESTRICT[self.MYNAME].append(NOW)

    def toint(self, s):
        temp = s.strip()
        result = 0
        if temp not in ['-']:
            result = int(temp)
        else:
            result = 0
        return result

    def tofloat(self, s):
        temp = s.strip()
        result = 0
        if temp not in ['-']:
            result = float(temp)
        else:
            result = 0.0
        return result

    def OnReceiveMessage(self, systemError, messageCode, message):
        if self.parent != None:
            self.parent.OnReceiveMessage(systemError, messageCode, message)

    def OnReceiveData(self, szTrCode):
        pass

    def OnReceiveChartRealData(self, szTrCode):
        pass

    def RequestLinkToHTS(self, szLinkName, szData, szFiller):
        return self.ActiveX.RequestLinkToHTS(szLinkName, szData, szFiller)




''' 주식종목코드조회'''
class t8430(XAQuery):
    ''' 주식종목코드조회'''
    def Query(self, 구분='0'):
        self.QueryWaiting(howlong=50.0, limit_count=None, limit_seconds=600)

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
        self.ActiveX.Request(0)

    def OnReceiveData(self, szTrCode):
        self.result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", i).strip()
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", i).strip()
            확장코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "expcode", i).strip()
            ETF구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "etfgubun", i).strip())
            상한가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "uplmtprice", i).strip())
            하한가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "dnlmtprice", i).strip())
            전일가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "jnilclose", i).strip())
            주문수량단위 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "memedan", i).strip())
            기준가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "recprice", i).strip())
            구분 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "gubun", i).strip())

            lst = [종목명, 종목코드, 확장코드, ETF구분, 상한가, 하한가, 전일가, 주문수량단위, 기준가, 구분]
            self.result.append(lst)        

    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['종목명', '종목코드', '확장코드', 'ETF구분', 
                        '상한가', '하한가', '전일가', '주문수량단위', '기준가', '구분'])



# 업종전체조회
class t8424(XAQuery):
    def Query(self, 구분=''):
        self.QueryWaiting(howlong=100.0, limit_count=None, limit_seconds=600)

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun1", 0, 구분)
        self.ActiveX.Request(0)

    def OnReceiveData(self, szTrCode):
        self.result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            업종명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", i).strip()
            업종코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "upcode", i).strip()

            lst = [업종명, 업종코드]
            self.result.append(lst)

    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['업종명', '업종코드'])


# 전체테마
class t8425(XAQuery):
    def Query(self):
        self.QueryWaiting(howlong=100.0, limit_count=None, limit_seconds=600)

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "dummy", 0, "0")
        self.ActiveX.Request(0)

    def OnReceiveData(self, szTrCode):
        self.result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            테마명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "tmname", i).strip()
            테마코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "tmcode", i).strip()

            lst = [테마명, 테마코드]
            self.result.append(lst)

    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['테마명', '테마코드'])


'''주식현재가(시세)조회'''
class t1102(XAQuery):
    '''주식현재가(시세)조회'''
    def Query(self, 종목코드):
        self.QueryWaiting(howlong=20.0, limit_count=None, limit_seconds=600)
        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
        self.ActiveX.Request(0)   
    def OnReceiveData(self, szTrCode):
        self.result = dict()

        self.result['한글명'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "hname", 0)
        self.result['현재가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "price", 0)
        self.result['전일대비구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sign", 0)
        self.result['전일대비'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "change", 0)
        self.result['등락율'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "diff", 0)
        self.result['누적거래량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "volume", 0)
        self.result['기준가_평가가격'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "recprice", 0)
        self.result['가중평균'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "avg", 0)
        self.result['상한가_최고호가가격'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "uplmtprice", 0)
        self.result['하한가_최저호가가격'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dnlmtprice", 0)
        self.result['전일거래량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "jnilvolume", 0)
        self.result['거래량차'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "volumediff", 0)
        self.result['시가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "open", 0)
        self.result['시가시간'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "opentime", 0)
        self.result['고가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "high", 0)
        self.result['고가시간'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "hightime", 0)
        self.result['저가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "low", 0)
        self.result['저가시간'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "lowtime", 0)
        self.result['최고가_52'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "high52w", 0)
        self.result['최고가일_52'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "high52wdate", 0)
        self.result['최저가_52'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "low52w", 0)
        self.result['최저가일_52'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "low52wdate", 0)
        self.result['소진율'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "exhratio", 0)
        self.result['PER'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "per", 0)
        self.result['PBRX'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "pbrx", 0)
        self.result['상장주식수_천'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "listing", 0)
        self.result['증거금율'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "jkrate", 0)
        self.result['수량단위'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "memedan", 0)
        self.result['매도증권사코드1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd1", 0)
        self.result['매수증권사코드1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd1", 0)
        self.result['매도증권사명1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno1", 0)
        self.result['매수증권사명1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno1", 0)
        self.result['총매도수량1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol1", 0)
        self.result['총매수수량1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol1", 0)
        self.result['매도증감1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha1", 0)
        self.result['매수증감1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha1", 0)
        self.result['매도비율1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff1", 0)
        self.result['매수비율1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff1", 0)
        self.result['매도증권사코드2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd2", 0)
        self.result['매수증권사코드2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd2", 0)
        self.result['매도증권사명2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno2", 0)
        self.result['매수증권사명2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno2", 0)
        self.result['총매도수량2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol2", 0)
        self.result['총매수수량2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol2", 0)
        self.result['매도증감2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha2", 0)
        self.result['매수증감2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha2", 0)
        self.result['매도비율2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff2", 0)
        self.result['매수비율2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff2", 0)
        self.result['매도증권사코드3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd3", 0)
        self.result['매수증권사코드3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd3", 0)
        self.result['매도증권사명3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno3", 0)
        self.result['매수증권사명3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno3", 0)
        self.result['총매도수량3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol3", 0)
        self.result['총매수수량3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol3", 0)
        self.result['매도증감3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha3", 0)
        self.result['매수증감3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha3", 0)
        self.result['매도비율3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff3", 0)
        self.result['매수비율3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff3", 0)
        self.result['매도증권사코드4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd4", 0)
        self.result['매수증권사코드4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd4", 0)
        self.result['매도증권사명4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno4", 0)
        self.result['매수증권사명4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno4", 0)
        self.result['총매도수량4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol4", 0)
        self.result['총매수수량4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol4", 0)
        self.result['매도증감4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha4", 0)
        self.result['매수증감4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha4", 0)
        self.result['매도비율4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff4", 0)
        self.result['매수비율4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff4", 0)
        self.result['매도증권사코드5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offernocd5", 0)
        self.result['매수증권사코드5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidnocd5", 0)
        self.result['매도증권사명5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "offerno5", 0)
        self.result['매수증권사명5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bidno5", 0)
        self.result['총매도수량5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dvol5", 0)
        self.result['총매수수량5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svol5", 0)
        self.result['매도증감5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dcha5", 0)
        self.result['매수증감5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "scha5", 0)
        self.result['매도비율5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ddiff5", 0)
        self.result['매수비율5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sdiff5", 0)
        self.result['외국계매도합계수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "fwdvl", 0)
        self.result['외국계매도직전대비'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmdcha", 0)
        self.result['외국계매도비율'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmddiff", 0)
        self.result['외국계매수합계수량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "fwsvl", 0)
        self.result['외국계매수직전대비'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmscha", 0)
        self.result['외국계매수비율'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmsdiff", 0)
        self.result['회전율'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "vol", 0)
        self.result['종목코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", 0)
        self.result['누적거래대금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "value", 0)
        self.result['전일동시간거래량'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "jvolume", 0)
        self.result['연중최고가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "highyear", 0)
        self.result['연중최고일자'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "highyeardate", 0)
        self.result['연중최저가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "lowyear", 0)
        self.result['연중최저일자'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "lowyeardate", 0)
        self.result['목표가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "target", 0)
        self.result['자본금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "capital", 0)
        self.result['유동주식수'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "abscnt", 0)
        self.result['액면가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "parprice", 0)
        self.result['결산월'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "gsmm", 0)
        self.result['대용가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "subprice", 0)
        self.result['시가총액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "total", 0)
        self.result['상장일'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "listdate", 0)
        self.result['전분기명'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "name", 0)
        self.result['전분기매출액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfsales", 0)
        self.result['전분기영업이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfoperatingincome", 0)
        self.result['전분기경상이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfordinaryincome", 0)
        self.result['전분기순이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfnetincome", 0)
        self.result['전분기EPS'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfeps", 0)
        self.result['전전분기명'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "name2", 0)
        self.result['전전분기매출액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfsales2", 0)
        self.result['전전분기영업이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfoperatingincome2", 0)
        self.result['전전분기경상이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfordinaryincome2", 0)
        self.result['전전분기순이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfnetincome2", 0)
        self.result['전전분기EPS'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "bfeps2", 0)
        self.result['전년대비매출액'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "salert", 0)
        self.result['전년대비영업이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "opert", 0)
        self.result['전년대비경상이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ordrt", 0)
        self.result['전년대비순이익'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "netrt", 0)
        self.result['전년대비EPS'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "epsrt", 0)
        self.result['락구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "info1", 0)
        self.result['관리_급등구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "info2", 0)
        self.result['정지_연장구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "info3", 0)
        self.result['투자_불성실구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "info4", 0)
        self.result['장구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "janginfo", 0)
        self.result['TPER'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "t_per", 0)
        self.result['통화ISO코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "tonghwa", 0)
        self.result['총매도대금1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval1", 0)
        self.result['총매수대금1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval1", 0)
        self.result['총매도대금2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval2", 0)
        self.result['총매수대금2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval2", 0)
        self.result['총매도대금3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval3", 0)
        self.result['총매수대금3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval3", 0)
        self.result['총매도대금4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval4", 0)
        self.result['총매수대금4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval4", 0)
        self.result['총매도대금5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "dval5", 0)
        self.result['총매수대금5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "sval5", 0)
        self.result['총매도평단가1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg1", 0)
        self.result['총매수평단가1'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg1", 0)
        self.result['총매도평단가2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg2", 0)
        self.result['총매수평단가2'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg2", 0)
        self.result['총매도평단가3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg3", 0)
        self.result['총매수평단가3'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg3", 0)
        self.result['총매도평단가4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg4", 0)
        self.result['총매수평단가4'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg4", 0)
        self.result['총매도평단가5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "davg5", 0)
        self.result['총매수평단가5'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "savg5", 0)
        self.result['외국계매도대금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmdval", 0)
        self.result['외국계매수대금'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmsval", 0)
        self.result['외국계매도평단가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmdvag", 0)
        self.result['외국계매수평단가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "ftradmsvag", 0)
        self.result['투자주의환기'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "info5", 0)
        self.result['기업인수목적회사여부'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "spac_gubun", 0)
        self.result['발행가격'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "issueprice", 0)
        self.result['배분적용구분코드'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "alloc_gubun", 0)
        self.result['배분적용구분'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "alloc_text", 0)
        self.result['단기과열_VI발동'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "shterm_text", 0)
        self.result['정적VI상한가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svi_uplmtprice", 0)
        self.result['정적VI하한가'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "svi_dnlmtprice", 0)
        self.result['저유동성종목여부'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "low_lqdt_gu", 0)
        self.result['이상급등종목여부'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "abnormal_rise_gu", 0)
        self.result['대차불가표시'] = self.ActiveX.GetFieldData(self.OUTBLOCK, "lend_text", 0)

    def GetResult(self):
        XAQueryEvents.status = False
        return Series(data=self.result, index= self.result.keys())



''' 주식분별주가조회_연속'''
class t1302(XAQuery):
    def Query(self, 종목코드='',작업구분='1',시간='',건수='900', 연속조회=False):
        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)

        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
            self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 작업구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "time", 0, 시간)
            self.ActiveX.SetFieldData(self.INBLOCK, "cnt", 0, 건수)
            self.ActiveX.Request(0)
        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "cts_time", 0, self.시간)

            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True
            if err_code < 0:
                클래스이름 = self.__class__.__name__
                함수이름 = inspect.currentframe().f_code.co_name
                print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):

        self.시간 = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_time", 0).strip()
        self.result = []

        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            시간 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "chetime", i).strip()
            종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "close", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            체결강도 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "chdegree", i).strip())
            매도체결수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdvolume", i).strip())
            매수체결수량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "msvolume", i).strip())
            순매수체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "revolume", i).strip())
            매도체결건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdchecnt", i).strip())
            매수체결건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mschecnt", i).strip())
            순체결건수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "rechecnt", i).strip())
            거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            시가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            고가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            저가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "cvolume", i).strip())
            매도체결건수시간 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdchecnttm", i).strip())
            매수체결건수시간 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mschecnttm", i).strip())
            매도잔량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "totofferrem", i).strip())
            매수잔량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "totbidrem", i).strip())
            시간별매도체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "mdvolumetm", i).strip())
            시간별매수체결량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "msvolumetm", i).strip())

            lst = [시간, 종가, 전일대비구분, 전일대비, 등락율, 체결강도, 매도체결수량, 매수체결수량, 순매수체결량, 매도체결건수, 매수체결건수, 순체결건수, 거래량, 시가, 고가, 저가, 체결량,
                   매도체결건수시간, 매수체결건수시간, 매도잔량, 매수잔량, 시간별매도체결량, 시간별매수체결량]
            self.result.append(lst)

    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['시간', '종가', '전일대비구분', '전일대비', '등락율', '체결강도', '매도체결수량', '매수체결수량', '순매수체결량', '매도체결건수', '매수체결건수',
                        '순체결건수', '거래량', '시가', '고가', '저가', '체결량', '매도체결건수시간', '매수체결건수시간', '매도잔량', '매수잔량', '시간별매도체결량',
                        '시간별매수체결량'])


'''종목코드별체결조회_연속'''      
class t1305(XAQuery):
    '''종목코드별체결조회'''
    def Query(self, 종목코드='',일주월구분='1',날짜='',IDX='',건수='900',연속조회 = False):
        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)
        
        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
            self.ActiveX.SetFieldData(self.INBLOCK, "dwmcode", 0, 일주월구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "date", 0, 날짜)
            self.ActiveX.SetFieldData(self.INBLOCK, "idx", 0, IDX)
            self.ActiveX.SetFieldData(self.INBLOCK, "cnt", 0, 건수)
            self.ActiveX.Request(False)
        else:
            self.ActiveX.SetFieldData("%sInBlock" % self.MYNAME, "cnt", 0, self.건수)
            self.ActiveX.SetFieldData("%sInBlock" % self.MYNAME, "date", 0, self.날짜)
            self.ActiveX.SetFieldData("%sInBlock" % self.MYNAME, "idx", 0, self.IDX)
            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True
            
            if err_code < 0:
                print("error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):

        self.건수 = self.ActiveX.GetFieldData(self.OUTBLOCK, "cnt", 0).strip()
        self.날짜 = self.ActiveX.GetFieldData(self.OUTBLOCK, "date", 0).strip()
        self.IDX = self.ActiveX.GetFieldData(self.OUTBLOCK, "idx", 0).strip()
        
        self.result = []

        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)

        for i in range(nCount):
            일자 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "date", i).strip()
            시가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            고가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            저가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "close", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            거래증가율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff_vol", i).strip())
            체결강도 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "chdegree", i).strip())
            소진율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "sojinrate", i).strip())
            회전율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "changerate", i).strip())
            외인순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "fpvolume", i).strip())
            기관순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "covolume", i).strip())
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            누적거래대금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value", i).strip())
            개인순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "ppvolume", i).strip())
            시가대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "o_sign", i).strip()
            시가대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "o_change", i).strip())
            시가기준등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "o_diff", i).strip())
            고가대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "h_sign", i).strip()
            고가대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "h_change", i).strip())
            고가기준등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "h_diff", i).strip())
            저가대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "l_sign", i).strip()
            저가대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "l_change", i).strip())
            저가기준등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "l_diff", i).strip())
            시가총액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "marketcap", i).strip())

            lst = [일자, 시가, 고가, 저가, 종가, 전일대비구분, 전일대비, 등락율, 누적거래량
                   , 거래증가율, 체결강도, 소진율, 회전율, 외인순매수, 기관순매수, 종목코드
                   , 누적거래대금, 개인순매수, 시가대비구분, 시가대비, 시가기준등락율
                   , 고가대비구분, 고가대비, 고가기준등락율, 저가대비구분, 저가대비
                   , 저가기준등락율, 시가총액]
            
            self.result.append(lst)
            
    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['일자','시가','고가','저가','종가','전일대비구분','전일대비','등락율'
                        ,'누적거래량','거래증가율','체결강도','소진율','회전율','외인순매수'
                        ,'기관순매수','종목코드','누적거래대금','개인순매수','시가대비구분'
                        ,'시가대비','시가기준등락율','고가대비구분','고가대비','고가기준등락율'
                        ,'저가대비구분','저가대비','저가기준등락율','시가총액'])

# 업종별 종목시세 2
# 업종별종목 리스트 1
class t1516(XAQuery):
    def Query(self, 업종코드='001',구분='',종목코드='', 연속조회=False):
        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)

        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "upcode", 0, 업종코드)
            self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
            self.ActiveX.Request(0)
        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, self.종목코드)

            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True
            if err_code < 0:
                클래스이름 = self.__class__.__name__
                함수이름 = inspect.currentframe().f_code.co_name
                print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        
        self.종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", 0).strip()
        self.result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK, "shcode", i).strip()
            지수 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK, "pricejisu", i).strip())
            지수_전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sign", i).strip()
            지수_전일대비 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK, "change", i).strip())
            지수_등락율 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK, "jdiff", i).strip())

            lst = [종목코드, 지수,지수_전일대비구분,지수_전일대비,지수_등락율]

            self.result.append(lst)


        self.result2 = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            현재가 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i))
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i))
            등락율 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i))
            누적거래량 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i))
            시가 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i))
            고가 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i))
            저가 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i))
            소진율 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK1, "sojinrate", i))
            베타계수 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK1, "beta", i))
            PER = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK1, "perx", i))
            외인순매수 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "frgsvolume", i))
            기관순매수 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "orgsvolume", i))
            거래증가율 = self.tofloat(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff_vol", i))
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            시가총액 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "total", i))
            거래대금 = self.toint(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value", i))

            lst = [종목명,현재가,전일대비구분,전일대비,등락율,누적거래량,시가,고가,저가,소진율,베타계수,PER,외인순매수,기관순매수,거래증가율,종목코드,시가총액,거래대금]

            self.result2.append(lst)


    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result2, columns=['종목명','현재가','전일대비구분','전일대비','등락율','누적거래량','시가','고가','저가','소진율','베타계수','PER','외인순매수','기관순매수','거래증가율','종목코드','시가총액','거래대금'])            

    def GetResult2(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['종목코드','지수','지수_전일대비구분','지수_전일대비','지수_등락율'])     



# 테마중 상승종목수 2
# 테마종목별 시세조회 1
class t1537(XAQuery):
    def Query(self, 테마코드='0001', 연속조회=False):
        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)

        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "tmcode", 0, 테마코드)
            self.ActiveX.Request(0)
        else:
            self.ActiveX.SetFieldData(self.INBLOCK, "cts_date", 0, self.CTSDATE)

            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True
            if err_code < 0:
                클래스이름 = self.__class__.__name__
                함수이름 = inspect.currentframe().f_code.co_name
                print("%s-%s " % (클래스이름, 함수이름), "error... {0}".format(err_code))

    def OnReceiveData(self, szTrCode):
        self.CTSDATE = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_date", 0).strip()

        self.result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            상승종목수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "upcnt", i).strip())
            테마종목수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tmcnt", i).strip())
            상승종목비율 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "uprate", i).strip())
            테마명 = self.ActiveX.GetFieldData(self.OUTBLOCK, "tmname", i).strip()

            lst = [상승종목수, 테마종목수, 상승종목비율, 테마명]
            self.result.append(lst)


        self.result2 = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)
        for i in range(nCount):
            종목명 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "hname", i).strip()
            현재가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "price", i).strip())
            전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            전일동시간 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "jniltime", i).strip())
            종목코드 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "shcode", i).strip()
            예상체결가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "yeprice", i).strip())
            시가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            고가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            저가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            누적거래대금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value", i).strip())
            시가총액 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "marketcap", i).strip())

            lst = [종목명, 현재가, 전일대비구분, 전일대비, 등락율, 누적거래량, 전일동시간, 종목코드, 예상체결가, 시가, 고가, 저가, 누적거래대금, 시가총액]
            self.result2.append(lst)


    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result2, columns=['종목명', '현재가', '전일대비구분', '전일대비', '등락율', '누적거래량', '전일동시간', '종목코드', '예상체결가', '시가', '고가', '저가',
                       '누적거래대금', '시가총액'])            

    def GetResult2(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['상승종목수', '테마종목수', '상승종목비율', '테마명'])     


''' 외인기관종목별동향_연속'''
class t1702(XAQuery):
    ''' 외인기관종목별동향'''

    def Query(self, 종목코드='069500',종료일자='',금액수량구분='0',매수매도구분='0',누적구분='0',
                CTSDATE='',CTSIDX='', 연속조회 = False):

        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)

        if 연속조회 == False:
            self.ActiveX.LoadFromResFile(self.RESFILE)
            self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
            self.ActiveX.SetFieldData(self.INBLOCK, "todt", 0, 종료일자)
            self.ActiveX.SetFieldData(self.INBLOCK, "volvalgb", 0, 금액수량구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "msmdgb", 0, 매수매도구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "cumulgb", 0, 누적구분)
            self.ActiveX.SetFieldData(self.INBLOCK, "cts_date", 0, CTSDATE)
            self.ActiveX.SetFieldData(self.INBLOCK, "cts_idx", 0, CTSIDX)
            self.ActiveX.Request(0)

        else: 
            self.ActiveX.SetFieldData("%sInBlock" % self.MYNAME, "cts_date", 0, self.CTSDATE)
            self.ActiveX.SetFieldData("%sInBlock" % self.MYNAME, "cts_idx", 0, self.CTSIDX)
            err_code = self.ActiveX.Request(True)  # 연속조회인경우만 True  

            if err_code < 0:
                print("error... {0}".format(err_code))


    def OnReceiveData(self, szTrCode):

        self.CTSIDX = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_idx", 0).strip()
        self.CTSDATE = self.ActiveX.GetFieldData(self.OUTBLOCK, "cts_date", 0).strip()
        
        self.result = []

        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)

        for i in range(nCount):
            try:
                일자 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "date", i).strip()
            except Exception as e:
                일자 = ''
            try:
                종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "close", i).strip())
            except Exception as e:
                종가 = 0
            try:
                전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "sign", i).strip()
            except Exception as e:
                전일대비구분 = 0
            try:
                전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "change", i).strip())
            except Exception as e:
                전일대비 = 0
            try:
                등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "diff", i).strip())
            except Exception as e:
                등락율 = 0
            try:
                누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            except Exception as e:
                누적거래량 = 0
            try:
                사모펀드 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0000", i).strip())
            except Exception as e:
                사모펀드 = 0
            try:
                증권 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0001", i).strip())
            except Exception as e:
                증권 = 0
            try:
                보험 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0002", i).strip())
            except Exception as e:
                보험 = 0
            try:
                투신 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0003", i).strip())
            except Exception as e:
                투신 = 0
            try:
                은행 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0004", i).strip())
            except Exception as e:
                은행 = 0
            try:
                종금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0005", i).strip())
            except Exception as e:
                종금 = 0
            try:
                기금 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0006", i).strip())
            except Exception as e:
                기금 = 0
            try:
                기타법인 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0007", i).strip())
            except Exception as e:
                기타법인 = 0
            try:
                개인 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0008", i).strip())
            except Exception as e:
                개인 = 0
            try:
                등록외국인 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0009", i).strip())
            except Exception as e:
                등록외국인 = 0
            try:
                미등록외국인 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0010", i).strip())
            except Exception as e:
                미등록외국인 = 0
            try:
                국가외 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0011", i).strip())
            except Exception as e:
                국가외 = 0
            try:
                기관 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0018", i).strip())
            except Exception as e:
                기관 = 0
            try:
                외인계 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0088", i).strip())
            except Exception as e:
                외인계 = 0
            try:
                기타계 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "amt0099", i).strip())
            except Exception as e:
                기타계 = 0

            lst = [일자, 종가, 전일대비구분, 전일대비, 등락율, 누적거래량, 사모펀드, 증권, 보험, 투신, 은행, 종금, 기금, 기타법인, 개인, 등록외국인, 미등록외국인, 국가외, 기관,
                   외인계, 기타계]

            self.result.append(lst)
        
    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data=self.result, columns=['일자','종가','전일대비구분','전일대비','등락율'
                                                    ,'누적거래량','사모펀드','증권','보험','투신','은행'
                                                    ,'종금','기금','기타법인','개인','등록외국인'
                                                    ,'미등록외국인','국가외','기관','외인계','기타계'])


''' 외인기관종목별동향_단가등용'''
class t1717(XAQuery):
    def Query(self, 종목코드='069500',구분='0',시작일자='20170101',종료일자='20172131'):

        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)
        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
        self.ActiveX.SetFieldData(self.INBLOCK, "gubun", 0, 구분)
        self.ActiveX.SetFieldData(self.INBLOCK, "fromdt", 0, 시작일자)
        self.ActiveX.SetFieldData(self.INBLOCK, "todt", 0, 종료일자)
        self.ActiveX.Request(0)


    def OnReceiveData(self, szTrCode):
        self.result = []
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK)
        for i in range(nCount):
            try:
                일자 = self.ActiveX.GetFieldData(self.OUTBLOCK, "date", i).strip()
            except Exception as e:
                일자 = ''
            try:
                종가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "close", i).strip())
            except Exception as e:
                종가 = 0
            try:
                전일대비구분 = self.ActiveX.GetFieldData(self.OUTBLOCK, "sign", i).strip()
            except Exception as e:
                전일대비구분 = 0
            try:
                전일대비 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "change", i).strip())
            except Exception as e:
                전일대비 = 0
            try:
                등락율 = float(self.ActiveX.GetFieldData(self.OUTBLOCK, "diff", i).strip())
            except Exception as e:
                등락율 = 0
            try:
                누적거래량 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "volume", i).strip())
            except Exception as e:
                누적거래량 = 0
            try:
                사모펀드_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0000_vol", i).strip())
            except Exception as e:
                사모펀드_순매수 = 0
            try:
                증권_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0001_vol", i).strip())
            except Exception as e:
                증권_순매수 = 0
            try:
                보험_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0002_vol", i).strip())
            except Exception as e:
                보험_순매수 = 0
            try:
                투신_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0003_vol", i).strip())
            except Exception as e:
                투신_순매수 = 0
            try:
                은행_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0004_vol", i).strip())
            except Exception as e:
                은행_순매수 = 0
            try:
                종금_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0005_vol", i).strip())
            except Exception as e:
                종금_순매수 = 0
            try:
                기금_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0006_vol", i).strip())
            except Exception as e:
                기금_순매수 = 0
            try:
                기타법인_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0007_vol", i).strip())
            except Exception as e:
                기타법인_순매수 = 0
            try:
                개인_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0008_vol", i).strip())
            except Exception as e:
                개인_순매수 = 0
            try:
                등록외국인_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0009_vol", i).strip())
            except Exception as e:
                등록외국인_순매수 = 0
            try:
                미등록외국인_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0010_vol", i).strip())
            except Exception as e:
                미등록외국인_순매수 = 0
            try:
                국가외_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0011_vol", i).strip())
            except Exception as e:
                국가외_순매수 = 0
            try:
                기관_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0018_vol", i).strip())
            except Exception as e:
                기관_순매수 = 0
            try:
                외인계_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0016_vol", i).strip())
            except Exception as e:
                외인계_순매수 = 0
            try:
                기타계_순매수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0017_vol", i).strip())
            except Exception as e:
                기타계_순매수 = 0
            try:
                사모펀드_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0000_dan", i).strip())
            except Exception as e:
                사모펀드_단가 = 0
            try:
                증권_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0001_dan", i).strip())
            except Exception as e:
                증권_단가 = 0
            try:
                보험_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0002_dan", i).strip())
            except Exception as e:
                보험_단가 = 0
            try:
                투신_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0003_dan", i).strip())
            except Exception as e:
                투신_단가 = 0
            try:
                은행_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0004_dan", i).strip())
            except Exception as e:
                은행_단가 = 0
            try:
                종금_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0005_dan", i).strip())
            except Exception as e:
                종금_단가 = 0
            try:
                기금_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0006_dan", i).strip())
            except Exception as e:
                기금_단가 = 0
            try:
                기타법인_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0007_dan", i).strip())
            except Exception as e:
                기타법인_단가 = 0
            try:
                개인_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0008_dan", i).strip())
            except Exception as e:
                개인_단가 = 0
            try:
                등록외국인_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0009_dan", i).strip())
            except Exception as e:
                등록외국인_단가 = 0
            try:
                미등록외국인_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0010_dan", i).strip())
            except Exception as e:
                미등록외국인_단가 = 0
            try:
                국가외_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0011_dan", i).strip())
            except Exception as e:
                국가외_단가 = 0
            try:
                기관_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0018_dan", i).strip())
            except Exception as e:
                기관_단가 = 0
            try:
                외인계_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0016_dan", i).strip())
            except Exception as e:
                외인계_단가 = 0
            try:
                기타계_단가 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "tjj0017_dan", i).strip())
            except Exception as e:
                기타계_단가 = 0

            lst = [일자, 종가, 전일대비구분, 전일대비, 등락율, 누적거래량,
                   사모펀드_순매수, 증권_순매수, 보험_순매수, 투신_순매수, 은행_순매수, 종금_순매수, 기금_순매수, 기타법인_순매수, 개인_순매수, 등록외국인_순매수, 미등록외국인_순매수,
                   국가외_순매수, 기관_순매수, 외인계_순매수, 기타계_순매수,
                   사모펀드_단가, 증권_단가, 보험_단가, 투신_단가, 은행_단가, 종금_단가, 기금_단가, 기타법인_단가, 개인_단가, 등록외국인_단가, 미등록외국인_단가, 국가외_단가,
                   기관_단가, 외인계_단가, 기타계_단가]

            self.result.append(lst)
        
    def GetResult(self):
        XAQueryEvents.status = False
        return DataFrame(data= self.result, columns= ['일자', '종가', '전일대비구분', '전일대비', '등락율', '누적거래량', 
                                                '사모펀드_순매수', '증권_순매수', '보험_순매수', '투신_순매수', 
                                                '은행_순매수','종금_순매수', '기금_순매수', '기타법인_순매수', '개인_순매수', 
                                                '등록외국인_순매수', '미등록외국인_순매수', '국가외_순매수', '기관_순매수',
                                                '외인계_순매수', '기타계_순매수', '사모펀드_단가', '증권_단가', '보험_단가', 
                                                '투신_단가', '은행_단가', '종금_단가', '기금_단가', '기타법인_단가',
                                                '개인_단가', '등록외국인_단가', '미등록외국인_단가', '국가외_단가', '기관_단가',
                                                 '외인계_단가', '기타계_단가'])



# 추세지표 : '가격 이동평균'
# 변동성지표 : 'Bollinger Bands'
# 모멘텀지표 : 'Stochastics Slow', 'RSI'
''' 차트인덱스 '''
class ChartIndex(XAQuery):
    def Query(self, 지표ID='',지표명='',지표조건설정='',시장구분='',주기구분='',종목코드='',요청건수='500',단위='',시작일자='',종료일자='',수정주가반영여부='',갭보정여부='',실시간데이터수신자동등록여부='0'):
        self.QueryWaiting(howlong=100.0, limit_count=200, limit_seconds=600)

        self.ActiveX.LoadFromResFile(self.RESFILE)
        self.ActiveX.SetFieldData(self.INBLOCK, "indexid", 0, 지표ID)
        self.ActiveX.SetFieldData(self.INBLOCK, "indexname", 0, 지표명)
        self.ActiveX.SetFieldData(self.INBLOCK, "indexparam", 0, 지표조건설정)
        self.ActiveX.SetFieldData(self.INBLOCK, "market", 0, 시장구분)
        self.ActiveX.SetFieldData(self.INBLOCK, "period", 0, 주기구분)
        self.ActiveX.SetFieldData(self.INBLOCK, "shcode", 0, 종목코드)
        self.ActiveX.SetFieldData(self.INBLOCK, "qrycnt", 0, 요청건수)
        self.ActiveX.SetFieldData(self.INBLOCK, "ncnt", 0, 단위)
        self.ActiveX.SetFieldData(self.INBLOCK, "sdate", 0, 시작일자)
        self.ActiveX.SetFieldData(self.INBLOCK, "edate", 0, 종료일자)
        self.ActiveX.SetFieldData(self.INBLOCK, "Isamend", 0, 수정주가반영여부)
        self.ActiveX.SetFieldData(self.INBLOCK, "Isgab", 0, 갭보정여부)
        self.ActiveX.SetFieldData(self.INBLOCK, "IsReal", 0, 실시간데이터수신자동등록여부)
        self.ActiveX.RequestService("ChartIndex", "")

    def RemoveService(self):
        try:
            self.지표ID = self.ActiveX.GetFieldData(self.OUTBLOCK, "indexid", 0).strip()
            self.ActiveX.RemoveService("ChartIndex", self.지표ID)
        except Exception as e:
            pass

    def OnReceiveData(self, szTrCode):
        self.지표ID = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "indexid", 0).strip())
        self.레코드갯수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "rec_cnt", 0).strip())
        self.유효데이터컬럼갯수 = int(self.ActiveX.GetFieldData(self.OUTBLOCK, "validdata_cnt", 0).strip())

        self.result = []
        
        nCount = self.ActiveX.GetBlockCount(self.OUTBLOCK1)

        for i in range(nCount):
            일자 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "date", i).strip()
            시간 = self.ActiveX.GetFieldData(self.OUTBLOCK1, "time", i).strip()
            시가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "open", i).strip())
            고가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "high", i).strip())
            저가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "low", i).strip())
            종가 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "close", i).strip())
            거래량 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "volume", i).strip())
            지표값1 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value1", i).strip())
            지표값2 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value2", i).strip())
            지표값3 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value3", i).strip())
            지표값4 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value4", i).strip())
            지표값5 = float(self.ActiveX.GetFieldData(self.OUTBLOCK1, "value5", i).strip())
            위치 = int(self.ActiveX.GetFieldData(self.OUTBLOCK1, "pos", i).strip())

            lst = [일자, 시간, 시가, 고가, 저가, 종가, 거래량, 지표값1, 지표값2, 지표값3, 지표값4, 지표값5, 위치]
            self.result.append(lst)

    def GetResult(self):
        XAQueryEvents.status = False        
        return DataFrame(data=self.result, columns=['일자', '시간', '시가', '고가', '저가', '종가', '거래량', 
                                                    '지표값1', '지표값2', '지표값3', '지표값4', '지표값5', '위치'])


    '''
    def OnReceiveChartRealData(self, szTrCode):
        self.지표ID = self.ActiveX.GetFieldChartRealData(self.OUTBLOCK, "indexid").strip()
        self.레코드갯수 = self.ActiveX.GetFieldChartRealData(self.OUTBLOCK, "rec_cnt").strip()
        self.유효데이터컬럼갯수 = self.ActiveX.GetFieldChartRealData(self.OUTBLOCK, "validdata_cnt").strip()

        result = dict()
        result['일자'] = self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "date").strip()
        result['시간'] = self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "time").strip()
        result['시가'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "open").strip())
        result['고가'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "high").strip())
        result['저가'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "low").strip())
        result['종가'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "close").strip())
        result['거래량'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "volume").strip())
        result['지표값1'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "value1").strip())
        result['지표값2'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "value2").strip())
        result['지표값3'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "value3").strip())
        result['지표값4'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "value4").strip())
        result['지표값5'] = float(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "value5").strip())
        result['위치'] = int(self.ActiveX.GetFieldChartRealData(self.OUTBLOCK1, "pos").strip())
    '''



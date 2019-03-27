# -*- coding: utf-8 -*-
import re
import datetime
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#需要保留斜杠的字段
C_BaoLiuXieGang = {
    "MZZD":1,"ZYZD":1,"QTZD1":1,"QTZD2":1,"QTZD3":1,"QTZD4":1,"QTZD5":1,"QTZD6":1,"QTZD7":1,"QTZD9":1,"QTZD10":1,
    "QTZD11":1,"QTZD12":1,"QTZD13":1,"QTZD14":1,"QTZD15":1,"BLZD":1,"BLH":1,"SSJCZMC1":1,"SSJCZMC2":1,"SSJCZMC3":1,
    "SSJCZMC4":1,"SSJCZMC5":1,"SSJCZMC6":1,"SSJCZMC7":1,"H23":1,"JBMM":1,"JBBM":1,"JBDM":1,"JBDM1":1,"JBDM2":1,
    "JBDM3":1,"JBDM4":1,"JBDM5":1,"JBDM6":1,"JBDM7":1,"JBDM8":1,"JBDM9":1,"JBDM10":1,"JBDM11":1,"JBDM12":1,"JBDM13":1,
    "JBDM14":1,"JBDM15":1,"SSJCZBM1":1,"SSJCZBM2":1,"SSJCZBM3":1,"SSJCZBM4":1,"SSJCZBM5":1,"SSJCZBM6":1,"SSJCZBM7":1
}

#编码字段
C_BianMa = {
    "H23":1,"JBMM":1,"JBBM":1,"JBDM":1,"JBDM1":1,"JBDM2":1,"JBDM3":1,"JBDM4":1,"JBDM5":1,"JBDM6":1,"JBDM7":1,
    "JBDM8":1,"JBDM9":1,"JBDM10":1,"JBDM11":1,"JBDM12":1,"JBDM13":1,"JBDM14":1,"JBDM15":1,"SSJCZBM1":1,
    "SSJCZBM2":1,"SSJCZBM3":1,"SSJCZBM4":1,"SSJCZBM5":1,"SSJCZBM6":1,"SSJCZBM7":1
}

#需要处理科学计数法的字段
C_KexueJishu = {
    "SFZH":1,"JKKH":1,"DH":1,"DH2":1,"DWDH":1
}

#需要处理成日期的字段
C_Date = {
    "CSRQ":1,"RYSJ":1,"CYSJ":1,"QZRQ":1,"ZKRQ":1,"SSJCZRQ1":1,"SSJCZRQ2":1,"SSJCZRQ3":1,"SSJCZRQ4":1,"SSJCZRQ5":1,"SSJCZRQ6":1,"SSJCZRQ7":1
}

#出入院科别字段
C_CRYKB = {
    "CYKB":1,"RYKB":1
}

#需要处理成整数，不保留小数的字段
C_Int = {
    "QJCS":1,"QJCGCS":1,"RYQ_T":1,"RYQ_F":1,"RYH_T":1,"RYH_F":1,"RYSJS":1,"CYSJS":1,"RYQ_XS":1,"RYH_XS":1,"P785":1,"P795":1,
    "P796":1,"P799":1,"P1800":1,"P64":1,"P1802":1,"P1803":1,"P1804":1,"P1805":1,"P1806":1,"P1807":1,"P1808":1,"P1809":1,
    "P1810":1,"P1811":1,"BAH":1,"LYFS":1,"YLFKFS":1,"ZYCS":1,"JKKH":1,"XB":1,"ZY":1,"HY":1,"RYTJ":1,"GX":1,"SJZYTS":1,
    "RYBQ":1,"RYBQ1":1,"RYBQ2":1,"RYBQ3":1,"RYBQ4":1,"RYBQ5":1,"RYBQ6":1,"RYBQ7":1,"RYBQ8":1,"RYBQ9":1,"RYBQ10":1,"RYBQ11":1,
    "RYBQ12":1,"RYBQ13":1,"RYBQ14":1,"RYBQ15":1,"BLH":1,"YWGM":1,"SWHZSJ":1,"XX":1,"RH":1,"BAZL":1,"SFZZYJH":1,"YB1":1,
    "YB2":1,"YB3":1,"RYBF":1,"ZKKB":1,"CYBF":1,"SSJB1":1,"SSJB2":1,"SSJB3":1,"SSJB4":1,"SSJB5":1,"MZ":1
}

#需要处理成保留两位小数的样子的字段
C_Float = {
    "ZFY":1,"ZFJE":1,"YLFUF":1,"BZLZF":1,"ZYBLZHZF":1,"ZLCZF":1,"HLF":1,"QTFY":1,"BLZDF":1,"SYSZDF":1,"YXXZDF":1,
    "LCZDXMF":1,"FSSZLXMF":1,"WLZLF":1,"SSZLF":1,"MAF":1,"SSF":1,"KFF":1,"ZYL_ZYZD":1,"ZYZLF":1,"ZYWZ":1,"ZYGS":1,
    "ZCYJF":1,"ZYTNZL":1,"ZYGCZL":1,"ZYTSZL":1,"ZYQT":1,"ZYTSTPJG":1,"BZSS":1,"XYF":1,"KJYWF":1,"ZCYF":1,"ZYZJF":1,
    "ZCYF1":1,"XF":1,"BDBLZPF":1,"QDBLZPF":1,"NXYZLZPF":1,"XBYZLZPF":1,"HCYYCLF":1,"YYCLF":1,"YCXYYCLF":1,"QTF":1
}

#以下这些字段里如果只有一个小减号则当成没有填写，直接返回空字符串
C_Jianhao = {
    "XSECSTZ":1,"XSERYTZ":1,"SJZYTS":1,"CYKB":1,"CYBF":1,"RYKB":1,"RYBF":1,"ZYZD":1,"JBDM":1,"JBDM1":1,"JBDM2":1,"JBDM3":1,"JBDM4":1,"JBDM5":1,
    "JBDM6":1,"JBDM7":1,"JBDM8":1,"JBDM9":1,"JBDM10":1,"JBDM11":1,"JBDM12":1,"JBDM13":1,"JBDM14":1,"JBDM15":1,"MZZD":1,"JBBM":1,"SSJCZMC1":1,
    "SSJCZMC2":1,"SSJCZMC3":1,"SSJCZMC4":1,"SSJCZMC5":1,"SSJCZMC6":1,"SSJCZMC7":1,"SSJCZBM2":1,"SSJCZBM3":1,"SSJCZBM4":1,"SSJCZBM5":1,
    "SSJCZBM6":1,"SSJCZBM7":1,"SSJCZRQ1":1,"SSJCZRQ2":1,"SSJCZRQ3":1,"SSJCZRQ4":1,"SSJCZRQ5":1,"SSJCZRQ6":1,"SSJCZRQ7":1,"SSJCZRQ8":1,
    "MZFS1":1,"MZFS2":1,"MZFS3":1,"MZFS4":1,"MZFS5":1,"MZFS6":1,"MZFS7":1
}

class DataClean:
    def __init__(self):
        pass

    def cleanByField(self, fieldName, fieldValue, fileType):
        res = fieldValue.strip()
        if res == '\\':
            res = ''
        res = self.__clean4Jianhao(fieldName, res)
        res = self.__clean4Date(fieldName, res)
        res = self.__clean4KexueJishu(fieldName, res)
        res = self.__clean4CRYKB(fieldName, res)
        res = self.__clean4Int(fieldName, res)
        res = self.__clean4Float(fieldName, res)
        res = self.__clean4NL(fieldName, res)
        res = self.__clean4BZYZSNL(fieldName, res)
        res = self.__clean4BianMa(fieldName, res)
        res = self.__clean4XieGang(fieldName, res)
        res = self.__clean4MZ(fieldName, res)
        res = self.__clean4YLFKFS(fieldName, res)
        res = self.__clean4GX(fieldName, res)

        if fileType.upper() == 'XML':
            res = self.__clean4XML(fieldName, res)
        return res

    #专门针对XML文件的某些字段做特殊处理
    def __clean4XML(self, fieldName, fieldValue):
        res = fieldValue
        if fieldName == 'SFZZYJH':
            if res == '1':
                res = '2'
            elif res == '2':
                res = '1'
        return res
    
    def __clean4Date(self, fieldName, fieldValue):
        res = fieldValue
        if C_Date.has_key(fieldName):
            parseRes = True
            try:
                d = datetime.datetime.strptime(res, u'%Y年%m月%d日')
                res = d.strftime('%Y-%m-%d')
            except Exception, e:
                parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, '%Y-%m-%d')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, '%Y%m%d')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, '%Y-%m-%d %H:%M:%S')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, '%Y/%m/%d %H:%M:%S')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, '%Y/%m/%d')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, '%m/%d/%Y')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                try:
                    d = datetime.datetime.strptime(res, 'The %B %d %H:%M;%S %Z %Y')
                    res = d.strftime('%Y-%m-%d')
                    parseRes = True
                except Exception, e:
                    parseRes = False

            if not parseRes:
                ls = re.compile(r'[0-9]').findall(res)
                if len(ls) > 0:
                    res = ''.join(ls)
                    res = res[0:8]

        return res

    def __clean4KexueJishu(self, fieldName, fieldValue):
        res = fieldValue
        if C_KexueJishu.has_key(fieldName):
            parseRes = False
            if res.find('e') != -1 or res.find('E') != -1:
                try:
                    if res.find('-') != -1:   #说明是小于1的小数
                        res = '{:f}'.format(eval(res))      #这里不知道要保留几位小数合适。。。
                    else:
                        res = '{:.0f}'.format(eval(res))
                    parseRes = True
                except Exception, e:
                    parseRes = False

            # 身份证号什么的可能会有字母，所以最后一步不要做这个处理
            # if not parseRes:
            #     ls = re.compile(r'[0-9]').findall(res)
            #     res = ''.join(ls)
                
        return res

    def __clean4CRYKB(self, fieldName, fieldValue):
        res = fieldValue
        if C_CRYKB.has_key(fieldName):
            #res = unicode(res, "utf-8")        #这里不转换了，因为传过来的会转
            # 先看最后两位是不是'.0',是则去掉，再看最后三位是不是'.00'，是则去掉
            if len(res) >= 2:
                if res[len(res)-2:len(res)] == '.0':
                    res = res[0:len(res)-2]
            if len(res) >= 3:
                if res[len(res)-3:len(res)] == '.00':
                    res = res[0:len(res)-3]

            regex = re.compile(u'[\u4E00-\u9FD5]')
            ls = regex.findall(res)
            if len(ls) == 0:    #没有匹配到汉字
                ls = re.compile(r'[0-9.]').findall(res)
                res = ''.join(ls)
                if res.find('.') == -1:     #不包含小数点
                    if len(res) == 1:
                        res = '0%s' % res
                    elif len(res) == 3:
                        if res[0] == '0':
                            res = '%s0%s' %(res[0:2],res[2])
                        else:
                            res = '0%s' % res
                        res = '%s.%s' % (res[0:2], res[2:4])
                    elif len(res) == 4:
                        res = '%s.%s' % (res[0:2], res[2:4])
                    elif len(res) == 5:
                        if res[0] == '0':
                            res = '%s0%s' %(res[0:4], res[4])
                        else:
                            res = '0%s' % res
                        res = '%s.%s.%s' % (res[0:2], res[2:4], res[4:6])
                    elif len(res) >= 6:
                        res = res[0:6]
                        res = '%s.%s.%s' % (res[0:2], res[2:4], res[4:6])
                else:
                    ls = res.split('.')
                    if len(ls) == 2:
                        left = ls[0]
                        right = ls[1]

                        if len(left) < 2:
                            left = '0%s' % left
                        if len(right) < 2:
                            right = '0%s' % right
                        res = '%s.%s' % (left, right)
                    elif len(ls) >= 3:
                        left = ls[0]
                        mid = ls[1]
                        right = ls[2]

                        if len(left) < 2:
                            left = '0%s' % left
                        if len(mid) < 2:
                            mid = '0%s' % mid
                        if len(right) < 2:
                            right = '0%s' % right
                        res = '%s.%s.%s' % (left, mid, right)
        return res

    #这个跟老徐确认直接简单粗暴的把.00,.0替换成没有即可
    def __clean4Int(self, fieldName, fieldValue):
        res = fieldValue
        if C_Int.has_key(fieldName):
            res = res.replace('.00','')
            res = res.replace('.0','')
            # try:
            #     f = float(res)
            #     res = str(int(f))
            # except Exception,e:
            #     regex = re.compile(r'[0-9]')
            #     ls = regex.findall(res)
            #     if len(ls) > 0:
            #         res = ''.join(ls)
            #         res = str(int(res))
            #     else:
            #         res = '0'
        return res
    
    #处理成带两位小数那样的字符串
    def __clean4Float(self, fieldName, fieldValue):
        res = fieldValue
        if C_Float.has_key(fieldName):
            regex = re.compile(r'[0-9.]')
            ls = regex.findall(res)
            if len(ls) > 0:
                tmpStr = ''.join(ls)
                i = 0
                for s in tmpStr:
                    if s=='0':
                        i+=1
                    else:
                        break
                tmpRes = tmpStr[i:]
                try:
                    f = float(tmpRes)
                    res = '%.2f' % f
                except:
                    res = '0'
            else:
                res = '0'
        return res

    #专门处理NL字段
    def __clean4NL(self, fieldName, fieldValue):
        res = fieldValue
        if fieldName == "NL":
            res = res.replace(u'个','')
            index = res.find('Y')
            if index == -1:
                index = res.find(u'年')
            if index != -1:     #找到年了
                if index-2 < 0:
                    tmpRes = res[0:index]
                else:
                    tmpRes = res[index-2:index]
                if len(tmpRes) > 0:
                    res = tmpRes
                else:
                    tmpRes = res[index+1:index+3]
                    
                    res = tmpRes
                ls = re.compile(r'[0-9]').findall(res)
                res = ''.join(ls)
                try:
                    res = str(int(res))
                except:
                    res = '0'
            else:
                index = res.find('M')
                isHanzi = False
                if index == -1:
                    index = res.find(u'月')
                if index != -1:     #找到月了
                    if index-2 < 0:
                        tmpRes = res[0:index]
                    else:
                        tmpRes = res[index-2:index]
                    if len(tmpRes) > 0:
                        res = tmpRes
                    else:
                        tmpRes = res[index+1:index+3]
                        res = tmpRes
                    ls = re.compile(r'[0-9]').findall(res)
                    res = ''.join(ls)
                    try:
                        m = int(res)
                    except:
                        m = 0
                    res = str(m/12)
            if index == -1:     #年和月都没有找到
                if res.find('D') != -1 or res.find(u'天') != -1 or res.find(u'日') != -1 or res.find('H') != -1 or res.find(u'时') != -1 or res.find('S') != -1 or res.find(u'分') != -1:
                    res = '0'
                else:
                    ls = re.compile(r'[0-9]').findall(res)
                    if len(ls) > 0:
                        res = ''.join(ls)
                        res = str(int(res[0:2]))
                    else:
                        res = '0'
        return res

    #专门处理BZYZSNL字段
    def __clean4BZYZSNL(self, fieldName, fieldValue):
        res = fieldValue
        if fieldName == 'BZYZSNL':
            try:
                res = float(res)
                if res > 1:
                    res = '%.2f' % res
                else:
                    res = '0.5'
            except:
                if res.find(' ') != -1:
                    res = res.split(' ')[0]
                    try:
                        i = int(res)
                        if i > 1:
                            res = str(i)
                        else:
                            res = '0.5'
                    except:
                        res = '0'
                elif res.find('/') != -1:
                    ls = res.split('/')
                    left = ls[0]
                    right = ls[1]
                    try:
                        l = float(left)
                        try:
                            r = float(right)
                            tmpRes = l / r
                            if tmpRes > 1:
                                res = '%.2f' % tmpRes
                            else:
                                res = '0.5'
                        except:
                            res = '0'
                    except:
                        res = '0'
                else:
                    ls = re.compile(r'[0-9]').findall(res)
                    if len(ls) > 0:
                        res = ''.join(ls)
                        res = res[0:2]
                        res = str(int(res))
                    else:
                        res = '0'
        return res
    
    #专门处理编码字段，只保留字母、数字、加号、小数点、斜杠
    def __clean4BianMa(self, fieldName, fieldValue):
        res = fieldValue
        if C_BianMa.has_key(fieldName):
            regex = re.compile(r'[0-9a-zA-Z+./]')
            ls = regex.findall(res)
            res = ''.join(ls)
        return res

    #如果这些字段里只填写了一个减号则当成没有填写，直接返回空串
    def __clean4Jianhao(self, fieldName, fieldValue):
        res = fieldValue
        if C_Jianhao.has_key(fieldName):
            if fieldValue == '-':
                res = ''
        return res

    #专门处理名族字段，这个字段里原则上只会有1~9，或者对应的前面加0的
    def __clean4MZ(self, fieldName, fieldValue):
        res = fieldValue
        if fieldName == 'MZ':
            if len(fieldValue) == 1 and fieldValue in ('1','2','3','4','5','6','7','8','9'):
                res = '0%s' % fieldValue

        return res

    #专门针对YLFKFS字段做处理，1~9变成01~08和99
    def __clean4YLFKFS(self, fieldName, fieldValue):
        res = fieldValue
        if fieldName == 'YLFKFS':
            if len(fieldValue) == 1:
                if fieldValue in ('1','2','3','4','5','6','7','8'):
                    res = '0%s' % fieldValue
                elif fieldValue == '9':
                    res = '99'
        return res

    #专门处理GX字段，主要是要把9变成8
    def __clean4GX(self, fieldName, fieldValue):
        res = fieldValue
        if fieldName == 'GX':
            if fieldValue == '9':
                res = '8'
        return res

    #去除斜杠
    def __clean4XieGang(self, fieldName, fieldValue):
        res = fieldValue
        if not C_BaoLiuXieGang.has_key(fieldName):
            res = res.replace("/","")
        return res

if __name__ == "__main__":
    dc = DataClean()
    print(dc.cleanByField('NL',u'62','XML'))





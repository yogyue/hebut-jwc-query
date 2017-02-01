# coding=utf-8
import urllib
import urllib2
import cookielib
import random

from bs4 import BeautifulSoup

import sys
import os

# print sys.getdefaultencoding()
# print sys.stdout.encoding

# urlib的使用
# blog reference http://python.jobbole.com/81344/

# python2的编码问题
# http://www.cnblogs.com/ymy124/archive/2012/06/23/2559282.html

class WebJWC(object):
    def __init__(self):
        self.__openLog = False
        self.__opener = None
        self.__headers = {
            'Accept': 'application/x-ms-application, image/jpeg, application/xaml+xml, image/gif, image/pjpeg, application/x-ms-xbap, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)'
        }
        self.__validatePicName = u'_validatePic.jpg'

    def openLog(self):
        self.__openLog = True

    def closeLog(self):
        self.__openLog = False

    def log(self, str=u'...'):
        if self.__openLog:
            print(u'-->' + u' [Log] ' + str)

    def tip(self, str=u'...'):
        print(u'-->' + u' [Tip] ' + str)

    def printScoreInfo(self,scoreName = u'defaultName' , scoreXF = u'defaultXF',scoreType = u'必修|选秀',score = u'defaultScore'):
        # 关于\xa0问题
        # http://www.cnblogs.com/zhaoyl/p/3770340.html
        unstr = (u'-->' + u' [Score] ' + scoreName + u' ' + scoreXF + u'学分' + u' ' + scoreType + u' 分数:' + score).replace(u'\xa0', u' ')
        print(unstr)

    def showValidatePicture(self):
        # 不同的操作系统打开文件的方式不同
        if sys.platform.startswith('win'):
            os.startfile(self.__validatePicName)
        else:
            self.tip(u'验证码图片已保存到当前目录 ' + self.__validatePicName + u' 请自行打开查看验证码 (我懒得解决其他平台下的图片打开问题了)')

    def login(self):
        # DebugLog
        # httpHandler = urllib2.HTTPHandler(debuglevel=1)
        # httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
        # opener = urllib2.build_opener(httpHandler, httpsHandler)
        # urllib2.install_opener(opener)
        self.tip(u'正在访问登陆页面...')
        cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

        try:
            request = urllib2.Request(u"http://115.24.160.162/", headers=self.__headers)
            response = opener.open(request)
        except urllib2.URLError, e:
            if hasattr(e, 'code'):
                self.log(u'Error HTTP : ' + str(e.code).decode())
            if hasattr(e, 'reason'):
                self.log(u'Error : ' + str(e.reason).decode())
            self.tip(u'登陆页面请求失败 :(')
            return False
        else:
            self.__opener = opener
            self.log(u'request success {Login Page}')
            self.log(u'cookie info : ')
            # print type(str(cookie)) # str
            # print type(cookie) # instance
            self.log(str(cookie).decode())
        finally:
            response.close()

        # get validate picture
        self.log(u'prepare to download the verification picture')
        # chrome F12 : /validateCodeAction.do?random=Math.random()
        pictureURL = u'http://115.24.160.162/validateCodeAction.do?random=' + str(random.random()).decode()
        self.log(u'verification picture url : ')
        self.log(pictureURL)
        request = urllib2.Request(pictureURL, headers=self.__headers)
        try:
            response = self.__opener.open(request)
            mfile = open(self.__validatePicName, 'wb')
            mfile.write(response.read())
        except:
            self.tip(u'验证码操作失败 :(')
            return False
        else:
            self.log(u'request success {validate Picture}')
        finally:
            mfile.close()
            response.close()

        # show validate picture
        self.showValidatePicture()

        # user info
        while True:
            # python2 遗留问题,为了适配windows和Linux控制台，没有想出更好的办法
            if sys.platform.startswith('win'):
                username = raw_input(u'[*] 请输入学号 : '.encode('gbk')).decode('gbk')
                password = raw_input(u'[*] 请输入密码 : '.encode('gbk')).decode('gbk')
                validateCode = raw_input(u'[*] 请输入验证码 : '.encode('gbk')).decode('gbk')
                confirm = raw_input(u'[*] 请确认 Y/N : '.encode('gbk')).decode('gbk')
            else:
                username = raw_input(u'[*] 请输入学号 : '.encode('utf-8')).decode('utf-8')
                password = raw_input(u'[*] 请输入密码 : '.encode('utf-8')).decode('utf-8')
                validateCode = raw_input(u'[*] 请输入验证码 : '.encode('utf-8')).decode('utf-8')
                confirm = raw_input(u'[*] 请确认 Y/N : '.encode('utf-8')).decode('utf-8')
            '''
            username = raw_input(u'[*] 请输入学号 : ')#.decode('gbk')
            password = raw_input(u'[*] 请输入密码 : ')#.decode('gbk')
            validateCode = raw_input(u'[*] 请输入验证码 : ')#.decode('gbk')
            confirm = raw_input(u'[*] 请确认 Y/N : ')#.decode('gbk')
            '''
            if confirm == u'y' or confirm == u'Y':
                break

        # login
        self.log(u'prepare to login')
        postdata = urllib.urlencode({
            'zjh': username,
            'mm': password,
            'v_yzm': validateCode
        })
        request = urllib2.Request('http://115.24.160.162/loginAction.do', data=postdata, headers=self.__headers)
        try:
            response = self.__opener.open(request)
        except:
            self.log(u'login error')
            return False
        else:
            self.log(u'request success {Login Action}')
            # jwc网站html是用gbk进行编码的
            loginHtml = response.read().decode('gbk')
            # self.log(u'returned HTML : ')
            # self.log(loginHtml)
        finally:
            response.close()

        # confirm login success or failed
        soup = BeautifulSoup(loginHtml)
        # type(soup.title.string) -> NavigableString extends unicode,object
        self.log(u'document.head.title = ' + soup.title.string)
        if soup.title.string == u'学分制综合教务':
            self.tip(u'登陆成功')
            return True
        else:
            self.log(u'login failed')
            message = soup.find('strong').string
            self.tip(message)
        return False

    def queryAllScore(self):
        # Chrome F12 : 'http://115.24.160.162/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2016-2017学年秋(两学期)'
        self.tip(u'正在查询您的所有成绩')
        getData = {
            'type':'ln',
            'oper':'qbinfo',
            'lnxndm':u'2016-2017学年秋(两学期)'.encode('gbk')
        }
        data = urllib.urlencode(getData)
        queryAllURL = u'http://115.24.160.162/gradeLnAllAction.do?' + data
        self.log(u'query all score URL : ')
        self.log(queryAllURL)
        request = urllib2.Request( queryAllURL , data=None, headers=self.__headers)
        try:
            response = self.__opener.open(request)
            allScoreHTML = response.read().decode('gbk')
        except urllib2.URLError,e:
            self.log(u'query all score Error')
            print e
        finally:
            response.close()

        # parse score info
        soup = BeautifulSoup(allScoreHTML)
        scoreTRList = soup.find_all('tr',class_='odd')
        for trTag in scoreTRList:
            scoreName = trTag.contents[5].string.replace('\r','').replace('\n','').replace(' ','')
            scoreXF = trTag.contents[9].string.replace('\r','').replace('\n','').replace(' ','')
            scoreType = trTag.contents[11].string.replace('\r','').replace('\n','').replace(' ','')
            score = trTag.contents[13].p.string.replace('\r','').replace('\n','').replace(' ','')
            self.printScoreInfo(scoreName=scoreName,scoreXF=scoreXF,scoreType=scoreType,score=score)
        #
        self.tip(u'---------------------------------------')
        pass

    def queryFailedCourse(self):
        self.tip(u'正在查询您的挂科成绩')
        # Chrome F12 : http://115.24.160.162/gradeLnAllAction.do?type=ln&oper=bjg
        getData = {
            'type': 'ln',
            'oper': 'bjg'
        }
        data = urllib.urlencode(getData)
        queryGKURL = u'http://115.24.160.162/gradeLnAllAction.do?' + data
        self.log(u'query unpassed score URL : ')
        self.log(queryGKURL)
        request = urllib2.Request(queryGKURL, data=None, headers=self.__headers)
        try:
            response = self.__opener.open(request)
            GKScoreHTML = response.read().decode('gbk')
        except urllib2.URLError,e:
            self.log(u'query unpassed score Error')
            print e
        finally:
            response.close()

        # pass score info
        soup = BeautifulSoup(GKScoreHTML)
        scoreTRList = soup.find_all('tr', class_='odd')
        for trTag in scoreTRList:
            scoreName = trTag.contents[5].string.replace('\r', '').replace('\n', '').replace(' ', '')
            scoreXF = trTag.contents[9].string.replace('\r', '').replace('\n', '').replace(' ', '')
            scoreType = trTag.contents[11].string.replace('\r', '').replace('\n', '').replace(' ', '')
            score = trTag.contents[13].p.string.replace('\r', '').replace('\n', '').replace(' ', '')
            self.printScoreInfo(scoreName=scoreName, scoreXF=scoreXF, scoreType=scoreType, score=score)
        #
        self.tip(u'---------------------------------------')
        pass

    def __exit(self):
        self.__opener = None
        pass

    def start(self):
        while True:
            if self.login():
                break
        while True:
            self.tip(u'* 1 查询我的全部成绩')
            self.tip(u'* 2 查询不及格成绩')
            self.tip(u'* 3 退出')
            if sys.platform.startswith('win'):
                choice = raw_input(u'请输入:'.encode('gbk')).decode('gbk')
            else:
                choice = raw_input(u'请输入:'.encode('utf-8')).decode('utf-8')
            if choice == u'3':
                 break
            elif choice == u'2':
                self.queryFailedCourse()
            elif choice == u'1':
                self.queryAllScore()
            else:
                self.tip(u'错误 请重新输入')
        self.__exit()


if __name__ == '__main__':
    jwc = WebJWC()
    jwc.openLog()
    jwc.start()

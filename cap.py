#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Image
import urllib2, cookielib
import gzip, string, random, os, time, sys
import threading
from StringIO import StringIO

count = 0
imgWidth = 15
imgHeight = 26
imageDic = dict()
path = './sample/'
table = [i / 254 for i in range(256)]
lock = threading.RLock()
log = open("log.txt", 'w')

commonHeader =  {'Host':'www.7do.net',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip,deflate,sdch',
'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
}

def initSamples():
    for parent,dirnames,filenames in os.walk(path): 
        for filename in filenames:
            if filename[:1] != '.':
                img = Image.open(path + filename)
                imageDic[filename[:-4]] = img.load()

def compareImg(imgData):
    minimal = imgHeight * imgWidth
    for k, v in imageDic.iteritems():
        difference = 0
        for y in xrange(imgHeight):
            for x in xrange(imgWidth):
                if v[x, y] != imgData[x, y]:
                    difference = difference + 1
        if difference < minimal:
            minimal = difference
            key = k[:1]
    return key

def getSubStr(str, prefix, sufix, begin = 0):
    start = str.find(prefix, begin)
    pos = start + len(prefix)
    return str[pos : str.find(sufix, pos)], pos

def randomStr():
    letters = string.ascii_letters
    return ''.join([random.choice(letters) for _ in range(5)])

def processImage(data, img):
    if not img:
        img = Image.open(StringIO(data))
    img = img.convert("RGB")
    # global imgName
    # img.save(str(imgName) + '.png')
    # imgName = imgName + 1
    # img.save('dl.png')
    pixdata = img.load()

    white = (255, 255, 255)
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if (pixdata[x, y][0] + pixdata[x, y][1] + pixdata[x, y][2] == 0) or (x + 1 < img.size[0] and pixdata[x, y] == pixdata[x + 1, y]) or (x > 0 and pixdata[x, y] == pixdata[x - 1, y]):
                pass
            else:
                pixdata[x, y] = white

    findBlack = True
    px = []
    for x in xrange(img.size[0]):
        if findBlack:
            for y in xrange(img.size[1]):
                if pixdata[x, y] != white:
                    findBlack = not findBlack
                    px.append(x)
                    break
        else:
            allWhite = True
            for y in xrange(img.size[1]):
                if pixdata[x, y] != white:
                    allWhite = False
                    break
            if allWhite:
                findBlack = not findBlack
                px.append(x)
    if len(px) == 7:
        px.append(img.size[0] - 1)

    # log.write(str(px) + '\n')

    py = []
    for i in xrange(len(px) / 2):
        findBlack = True
        for j in xrange(img.size[1]):
            if findBlack:
                for k in xrange(px[i * 2], px[i * 2 + 1]):
                    if pixdata[k, j] != white:
                        py.append(j)
                        findBlack = not findBlack
                        break
            else:
                allWhite = True
                for k in xrange(px[i * 2], px[i * 2 + 1]):
                    if pixdata[k, j] != white:
                        allWhite = False
                        break
                if allWhite:
                    py.append(j)
                    break
                elif j == img.size[1] - 1:
                    py.append(j) 
    # log.write(str(py) + '\n')
    
    ret = ''
    for i in xrange(4):
        result = img.crop((px[2 * i], py[2 * i], px[2 * i + 1], py[2 * i + 1])).resize((imgWidth, imgHeight))
        result = result.convert('L')
        result = result.point(table, '1')
        char = compareImg(Image.fromstring('1', (imgWidth, imgHeight), result.tostring()).load())
        if char == '':
            print("error return")
        ret = ret + char
    
    return ret

class register(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self, name = name)
        self.cj = cookielib.LWPCookieJar(name)
        self.header = commonHeader.copy()

    def initWeb(self):
        self.cj.revert('cookieTemplate.txt')
        self.cj.save(ignore_discard = True, ignore_expires = True)
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.header['X-Forwarded-For'] = '{0}.{1}.{2}.{3}'.format(random.randrange(255), random.randrange(255), random.randrange(255), random.randrange(255))


    def req(self, url, unzip = True, data = None, specail = False):
        request = urllib2.Request(url = url, data = data, headers = self.header)
        response = self.opener.open(request)
        headers = str(response.headers.headers)
        # if specail:
            # log.write(headers + '\n')
        rawdata = response.read()
        self.cj.save(ignore_discard = True, ignore_expires = True)
        if specail and str(headers).find('creditnotice') > 0:
            lock.acquire()
            log.write("**********************success**************************\n")
            lock.release()

        if not unzip:
            return rawdata
        return gzip.GzipFile(fileobj = StringIO(rawdata)).read()

    def doRequests(self):
        self.req('http://www.7do.net/?fromuser=Tdfh')
        
        self.header["Referer"] = 'http://www.7do.net/?fromuser=Tdfh'
        self.req('http://www.7do.net/home.php?mod=misc&ac=sendmail&rand=' + str(int(time.time())))
        self.req('http://www.7do.net/member.php?mod=logging&action=login&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login')
        webContent = self.req('http://www.7do.net/member.php?mod=register')

        hashid = getSubStr(webContent, 'sechash" type="hidden" value="', '"')[0]
        name, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"')
        password, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"', begin)
        passwordConfirm, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"', begin)
        email, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"', begin)

        self.header['Referer'] = 'http://www.7do.net/member.php?mod=register'
        self.req('http://www.7do.net/home.php?mod=misc&ac=sendmail&rand=' + str(int(time.time())))

        while True:
            url = 'http://www.7do.net/misc.php?mod=seccode&action=update&idhash={0}&inajax=1&ajaxtarget=seccode_{1}'.format(hashid, hashid)
            content = self.req(url)

            pa = 'src="'
            params = getSubStr(content, pa, '"')[0]

            url = 'http://www.7do.net/' + params
            captcha = self.req(url, False)

            cap = processImage(captcha, None)
            log.write(cap + '\n')

            self.header['X-Requested-With'] = 'XMLHttpRequest'
            url = 'http://www.7do.net/misc.php?mod=seccode&action=check&inajax=1&&idhash='+ hashid + '&secverify=' + cap
            answer = self.req(url)
            del self.header['X-Requested-With']

            lock.acquire()
            log.write(answer + '\n')
            lock.release()

            if answer.find('invalid') <= 0:
                lock.acquire()
                log.write('valid')
                lock.release()
                break

        username = randomStr()
        userEmail = randomStr() + random.choice(('@126.com', '@qq.com', '@163.com', '@gmail.com', '@hotmail.com'))

        data = '''------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="regsubmit"\r
\r
yes\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="formhash"\r
\r
6fb000ad\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="referer"\r
\r
http://www.7do.net/?fromuser=Tdfh\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="activationauth"\r
\r
\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="{0}"\r
\r
{1}\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="{2}"\r
\r
111111\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="{3}"\r
\r
111111\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="{4}"\r
\r
{5}\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="sechash"\r
\r
{6}\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="seccodeverify"\r
\r
{7}\r
------WebKitFormBoundary3untao1xYPCyrRO1\r
Content-Disposition: form-data; name="regsubmit"\r
\r
true\r
------WebKitFormBoundary3untao1xYPCyrRO1--'''.format(name, username, password, passwordConfirm, email, userEmail, hashid, cap)
        # print(data)

        self.header['Content-Type'] = 'multipart/form-data; boundary=----WebKitFormBoundary3untao1xYPCyrRO1'
        self.req('http://www.7do.net/member.php?mod=register&inajax=1', True, data, True)
        del self.header['Content-Type']

    def run(self):
        global count
        while True:
            lock.acquire()
            if count == 0:
                lock.release()
                break
            print('count is', count)
            count = count - 1
            lock.release()
            
            self.initWeb()
            self.doRequests()
        os.remove(self.cj.filename)
        print(self.getName() + ' finished')

if __name__ == '__main__':
    if len(sys.argv) != 2 :
        print("Enter a count")
        exit()
    count = int(sys.argv[1])
    initSamples()

    threadCount = min(count, 10)
    for x in xrange(threadCount):
        thread = register(str(x))
        thread.start()
    log.close()
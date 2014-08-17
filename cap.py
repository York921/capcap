#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Image, pytesseract
import urllib2, cookielib,Cookie
from StringIO import StringIO
import gzip, re, string, random, os, time

imgWidth = 15
imgHeight = 26
imageDic = dict()
cj = None
path = '/Users/yangtianyu/Develop/captcha/sample/'
header =  {'Host':'www.7do.net',
'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip,deflate,sdch',
'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
}

table = []
for i in range(256):
    if  i < 254:
        table.append(0)
    else:
        table.append(1)

def compareImg(imgData):
    minimal = imgHeight * imgWidth
    key = ''
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

def initSamples():
    for parent,dirnames,filenames in os.walk(path): 
        for filename in filenames:
            if filename[:1] != '.':
                img = Image.open(path + filename)
                imageDic[filename[:-4]] = img.load()

def initWeb():
    global cj
    cj = cookielib.LWPCookieJar('cookie.txt')
    cj.load('cookieTemplate.txt')
    cj.save(ignore_discard=True, ignore_expires=True)

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    header['X-Forwarded-For'] = '{0}.{1}.{2}.{3}'.format(random.randrange(255), random.randrange(255), random.randrange(255), random.randrange(255))

def req(header, data, url, unzip = True, specail = False):
    request = urllib2.Request(url = url,data = data, headers = header)
    response = urllib2.urlopen(request)
    headers = str(response.headers.headers)
    if specail:
        print(headers)
    rawdata = response.read()
    cj.save(ignore_discard = True, ignore_expires = True)
    if specail:
        if str(headers).find('creditnotice') > 0:
                print("**********************success**************************")

    if not unzip:
        return rawdata
    return gzip.GzipFile(fileobj = StringIO(rawdata)).read()

def getSubStr(str, prefix, sufix, begin = 0):
    start = str.find(prefix, begin)
    pos = start + len(prefix)
    return str[pos : str.find(sufix, pos)], pos

def randomStr():
    letters=string.ascii_letters
    return ''.join([random.choice(letters) for _ in range(5)])

def processImage(data, img):
    if not img:
        img = Image.open(StringIO(data))
    img = img.convert("RGB")
    # img.save('dl.png')
    pixdata = img.load()

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if (pixdata[x, y][0] + pixdata[x, y][1] + pixdata[x, y][2] == 0) or (x + 1 < img.size[0] and pixdata[x, y] == pixdata[x + 1, y]) or (x > 0 and pixdata[x, y] == pixdata[x - 1, y]):
                pass
            else:
                pixdata[x, y] = (255,255,255)

    findBlack = True
    px = []
    for x in xrange(img.size[0]):
        if findBlack:
            for y in xrange(img.size[1]):
                if pixdata[x, y] != (255, 255, 255):
                    findBlack = not findBlack
                    px.append(x)
                    break
        else:
            allWhite = True
            for y in xrange(img.size[1]):
                if pixdata[x, y] != (255, 255, 255):
                    allWhite = False
                    break
            if allWhite:
                findBlack = not findBlack
                px.append(x)
    # print(px)

    py = []
    for i in xrange(len(px) / 2):
        findBlack = True
        for j in xrange(img.size[1]):
            if findBlack:
                for k in xrange(px[i * 2],px[i * 2 + 1]):
                    if pixdata[k, j] != (255, 255, 255):
                        py.append(j)
                        findBlack = not findBlack
                        break
            else:
                allWhite = True
                for k in xrange(px[i * 2],px[i * 2 + 1]):
                    if pixdata[k, j] != (255, 255, 255):
                        allWhite = False
                        break
                if allWhite:
                    py.append(j)
                    break
                elif j == img.size[1] - 1:
                    py.append(j) 
    # print(py)
    
    ret = ''
    for i in xrange(4):
        result = img.crop((px[2 * i], py[2 * i], px[2 * i + 1], py[2 * i + 1])).resize((imgWidth, imgHeight))
        result = result.convert('L')
        result = result.point(table, '1')
        result.save('s.png')
        char = compareImg(Image.open('s.png').load())
        if char == '':
            print("error return")
        ret = ret + char
    
    return ret

def doRequests():

    req(header, None, 'http://www.7do.net/?fromuser=Tdfh')
    
    header["Referer"] = 'http://www.7do.net/?fromuser=Tdfh'
    req(header, None, 'http://www.7do.net/home.php?mod=misc&ac=sendmail&rand=' + str(int(time.time())))

    copyHeader = header.copy()
    req(copyHeader , None, 'http://www.7do.net/member.php?mod=logging&action=login&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login')

    webContent = req(header, None, 'http://www.7do.net/member.php?mod=register')

    hashid = getSubStr(webContent, 'sechash" type="hidden" value="', '"')[0]

    formhash = getSubStr(webContent, 'formhash" value="', '"')[0]

    name, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"')
    password, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"', begin)
    passwordConfirm, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"', begin)
    email, begin = getSubStr(webContent, '<th><span class="rq">*</span><label for="', '"', begin)

    header['Referer'] = 'http://www.7do.net/member.php?mod=register'
    req(header, None, 'http://www.7do.net/home.php?mod=misc&ac=sendmail&rand=' + str(int(time.time())))

    cap = ''
    while True:
        url = 'http://www.7do.net/misc.php?mod=seccode&action=update&idhash={0}&inajax=1&ajaxtarget=seccode_{1}'.format(hashid, hashid)
        content = req(header, None, url)

        pa = 'src="'
        params = getSubStr(content, pa, '"')[0]

        url = 'http://www.7do.net/' + params
        captcha = req(header, None, url, False)

        cap = processImage(captcha, None)
        print(cap)

        url = 'http://www.7do.net/misc.php?mod=seccode&action=check&inajax=1&&idhash='+ hashid + '&secverify=' + cap
        answer = req(copyHeader, None, url)
        print(answer)
        if answer.find('invalid') <= 0:
            break

    username = randomStr()
    userEmail = randomStr() + '@126.com'
    copyHeader = header.copy()
    copyHeader['X-Requested-With'] = 'XMLHttpRequest'
    url = 'http://www.7do.net/forum.php?mod=ajax&inajax=yes&infloat=register&handlekey=register&ajaxmenu=1&action=checkusername&username=' + username
    req(copyHeader, None, url)

    url = 'http://www.7do.net/forum.php?mod=ajax&inajax=yes&infloat=register&handlekey=register&ajaxmenu=1&action=checkemail&email=' + userEmail
    req(copyHeader, None, url)

    url = 'http://www.7do.net/misc.php?mod=seccode&action=check&inajax=1&&idhash='+ hashid + '&secverify=' + cap
    answer = req(copyHeader, None, url)

    while answer.find('invalid') > 0:
        url = 'http://www.7do.net/misc.php?mod=seccode&action=update&idhash={0}&inajax=1&ajaxtarget=seccode_{1}'.format(hashid, hashid)
    
        content = req(header, None, url)

        pa = 'src="'
        params = getSubStr(content, pa, '"')[0]

        url = 'http://www.7do.net/' + params
        # print(url)
        captcha = req(header, None, url, False)

        cap = processImage(captcha, None)
        url = 'http://www.7do.net/misc.php?mod=seccode&action=check&inajax=1&&idhash='+ hashid + '&secverify=' + cap
        answer = req(copyHeader, None, url)
    print('valid')
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

    header['Content-Type'] = 'multipart/form-data; boundary=----WebKitFormBoundary3untao1xYPCyrRO1'

    req(header, data, 'http://www.7do.net/member.php?mod=register&inajax=1', True, True)


initSamples()

times = 0
while times < 1:
    initWeb()
    doRequests()
    times = times + 1


# print(processImage(None, Image.open('misc.png')))#/Users/yangtianyu/Desktop/captcha.png')))
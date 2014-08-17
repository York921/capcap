#! /usr/bin/env python
# -*- coding: utf-8 -*-

import Image, pytesseract
import urllib2, cookielib 
from StringIO import StringIO
import gzip, re, string, random, os
imgWidth = 15
imgHeight = 26

table = []
for i in range(256):
    if  i < 254:
        table.append(0)
    else:
        table.append(1)

def processImage(data, img):
    if not img:
        img = Image.open(StringIO(data))
        img.save("or.png")
    img = img.convert("RGB")

    pixdata = img.load()

    # seq = list(img.getdata())
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if (pixdata[x, y][0] + pixdata[x, y][1] + pixdata[x, y][2] == 0) or (x + 1 < img.size[0] and pixdata[x, y] == pixdata[x + 1, y]) or (x > 0 and pixdata[x, y] == pixdata[x - 1, y]):
                pass
            else:
                pixdata[x, y] = (255,255,255)

    findBlack = True
    px = []
    for x in xrange(img.size[0]):
        # find = False
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
    print(px)

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
    print(py)
    
    x = 0
    y = imgHeight
    ret = ''
    num = 1
    for i in xrange(4):
        # result = Image.new("RGB", (imgWidth, imgHeight), (255, 255, 255))
        result = img.crop((px[2 * i], py[2 * i], px[2 * i + 1], py[2 * i + 1])).resize((imgWidth, imgHeight))
        # x = x + imgWidth + 5
        result = result.convert('L')
        result = result.point(table, '1')
        result.save('/Users/yangtianyu/Develop/captcha/wwwwwwwww' + str(num) + '.png')
        num = num + 1
    return ret

# processImage(None, Image.open('/Users/yangtianyu/Desktop/captcha.png'))

imageDic = dict()
imageDic['4'] = list(Image.open('wwwwwwwww1.png').getdata())

def compareImg(imgData):
    print('compare****', imgData)
    print(imageDic['4'])
    minimal = imgHeight * imgWidth
    key = ''
    for k, v in imageDic.iteritems():
        difference = 0
        for idx, d in enumerate(imgData):
            if d != v[idx] :
                difference = difference + 1
        # for y in xrange(imgHeight):
        #     for x in xrange(imgWidth):
        #         # print(v[x, y], imgData[x, y])
        #         if v[x, y] != imgData[x, y]:
        #             difference = difference + 1
        print('diff',k, difference)
        if difference < minimal:
            minimal = difference
            key = k[:1]
    return key

compareImg(list(Image.open('wtf.png').getdata()))
    # result = result.point(table, '1')
    # result.save('re.png')
    # cap = pytesseract.image_to_string(result)    
    # print("cap is", cap)
    # return cap`
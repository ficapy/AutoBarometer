#!/usr/bin/env python
#coding=utf-8
#Author:ficapy<c4d@outlook.com>
#       http://zoulei.net
#Version:0.1
#Create on 2014-03-19

import os
import urllib2
import codecs
import time
import re
from PIL import Image
from selenium import webdriver

#获取海口今天最高气温和最低气温及天气状况
def query(y,m,d,h):
    weurl = 'http://www.accuweather.com/zh/cn/rongshan/58633/weather-forecast/58633'
    headers = { 'Use-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6' }
    #获取今日当时天气
    wereq = urllib2.Request(weurl, headers=headers)
    wecontent = urllib2.urlopen(wereq).read()
    weather = re.search(r'<span class="cond">(.+?)</span>',wecontent).group(1).decode('utf-8')

    #获取最高和最低气温
    temp = re.findall(r'<strong class="temp">(\d+)<span>',wecontent)
    high = temp[1].decode('gbk')
    low = temp[2].decode('gbk')

    #该列表只包含白天晴及阴的状况
    tianqi = output(weather)

    if int(h) <= 11:
        amfile = codecs.open(r'.{}AutoBarometer{}result.txt'.format(os.sep,os.sep),"w",'gbk')
        pmfile = codecs.open(r'.{}AutoBarometer{}bak.txt'.format(os.sep,os.sep),"r",'gbk')
        am = ' '.join(
            (unicode(y),unicode(m),unicode(d),unicode(h),high,low,weather,weather,tianqi,tianqi)
        )
        wlist = ''
        for line in pmfile:
            wlist += line

        wlist+= am
        amfile.write((wlist+u'\r\n'))
    if int(h) >= 12:
        amfile = codecs.open(r'.{}AutoBarometer{}result.txt'.format(os.sep,os.sep),"r",'gbk')
        pmfile = codecs.open(r'.{}AutoBarometer{}bak.txt'.format(os.sep,os.sep),"w",'gbk')
        wlist = ''
        reobject = re.compile(u'^{} {} {} \d+ \d+ \d+ \S+ (\S+) \S+ (\S+)'.format(y,m,d))
        searchcount = 0
        for line in amfile:
            if reobject.search(line):
                searchcount+=1
                start1,end1 = re.search(reobject,line).span(1)
                start2,end2 = re.search(reobject,line).span(2)
                line = line[:start1]+weather+line[end1:start2]+tianqi+line[end2:]
                wlist+= line
            else:
                wlist+= line
        if searchcount == 0:
            #无当天上午记录→追加
            pm = ' '.join(
                    (unicode(y),unicode(m),unicode(d),unicode(h),high,low,weather,weather,tianqi,tianqi)
            )
            wlist += pm
        pmfile.write((wlist+u'\r\n'))
    amfile.close()
    pmfile.close()

def transform(weather_1,weather_2 = None):
    #对单个天气情况做出判断，晴天记作1，雨天记作0，阴天记作-2
    def decide(weather):
        if u'雨' in weather or u'雷' in weather or u'冰' in weather or u'雪' in weather:
            out = 0
        elif u'云' in weather or u'阴' in weather or u'霾' in weather:
            out = -2
        elif u'雾' in weather or u'晴' in weather or u'阳' in weather:
            out = 1
        else:
            out = 1
        return out

    #出现雨则算作雨天，晴天和阴天在一起算作阴天，都是阴天的时候才算作阴天
    if weather_2 == None:
        if decide(weather_1)==0:
            weather = u'雨'
        elif decide(weather_1)==1:
            weather = u'晴'
        else:
            weather = u'阴'
    else:
        if decide(weather_1)*decide(weather_2) == 0:
            weather = u'雨'
        elif decide(weather_1)*decide(weather_2) == 4:
         weather = u'阴'
        else:
            weather = u'晴'

    return weather

def output(txt):
    b = re.split(u'转|间歇性|间|，|有时|有',txt)
    b = filter(lambda x:x!='',b)
    if len(b)==1:
        return transform(''.join(b))
    else:
        return reduce(transform,b)

# 网页截图
def webscreen(y,m,d,h):
    url = 'http://www.accuweather.com/zh/cn/rongshan/58633/weather-forecast/58633'
    driver = webdriver.PhantomJS()
    driver.set_page_load_timeout(300)
    driver.set_window_size(1280,800)
    driver.get(url)
    name = ['01' if int(h)<=12 else '02'][0]
    #截取需要的图片保存
    imgelement = driver.find_element_by_id('forecast-feed')
    location = imgelement.location
    size = imgelement.size
    savepath = r'.{}AutoBarometer{}{}{}{}{}.png'.format(os.sep,os.sep,y,m,d,name)
    driver.save_screenshot(savepath)
    im = Image.open(savepath)
    left = location['x']
    top = location['y']-92
    right = left + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left,top,right,bottom))
    im.save(savepath)

if __name__ =='__main__':
    while 1:
        #获取时间
        timelist=time.strftime('%y|%m|%d|%H|%M',time.gmtime(time.time()+28800))
        y,m,d,h,M=[i for i in timelist.split('|')]
        if 1:
            if int(h)==11 or int(h) ==17 or 1:
                webscreen(y,m,d,h)
                query(y,m,d,h)
                print u'{}年{}月{}日{}时获取完成'.format(y,m,d,h).encode('utf-8')
                time.sleep(3000)
            else:
                time.sleep(3000)





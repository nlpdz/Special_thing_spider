# -*- coding: utf-8 -*-
# 爬取网易悦图上的图片  （财经类）
import requests
import re
import json
import os
import time
from bs4 import BeautifulSoup
import pymysql
import pymysql.cursors
from yuntu import YunTu
import jieba


print('连接到mysql服务器...')
db = pymysql.connect("localhost","root","123456","specialthing",charset="utf8")
print('连接上了!')
cursor = db.cursor()
cursor.execute("DROP TABLE IF EXISTS EVENT1")

sql1 = """CREATE TABLE EVENT1(
        id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(100) DEFAULT NULL,
        tag VARCHAR(100) DEFAULT NULL,
        description VARCHAR(500) DEFAULT NULL,
        article VARCHAR(10000) DEFAULT NULL)"""

cursor.execute(sql1)
print('================')

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }
def Search():
    print('请输入事件：')
    searchEvent = input("searchEvent:")

    return searchEvent

def Show(searchEvent):
    data = []
    data2 = ''

    # i为页数，可以设置大一点
    for i in range(1, 10):
        url = 'http://api.search.sina.com.cn/?c=news&t=&q=%s&page=%d&sort=rel&num=10&ie=utf-8&qq-pf-to=pcqq.c2c' % (searchEvent, i)

        r = requests.get(url, headers=headers)
        # print(r.text)
        # 匹配所有的url,'.{3,200}' 为url为长度控制
        temp = re.findall(r'"url":"(http:.{3,200}.shtml)",', r.text, re.S)
        # print(temp)
        # print(len(temp))
        # 去掉url里面的'\',这样request就不会出错。
        for j in temp:
            j = j.replace('\\', '')
            data.append(j)
    print(data)
    print(len(data))

    # 遍历data里面的url,逐个网页获取我们要的内容，并存进数据库。   有些文章的article形式不统一，所以会出现一些空的article
    for url in data:
        r = requests.get(url)
        r.encoding = ('utf-8')
        # 非常致命的一点，如果html代码开头就有注释的话，BeautifulSoup是找不到想要的标签的!!!! 所以破坏掉前面的注释！
        html = r.text.replace('<!---->', '<!--###-->')
        # html = open('1.html', 'r', encoding='utf-8').read().replace('<!---->', '<!-- -->')
        # print(html)
        title = []
        tag = []
        description = []
        article = []

        try:
            soup = BeautifulSoup(html, "html5lib")  # 配置soup  'html5lib'优点：最好的容错性，以浏览器的方式解析文档，生成HTML5格式的文档  缺点：速度慢，不依赖外部扩展

            # title = re.findall(r'<meta property="og:title" content="(.*?)" />', html, re.S)[0]  # 有缺陷，meta是写给浏览器和爬虫看的，没有这个也不会影响内容，所有尽量后body里面的属性
            # keywords = re.findall(r'<meta name="keywords" content="(.*?)" />', html, re.S)[0]
            tag = re.findall(r'<meta name="tags" content="(.*?)" />', html, re.S)[0]  # 但是非title属性一般都会在mata里面有，方便浏览器检索。
            description = re.findall(r'<meta name="description" content="(.*?)" />', html, re.S)[0]
            # article = re.findall(r'<div class="article" id="article"(.*?)</div>', html, re.S)[0]

            # BeautifulSoup去掉特定标签及内容的方法！！！！ 对象为 soup对象
            [s.extract() for s in soup('script')]
            [s.extract() for s in soup('style')]

            # print(soup.find_all("div", class_='article'))

            title = soup.find_all(class_='main-title')[0]  # 寻找 'main-title'类的内容
            title = re.sub(r'<[^>]*>', "", str(title)) # 去标签！
            article = soup.find_all("div", class_='article')[0]
            article = re.sub(r'<[^>]*>', "", str(article))   # 去掉所有的html标签！！  剩下的基本上都是文本内容。
            data2 += article  # 字符串拼接，后面传给 wordcloud
        except:
            pass
        # article = re.sub(r'<[^>]*>', "", str(article))

        # 存入数据库，由于id设置为主键自增，所以这里不需要写id的值  原始数据！！！
        sql = "INSERT INTO EVENT1(title, tag, description, article) VALUES('%s', '%s', '%s', '%s')" % (title, tag, description, article)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            pass

    a = []
    print(data2)   # 分词前
    words = list(jieba.cut(data2))  # 分词后
    for word in words:
        if len(word) > 1:
            a.append(word)
    txt = r' '.join(a)
    print(txt)
    YunTu.wordcloudplot(txt)

def main():
    t = 0
    searchEvent = Search()
    while t <= 60:

        Show(searchEvent)
        time.sleep(15)
        t += 10

if __name__ == '__main__':
    main()
















































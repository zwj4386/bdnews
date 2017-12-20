#!/usr/bin/python
# -*- coding:utf-8 -*-
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from bdnews.items import BdnewsItem
import pymysql
import os
import datetime
import sys
from urllib import unquote
import urlparse
from urllib import quote
reload(sys)
sys.setdefaultencoding('utf-8')

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
'''
1.将title从数据库中取   !  转码  格式 .decode('string_escape')
2.url放到网页进行搜索
3.爬搜索结果   选中新闻标题selenium 涉及分页request
'''
class BaiDuNews(Spider):

    name = 'bdnews2'
    allowed_domains=['news.baidu.com']
    start_urls=[
        'http://news.baidu.com',
    ]
    conn = pymysql.connect(host='ip', user='zwj', passwd='123456', db='test', charset='utf8',
                           port=3306)
    cursor = conn.cursor()

    def getdata(self, response):
        try:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"
            headers = {'User-Agent': user_agent}
            hx = Selector(response)
            item = BdnewsItem()
            #拿到数据库
            cursor=self.cursor
            conn=self.conn
            #获取div 一页20条数据
            div=hx.xpath('//div[contains(@class,"result title")]')
            #遍历数据 进行查重存储
            for i in range(0,len(div)):
            # 获取元素
                micro=div[i]
                # 获取url
                t_url = micro.xpath("./h3[@class='c-title']/a/@href").extract()
                url=''.join(t_url)
                #url查重
                sql_select = "select URL from TOP_SEARCHRESULT where URL='"+url+"'"
                cursor.execute(sql_select)
                rs = cursor.fetchall()

                if len(rs)==0:
                    item['url'] = url
                else:
                    continue

                #获取title
                t_title=micro.xpath('./h3[@class="c-title"]/a')
                tm_title=t_title.xpath("string(.)").extract()
                title = ''.join(tm_title)
                item['title']=title


                #获取site
                t_site=micro.xpath("./div[@class='c-title-author']")
                tm_site=t_site.xpath("string(.)").extract()
                site=''.join(tm_site)
                item['site']=site

                #查看是否有相同话题的更多新闻
                more_site=t_site.xpath('./a[@class="c-more_link"]/@href').extract()
                if len(more_site)!=0:
                    murl=''.join(more_site)
                    xtlink='http://news.baidu.com'+murl
                    item['xtlink']=xtlink
                else:
                    item['xtlink']=""

                #获取cjmc
                if response.url.find('intitle')<>-1:
                    urlp = urlparse.urlparse(unquote(response.url)).query.split('&')
                    str = urlp[0].split('=')[1]
                    kw=str[str.find('intitle')+9:str.find(')+cont')]
                    cjmc = '百度新闻搜索_%s' % (kw)
                elif response.url.find('word=title')<>-1:
                    urlp = urlparse.urlparse(unquote(response.url)).query.split('&')
                    str = urlp[0].split('=')[1]
                    kw = str[str.find('title:(')+6:str.find(')+cont')].strip('(')
                    cjmc = '百度新闻搜索_%s' % (kw)
                else:
                    urlp = urlparse.urlparse(unquote(response.url)).query.split('&')
                    kw = urlp[0].split('=')[1]
                    cjmc='百度新闻搜索_%s'%(kw)
                item['cjmc']=cjmc

                yield item


            # 获取下一页//a/following-sibling::*[1]获取当前strong标签的所有a标签
            flag=response.xpath('//p[@id="page"]/strong/following-sibling::*')
            #如果strong标签页的下一子节点有href标签
            if flag<>None:
                #获取下一页a标签的href属性值
                Url = flag.xpath('./@href').extract()
                for i in range(1,len(Url)):
                    nextUrl = 'http://news.baidu.com' + ''.join(Url[i])
                    yield Request(nextUrl, headers=headers, callback=self.getdata)

            #只搜索最近5天的xtlink  不对 只搜索出来一个就request出去死循环
            #sql="select XTLINK from TOP_SEARCHRESULT where XTLINK is not null and XTLINK<>'' and datediff(now(),CREATEDATE)<5"
            #cursor.execute(sql)
            #url_list=cursor.fetchall()
            #for more_url in url_list:
            #    url=''.join(more_url)
            #    yield Request(url, headers=headers, callback=self.getdata)
        except BaseException, e:
            print e

	
    def parse(self,response):
        try:
            ##########################提取关键词#############################
            cursor=self.cursor
            sql = "select TITLE from TOP_YQSJ where SFSS='Y'"
            cursor.execute(sql)
            rs = cursor.fetchall()
            user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"
            headers={'User-Agent':user_agent}
            if rs == None:
                pass
            else:
                # rs打印出列表
                for bs in rs:
                # 测试打印关键词 string_escape
                    kw = str(bs[0]).decode('utf-8')
                    #######多线程
                    url='http://news.baidu.com/ns?word=%s&tn=newstitle&from=news&cl=2&rn=20&ct=0&qq-pf-to=pcqq.c2c'%kw
                    #print url
                    yield Request(url, headers=headers, callback=self.getdata)
        except BaseException,e:
            print e






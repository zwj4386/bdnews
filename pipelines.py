# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import json

#保证可以向oracle数据库中更新中文
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class BdnewsPipeline(object):
    def process_item(self, item, spider):
        #连接数据库
        conn=pymysql.connect(host='192.168.3.232',user='zwj',passwd='123456',db='caiji',charset='utf8',port=3306)
        cursor=conn.cursor()

        #在数据库中添加数据，违反唯一性约束则不插入
        sql_insert="insert into TOP_SEARCHRESULT(TITLE,SITE,CJMC,URL,XTLINK)" \
                   "values('%s','%s','%s','%s','%s')" % (item['title'],item['site'],item['cjmc'],item['url'],item['xtlink'])
        print(sql_insert)
        cursor.execute(sql_insert)
        conn.commit()

        #断开数据库的链接
        cursor.close()
        conn.close()
        return item

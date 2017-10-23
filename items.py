# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BdnewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title=scrapy.Field()
    site=scrapy.Field()
    cjmc=scrapy.Field()
    url=scrapy.Field()
    cjsj=scrapy.Field()
    xtlink=scrapy.Field()
    #进库时间触发器实现
    pass

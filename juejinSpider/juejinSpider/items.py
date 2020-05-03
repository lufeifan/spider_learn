# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JuejinspiderItem(scrapy.Item):
    # define the fields for your item here like:
    categoryid = scrapy.Field()
    categoryname = scrapy.Field()
    order = scrapy.Field()
    tagsid = scrapy.Field()
    tagname = scrapy.Field()
    title = scrapy.Field()
    originalUrl =scrapy.Field()
    readcount =scrapy.Field()
    pagesdetail = scrapy.Field()
    pass

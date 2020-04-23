# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JuejinspiderItem(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    tagsid = scrapy.Field()
    order = scrapy.Field()
    data = scrapy.Field()
    title = scrapy.Field()
    pass

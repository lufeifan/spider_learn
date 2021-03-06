# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    introduction = scrapy.Field()
    # section_list = scrapy.Field()
    view_count = scrapy.Field()
    # 主题id
    pageid = scrapy.Field()
    question_title = scrapy.Field()
    question_id = scrapy.Field()
    content = scrapy.Field()

    pass

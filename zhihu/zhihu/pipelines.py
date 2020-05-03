# -*- coding: utf-8 -*-
import pymongo,re

class ZhihuPipeline(object):

    def __init__(self):

        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = self.myclient["spider"]
        self.mycol = self.mydb["zhihu_4_29"]

    def process_item(self, item, spider):

        mylist = [
            {"title":item['title'],
             "introduction": item['introduction'],
             "view_count": item['view_count'],
             "pageid":item['pageid'],
             "question_title": item['question_title'],
             "question_id": item['question_id'],
             "content":item['content'],
             },
        ]

        self.mycol.insert_many(mylist)

        return item

# -*- coding: utf-8 -*-
# import json,pymysql
import pymysql
import pymongo
class JuejinspiderPipeline(object):
    def __init__(self):

        self.conn = pymysql.connect(host='127.0.0.1',port=3307, user='root',passwd='root', db='scrapy')  # 连接数据库

        # self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        # self.mydb = self.myclient["runoobdb"]
        # self.mycol = self.mydb["juejin"]

    def process_item(self, item, spider):

        self.conn.query(
            "insert juejin(title,category,abab,cvcv2)"
            "values('{}','{}','{}','{}')".format(
                item['title'],item['category'],item['data'],item['order']
            )
        )
        self.conn.commit()  # 执行添加

        # mylist = [
        #     {"title":item['title'], "category": item['category'], "tagsid": item['tagsid'], "order": item['order'],"data":item['data']},
        # ]

        # self.mycol.insert_many(mylist)

        return item

    def close_spider(self, spider):
        self.conn.close()  # 关闭连接
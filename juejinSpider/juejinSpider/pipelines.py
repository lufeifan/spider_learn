# -*- coding: utf-8 -*-
# import json,pymysql
import pymysql
import pymongo,re
from w3lib.html import remove_tags

class JuejinspiderPipeline(object):
    def __init__(self):

        # self.conn = pymysql.connect(host='127.0.0.1',port=3307, user='root',passwd='root', db='scrapy')  # 连接数据库

        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = self.myclient["spider"]
        self.mycol = self.mydb["juejin"]

    def process_item(self, item, spider):
        # 去除html 标签
        content = remove_tags(item['pagesdetail'])
        content = re.sub(r'[\t\r\n\s]',' ', content)
        # print(content)

        # self.conn.query(
        #     "insert juejin(title,category,abab,cvcv2)"
        #     "values('{}','{}','{}','{}')".format(
        #         item['title'],item['category'],item['data'],item['order']
        #     )
        # )
        # self.conn.commit()  # 执行添加

        mylist = [
            {"categoryid":item['categoryid'],
             "categoryname": item['categoryname'],
             "order": item['order'],
             "tagsid":item['tagsid'],
             "tagname": item['tagname'],
             "title": item['title'],
             "originalUrl":item['originalUrl'],
             "readcount": item['readcount'],
             "pagesdetail": content
             },
        ]

        self.mycol.insert_many(mylist)

        return item

    def close_spider(self, spider):
        pass
        # self.conn.close()  # 关闭连接
# -*- coding: utf-8 -*-
import scrapy,re,json
from copy import deepcopy
from ..items import JuejinspiderItem
from scrapy_redis.spiders import RedisSpider

class JuejinSpider(RedisSpider):
# class JuejinSpider(scrapy.Spider):
    name = 'juejin'
    redis_key = 'myspider:start_urls'
    # start_urls = ['http://juejin.im/']
    headers={
            'X-Agent': 'Juejin/Web',
            'Content-Type': 'application/json'
        }

    three = ['POPULAR','NEWEST','THREE_DAYS_HOTTEST']

    def parse(self, response):
        # 获取大的分类的 category 
        namelist = response.xpath('//*[@id="juejin"]/div[2]/main/nav/ul/li')
        for i in namelist[1:]:
            # 获取div标签
            category =i.xpath('./div').get()
            # 大的分类名
            categoryname = i.xpath('./div/a/text()').get()
            # 使用正则提起div 标签中的 st:state
            mat=re.compile(r'st:state="(.*)" class')
            categoryid= mat.findall(category)[0]
            item = JuejinspiderItem()
            item['categoryid'] = categoryid
            item['categoryname'] = categoryname

            # 获取每一个分类下的全部文章数据， 热门，最新，热榜
            for order in self.three:
                item['order'] = order
                item['tagname'] = categoryname
                # 因为要保存标签名，此处自己定义NAN数据
                item['tagsid'] = 'NAN'
                
                allbody = {"variables":{"tags":[],"category":f'{categoryid}',"first":40,"after":"","order":f'{order}'},"extensions":{"query":{"id":"653b587c5c7c8a00ddf67fc66f989d42"}}}
                yield scrapy.Request(
                    'https://web-api.juejin.im/query',
                    method='POST',
                    headers=self.headers,
                    body=json.dumps(allbody),
                    callback=self.getnameslist,
                    meta={'item':deepcopy(item)}
                )
           
            tagsbody = {"variables":{"category":f'{categoryid}',"limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828ba6b71a9fd9"}}}
            # 获取category中的 tagId
            yield scrapy.Request(
                'https://web-api.juejin.im/query',
                method='POST',
                headers=self.headers,
                body=json.dumps(tagsbody),
                callback=self.gettagslist,
                # 传入 category
                meta={'item':deepcopy(item)}
            )
            
    
    # 获取tags的数据
    def gettagslist(self,response):
        item = response.meta['item']
        categoryid = item['categoryid']
        data = json.loads(response.text)
       
        for order in self.three:
            for i in data['data']['tagNav']['items']:

                item['tagsid'] = i['tagId']
                item['order'] = order
                item['tagname'] = i['title']

                tag_hot_body = {"variables":{"tags":[f'{item["tagsid"]}'],"category":f'{categoryid}',"first":20,"after":"","order":f'{item["order"]}'},"extensions":{"query":{"id":"653b587c5c7c8a00ddf67fc66f989d42"}}}
                # 获取每个标签里的热门数据
                yield scrapy.Request(
                    'https://web-api.juejin.im/query',
                    method='POST',
                    headers=self.headers,
                    body=json.dumps(tag_hot_body),
                    callback=self.getnameslist,
                    meta={"item":deepcopy(item)}
                )
    
    def getnameslist(self,response):
        item = response.meta['item']
        # 提取数据
        datas = json.loads(response.text)
        datalist = datas['data']['articleFeed']['items']['edges']
        for data in datalist:
            # 页面详情链接
            item['originalUrl'] = data['node']['originalUrl']
            # 文章标题
            item['title'] = data['node']['title']
            # print(item['originalUrl'])
            yield scrapy.Request(
                item['originalUrl'],
                callback=self.getdetail,
                meta={"item":deepcopy(item)}
            )
    
    def getdetail(self,response):
        item = response.meta['item']
        try:
            item['pagesdetail'] = response.xpath('//*[@id="juejin"]/div[2]/main/div/div[1]/article').get()
            item['readcount'] = response.xpath('//*[@id="juejin"]/div[2]/main/div/div[1]/article/div[3]/div/div/span/text()').get().split(" ")[1]
        except :
            item['readcount'] = 'NAN'
        
        yield item
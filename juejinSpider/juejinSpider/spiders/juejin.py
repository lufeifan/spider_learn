# -*- coding: utf-8 -*-
import scrapy,re,json
from copy import deepcopy
from ..items import JuejinspiderItem


class JuejinSpider(scrapy.Spider):
    name = 'juejin'
    # allowed_domains = ['juejin.im']
    start_urls = ['http://juejin.im/']
    headers={
            'X-Agent': 'Juejin/Web',
            'Content-Type': 'application/json'
        }

    three = ['POPULAR','NEWEST','THREE_DAYS_HOTTEST']

    def parse(self, response):
        # 获取大的分类的category
        namelist = response.xpath('//*[@id="juejin"]/div[2]/main/nav/ul/li')
        for name in namelist[1:]:
            names =name.xpath('./div').get()
            # 使用正则提起div 标签中的 st:state
            mat=re.compile(r'st:state="(.*)" class')
            category= mat.findall(names)[0]
            # print(category)
            item = JuejinspiderItem()
            item['category'] = category

            # 获取每一个分类下的全部数据
            for order in self.three:
                item['order'] = order
                item['tagsid'] = 'nan'
                item['title'] = '全部'
                allbody = {"operationName":"","query":"","variables":{"tags":[],"category":f'{category}',"first":20,"after":"","order":f'{order}'},"extensions":{"query":{"id":"653b587c5c7c8a00ddf67fc66f989d42"}}}
                yield scrapy.Request(
                    'https://web-api.juejin.im/query',
                    method='POST',
                    headers=self.headers,
                    body=json.dumps(allbody),
                    callback=self.getnameslist,
                    meta={'item':deepcopy(item)}
                )
           
            tagsbody = {"operationName":"","query":"","variables":{"category":f'{category}',"limit":15},"extensions":{"query":{"id":"801e22bdc908798e1c828ba6b71a9fd9"}}}
            # 获取category中的tags
            yield scrapy.Request(
                'https://web-api.juejin.im/query',
                method='POST',
                headers=self.headers,
                body=json.dumps(tagsbody),
                callback=self.gettagslist,
                # 传入 category
                meta={'category':category,'item':deepcopy(item)}
            )
            
    
    # 获取tags的数据
    def gettagslist(self,response):
        # 接收 meta
        category = response.meta['category']
        item = response.meta['item']
        data = json.loads(response.text)
       
        for order in self.three:
            for tagIds in data['data']['tagNav']['items']:
                # 获取tagId
                tagId = tagIds['tagId']
                # 获取标签名字
                title = tagIds['title']
                item['tagsid'] = tagId
                item['order'] = order
                item['title'] = title
                tag_hot_body = {"operationName":"","query":"","variables":{"tags":[f'{tagId}'],"category":f'{category}',"first":20,"after":"","order":f'{order}'},"extensions":{"query":{"id":"653b587c5c7c8a00ddf67fc66f989d42"}}}
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
        data = json.loads(response.text)
        # with open('test.json','a',encoding='utf-8') as f:
        #     f.write(json.dumps(data['data']['articleFeed']['items']['edges']))
        item['data'] = data['data']['articleFeed']['items']['edges']
        yield item
        # print(data['data']['articleFeed']['items']['edges'])
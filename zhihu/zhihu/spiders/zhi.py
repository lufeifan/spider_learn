# -*- coding: utf-8 -*-
import scrapy,json,re,pymongo
from zhihu.items import ZhihuItem
from copy import deepcopy
from lxml import etree
from w3lib.html import remove_tags
from scrapy_redis.spiders import RedisSpider

class JuejinSpider(RedisSpider):
# class ZhiSpider(scrapy.Spider):
    redis_key = 'myspider:start_urls'
    name = 'zhi_test'

    # start_urls = ['https://www.zhihu.com/api/v4/news_specials/list?limit=10&offset=0']

    def parse(self, response):
        # 数据
        for data in json.loads(response.text)['data']:
            item = ZhihuItem()
            # 标题
            item['title'] = data['title']
            # 介绍
            item['introduction'] = data['introduction']
            # 内容列表
            # item['section_list'] = data['section_list']
            # 观看人数
            item['view_count'] = data['view_count']
            # 主题id
            item['pageid'] = data['id']

            yield scrapy.Request(
                'https://www.zhihu.com/special/'+item['pageid'],
                # 'https://www.zhihu.com/special/19560080',
                # 'https://www.zhihu.com/special/21285709',
                callback=self.page,
                meta={'item':deepcopy(item)}
            )

        # 下一条请求
        # print(json.loads(response.text)['paging']['next'])
        if not json.loads(response.text)['paging']['is_end']:
            print(json.loads(response.text)['paging']['next'])
            yield scrapy.Request(
                json.loads(response.text)['paging']['next'],
                callback=self.parse
            )
    
    def page(self,response):
        item = response.meta['item']
        question_id_list = []
        q_id = []
        # 获取每个问题的 url
        # with open('test.html','w',encoding="utf-8") as f:
        #     f.write(response.text)
        # //*[@id="root"]/div[3]/div[3]/section[1]/div/div[2]/div[1]/a[1]
        # print(response.xpath('').get())
        # mat = re.compile(r'(question)')
        # 匹配有 a 链接的
        mat=re.compile(r'(https://www.zhihu.com/question/[\d]+|https://zhuanlan.zhihu.com/[a-z]*/[\d]+)')
        question_id= mat.findall(response.text)
        # 如果没有 a 链接
        if len(question_id) == 0:
            # "id":"39995431"}
            # 去除换行
            res = re.sub(r'[\t\r\n\s]','', response.text)
            mat=re.compile(r'("id":"(?:[\d]{6,12})"})')
            # 提取出 "id":"39995431"}
            query_id= mat.findall(res)
            # 提取需要的正确数据
            for i in query_id:
                 q_id.append(i.split('"')[-2])
        else:
            for i in question_id:
                # 提取需要的正确数据
                # print(i)
                q_id.append(i.split('/')[-1])
        # 将未匹配的页面记录
        if question_id == 0:
            myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            mydb = myclient["spider"]
            mycol = mydb["erro"]
            mycol.insert_one({'erro':response.url}) 

        # 每个问题的id ，唯一标识
        for i in q_id:
            # 去除重复
            if i not in question_id_list:
                question_id_list.append(i)
        # print(question_id_list)
        # 每个主题下个个问题详情页面
        for ques_id in question_id_list:

            # print(ques_id)
            item['question_id'] = ques_id
            # url = 'https://www.zhihu.com/api/v4/questions/'
            url = 'https://www.zhihu.com/api/v4/questions/'+ques_id+'/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default'
            # print(url)
            
            yield scrapy.Request(
                url,
                meta={'item':deepcopy(item)},
                callback=self.question_detail,
            )
    
    def question_detail(self,response):

        # 第一个回答
        item = response.meta['item']
        copy_item = deepcopy(item)
        data = json.loads(response.text)
        try:
            
            for con in data['data']:
                content = remove_tags(con['content'])
                item['content'] = re.sub(r'[\t\r\n\s]',' ', content)
                item['question_title'] = con['question']['title']
                # print(item['question_title'])
                yield item

            # 判断是否是最后一条
            if not data['paging']['is_end']:
                next_url = data['paging']['next']
                # print(next_url)
                yield scrapy.Request(
                    next_url,
                    callback=self.question_detail,
                    meta={'item':deepcopy(copy_item)},
                )
        except :
            myclient = pymongo.MongoClient("mongodb://localhost:27017/")
            mydb = myclient["spider"]
            mycol = mydb["erro"]
            mycol.insert_one({'erro_question_id':item['question_id']}) 
            yield item
    
    # def other_content(self,response):

    #     item = response.meta['item']
    #     data= json.loads(response.text)['data']
    #     for other_con  in data:
    #         item['question_title'] = other_con['question']['title']
    #         content = remove_tags(other_con['content'])
    #         item['other_content'] = re.sub(r'[\t\r\n\s]',' ', content)
            
    #         yield item
        
        # 原来
        # question_title = response.xpath('//div[@class="RichContent-inner"]').get()

        # content = remove_tags(question_title)
        # # 记录第一个回答
        # item['first_content'] = re.sub(r'[\t\r\n\s]',' ', content)
        # # 其他回答   https://www.zhihu.com/api/v4/questions/371071410/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default  limit=5
        # detail_url ='https://www.zhihu.com/api/v4/questions/'+item['question_id'] +'/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=20&offset=10&platform=desktop&sort_by=default'
        # yield scrapy.Request(
        #     detail_url,
        #     callback=self.other_content,
        #     meta={'item':deepcopy(item)},
        # )
    
    


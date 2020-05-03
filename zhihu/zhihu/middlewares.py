# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import pymongo,json
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

from scrapy.utils.project import get_project_settings
settings = get_project_settings()

# 随机请求头
class UserAgentMiddleware(object):

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(settings['USER_AGENT_LIST'])

# 随机代理
class ProxyMiddleware(object):
    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = self.myclient["proxies"]
        self.mycol = self.mydb["proxy"]
    
    def process_request(self, request, spider):

        # 从数据库选择proxy
        proxy =[i['proxy'] for i in self.mycol.aggregate([ {'$sample': {'size':1}}])]
        request.meta['proxies'] = proxy[0]
        # print(request.meta)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        if response.status == 404:
            print("资源尚未找到 404")
        elif response.status >= 400:
            print("ip可能被封了")
        else:
            print(response.status)
        
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

class ZhihuSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        # print(response.meta)
        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            # print(i)
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        # 爬虫开始运行
        for r in start_requests:
            # print(r)
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ZhihuDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class My_RetryMiddleware(RetryMiddleware):

    def __init__(self, settings):
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
 
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            try:
                print("连接异常, 进行重试... 错误码："+ reason)
                # 将爬取失败的URL存下来，你也可以存到别的存储
                with open(str(spider.name)+"_erro" + ".txt", "a") as f:
                    f.write(response.url + "\n")

            except :
                print('获取失败！')
                spider.logger.error('获取失败！')

            return self._retry(request, reason, spider) or response

        return response
 
    def process_exception(self, request, exception, spider):
    # 出现异常的处理
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            with open(str(spider.name)+"_erro" + ".txt", "a") as f:
                f.write(str(request) + "\n")
            return None

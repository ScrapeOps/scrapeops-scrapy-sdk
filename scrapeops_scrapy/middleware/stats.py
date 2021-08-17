from scrapy.utils.python import global_object_name

from scrapeops_scrapy.signals.response_signal import scrapeops_response_recieved
from scrapeops_scrapy.signals.exception import scrapeops_exception_recieved


class ScrapeOpsStats:

    def __init__(self):
        pass

    def process_response(self, request, response, spider):
        spider.crawler.signals.send_catch_log(
            signal=scrapeops_response_recieved, 
            request=request, 
            response=response, 
            spider=spider)
        return response

    def process_exception(self, request, exception, spider):
        ex_class = global_object_name(exception.__class__)
        spider.crawler.signals.send_catch_log(
            signal=scrapeops_exception_recieved, 
            request=request, 
            spider=spider,
            exception_class=ex_class)
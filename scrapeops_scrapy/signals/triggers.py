from scrapeops_scrapy.signals.scrapeops_signals import scrapeops_response_rejected, scrapeops_item_rejected

class ScrapeOpsTrigger(object):

    def __init__(self):
        pass
    
    @staticmethod
    def reject_response(crawler=None, response=None, reason=None):   
        crawler.signals.send_catch_log(signal=scrapeops_response_rejected, 
                spider=crawler.spider, 
                response=response,
                reason=reason,
                )

    @staticmethod
    def reject_item(crawler=None, response=None, item=None, reason=None):   
        crawler.signals.send_catch_log(signal=scrapeops_item_rejected, 
                spider=crawler.spider, 
                response=response,
                item=item,
                reason=reason,
                )
    

    
 



   


    







         
    

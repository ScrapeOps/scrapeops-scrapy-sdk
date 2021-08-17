## scrapy
from scrapy.utils.request import request_httprepr
from scrapy.utils.response import response_httprepr


## scrapeops
from scrapeops_scrapy.stats.model import OverallStatsModel, PeriodicStatsModel ## weird, need to fix --> probably due to the init
from scrapeops_scrapy.utils.utils import current_time
from scrapeops_scrapy.processors.exceptions import ExceptionProcessor

import copy


class StatsCore(OverallStatsModel, PeriodicStatsModel):
    """
        Where the core ScrapeOps Functionality Goes
    """

    def __init__(self):
        OverallStatsModel.__init__(self)
        PeriodicStatsModel.__init__(self)
        
    def display_stats(self):
        self.display_periodic_stats()
        self.display_overall_stats()

    def check_periodic_stats(self):
        if self._periodic_stats == {}:
            self.set_value(self._periodic_stats, 'job_id', self.job_id)

    def spider_open_stats(self):
        self.set_value(self._overall_stats, 'job_id', self.job_id)
        self.set_value(self._overall_stats, 'job_start_time', self.start_time)
        self.set_value(self._overall_stats, 'job_finish_time', 0)
        self.set_value(self._overall_stats, 'job_run_time', 0)
        self.set_value(self._overall_stats, 'status', 'Live')


    def spider_close_stats(self, reason=None, crawler=None):
        finish_time = current_time()
        self.aggregate_stats(crawler) 
        self.set_value(self._overall_stats, 'job_finish_time', finish_time)
        self.set_value(self._overall_stats, 'job_run_time', finish_time - self.start_time)
        self.set_value(self._overall_stats, 'status', 'Finished')
        self.set_value(self._overall_stats, 'reason', reason)
        self.set_value(self._overall_stats, 'period_frequency', self.period_frequency)
        


    def generate_request_stats(self, request=None, proxy=None, domain=None):
        proxy_name = proxy.get('proxy_name', 'no_proxy')
        proxy_setup = proxy.get('proxy_setup', 'none')
        domain_name = domain.get('domain_name', 'no_domain')
        page_type = domain.get('page_type', 'none')
        reqlen = len(request_httprepr(request))
        
        ## periodic stats
        self.check_periodic_stats()
        self.inc_value(self._periodic_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|count')
        self.inc_value(self._periodic_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|bytes', count=reqlen)

        ## overall stats
        self.inc_value(self._overall_stats, f'requests|{request.method}|count')
        self.inc_value(self._overall_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|count')
        self.inc_value(self._overall_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|bytes', count=reqlen)



    def generate_response_stats(self, request=None, response=None, proxy=None, domain=None):
        proxy_name = proxy.get('proxy_name', 'no_proxy')
        proxy_setup = proxy.get('proxy_setup', 'none')
        domain_name = domain.get('domain_name', 'no_domain')
        page_type = domain.get('page_type', 'none')
        reslen = len(response_httprepr(response))
        total_latency = request.meta.get('_total_latency', 0) + request.meta['download_latency']

        # ## periodic stats
        # self.check_periodic_stats()
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|count')
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|bytes', count=reslen)
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|retries', count=request.meta.get('retry_times', 0))
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|total_latency', count=total_latency)
        # self.min_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|min_latency', total_latency)
        # self.max_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|max_latency', total_latency)

        # ## overall stats
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|count')
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|bytes', count=reslen)
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|retries', count=request.meta.get('retry_times', 0))
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|total_latency', count=total_latency)
        # self.min_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|min_latency', total_latency)
        # self.max_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|max_latency', total_latency)


        ## overall stats
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|count')
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|bytes', count=reslen)
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|retries', count=request.meta.get('retry_times', 0))
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|total_latency', count=total_latency)
        self.min_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|min_latency', total_latency)
        self.max_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|max_latency', total_latency)


        ## periodic stats
        self.check_periodic_stats()
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|count')
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|bytes', count=reslen)
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|retries', count=request.meta.get('retry_times', 0))
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|total_latency', count=total_latency)
        self.min_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|min_latency', total_latency)
        self.max_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|max_latency', total_latency)

        


    def generate_item_stats(self, signal=None, response=None, domain=None, proxy=None):
        request = response.request
        domain_name = domain.get('domain_name', 'no_domain')
        proxy_name = proxy.get('proxy_name', 'no_proxy')
        self.check_periodic_stats()

        if signal == 'item_scraped':
            self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|items')
            self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|items')
        
        elif signal == 'item_dropped':
            self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|items_dropped')
            self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|items_dropped')
        
        elif signal == 'item_error':
            self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|item_errors')
            self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{response.status}|item_errors')
    
    def generate_exception_stats(self, request=None, proxy=None, domain=None, exception_class=None):
        domain_name = domain.get('domain_name', 'no_domain')
        page_type = domain.get('page_type', 'none')
        proxy_name = proxy.get('proxy_name', 'no_proxy')
        proxy_setup = proxy.get('proxy_setup', 'none')
        exception_type = ExceptionProcessor.normalise_exception(exception_class)

        self.check_periodic_stats()
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{exception_type}|count')
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{exception_type}|count')

        #self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{domain_name}|{exception_type}|count')


    

    
    def aggregate_stats(self, crawler):
        self.avg_latency()
        self.log_levels(crawler)

    def avg_latency(self):
        for stat_type in [self._periodic_stats, self._overall_stats]:
            stats_copy = copy.deepcopy(stat_type)
            for key, value in stats_copy.items():
                if 'responses' in key and 'total_latency' in key:
                    count_key = key.replace('total_latency', 'count')
                    avg_latency = value / stats_copy.get(count_key)
                    self.set_value(stat_type, key.replace('total_latency', 'avg_latency'), avg_latency)

    def log_levels(self, crawler):
        scrapy_stats = crawler.stats.get_stats()
        for log_level in ['WARNING', 'ERROR', 'CRITICAL']:
            log_key = 'log_count/' + log_level
            log_value = scrapy_stats.get(log_key, 0)
            previous_value = self._overall_stats.get(log_key, 0)
            self.set_value(self._periodic_stats, log_key, log_value - previous_value)
            self.set_value(self._overall_stats, log_key, log_value)

            

    
                


    








    
        



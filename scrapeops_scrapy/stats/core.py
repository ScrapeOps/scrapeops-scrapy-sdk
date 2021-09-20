## scrapy
from scrapy.utils.request import request_httprepr
from scrapy.utils.response import response_httprepr

## scrapeops
from scrapeops_scrapy.stats.model import OverallStatsModel, PeriodicStatsModel 
from scrapeops_scrapy.utils import utils
from scrapeops_scrapy.normalizer.exceptions import ExceptionNormalizer

import copy


class StatsCore(OverallStatsModel, PeriodicStatsModel):

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
        self.set_value(self._overall_stats, 'job_name', self.job_group_name)
        self.set_value(self._overall_stats, 'job_start_time', self.start_time)
        self.set_value(self._overall_stats, 'job_finish_time', 0)
        self.set_value(self._overall_stats, 'job_run_time', 0)
        self.set_value(self._overall_stats, 'status', 'Live')


    def spider_close_stats(self, reason=None, crawler=None):
        finish_time = utils.current_time()
        self.aggregate_stats(crawler) 
        self.set_value(self._overall_stats, 'job_finish_time', finish_time)
        self.set_value(self._overall_stats, 'job_run_time', finish_time - self.start_time)
        self.set_value(self._overall_stats, 'status', 'Finished')
        self.set_value(self._overall_stats, 'reason', reason)
        self.set_value(self._overall_stats, 'period_frequency', self._period_frequency)
        

    def generate_request_stats(self, request_response_object, request=None):
        proxy_name = request_response_object.get_proxy_name()
        proxy_setup = request_response_object.get_proxy_setup()
        domain_name = request_response_object.get_domain()
        page_type = request_response_object.get_page_type()
        custom_tag = request_response_object.get_custom_tag()
        reqlen = len(request_httprepr(request))
        
        ## periodic stats
        self.check_periodic_stats()
        self.inc_value(self._periodic_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{custom_tag}|count')
        self.inc_value(self._periodic_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{custom_tag}|bytes', count=reqlen)

        ## overall stats
        self.inc_value(self._overall_stats, f'requests|{request.method}|count')
        self.inc_value(self._overall_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{custom_tag}|count')
        self.inc_value(self._overall_stats, f'requests|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{custom_tag}|bytes', count=reqlen)


    def generate_response_stats(self, request_response_object, request=None, response=None):
        proxy_name = request_response_object.get_proxy_name()
        proxy_setup = request_response_object.get_proxy_setup()
        domain_name = request_response_object.get_domain()
        page_type = request_response_object.get_page_type()
        validation = request_response_object.get_validation_test()
        geo = request_response_object.get_geo()
        custom_tag = request_response_object.get_custom_tag()
        custom_signal = 'none'
        reslen = len(response_httprepr(response))
        total_latency = request.meta.get('_total_latency', 0) + request.meta['download_latency']

        ## periodic stats
        self.check_periodic_stats()
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|count')
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|bytes', count=reslen)
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|retries', count=request.meta.get('retry_times', 0))
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|total_latency', count=total_latency)
        self.min_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|min_latency', total_latency)
        self.max_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|max_latency', total_latency)

        ## overall stats
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|count')
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|bytes', count=reslen)
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|retries', count=request.meta.get('retry_times', 0))
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|total_latency', count=total_latency)
        self.min_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|min_latency', total_latency)
        self.max_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|max_latency', total_latency)


        # ## periodic stats
        # self.check_periodic_stats()
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|count')
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|bytes', count=reslen)
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|retries', count=request.meta.get('retry_times', 0))
        # self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|total_latency', count=total_latency)
        # self.min_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|min_latency', total_latency)
        # self.max_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|max_latency', total_latency)

        # ## overall stats
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|count')
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|bytes', count=reslen)
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|retries', count=request.meta.get('retry_times', 0))
        # self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|total_latency', count=total_latency)
        # self.min_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|min_latency', total_latency)
        # self.max_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|max_latency', total_latency)


        
        ## captcha[1]_cloudflare_geo
        #self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|count')
        
    def generate_item_stats(self, request_response_object, signal=None, response=None, domain=None, proxy=None):
        request = response.request
        proxy_name = request_response_object.get_proxy_name()
        proxy_setup = request_response_object.get_proxy_setup()
        domain_name = request_response_object.get_domain()
        page_type = request_response_object.get_page_type()
        validation = request_response_object.get_validation_test()
        geo = request_response_object.get_geo()
        custom_tag = request_response_object.get_custom_tag()
        custom_signal = 'none'
        self.check_periodic_stats()

        if signal == 'item_scraped':
            self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|items')
            self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|items')
        
        elif signal == 'item_dropped':
            self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|items_dropped')
            self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|items_dropped')
        
        elif signal == 'item_error':
            self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|item_errors')
            self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|{validation}|{geo}|{custom_tag}|{custom_signal}|item_errors')

        
        # if signal == 'item_scraped':
        #     self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|items')
        #     self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|items')
        
        # elif signal == 'item_dropped':
        #     self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|items_dropped')
        #     self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|items_dropped')
        
        # elif signal == 'item_error':
        #     self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|item_errors')
        #     self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{response.status}|item_errors')
    

    def generate_exception_stats(self, request_response_object, request=None, exception_class=None):
        proxy_name = request_response_object.get_proxy_name()
        proxy_setup = request_response_object.get_proxy_setup()
        domain_name = request_response_object.get_domain()
        page_type = request_response_object.get_page_type()
        validation = request_response_object.get_validation_test()
        geo = request_response_object.get_geo()
        custom_tag = request_response_object.get_custom_tag()
        custom_signal = 'none'
        exception_type = ExceptionNormalizer.normalise_exception(exception_class)

        self.check_periodic_stats()
        self.inc_value(self._periodic_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{exception_type}|{validation}|{geo}|{custom_tag}|{custom_signal}|count')
        self.inc_value(self._overall_stats, f'responses|{request.method}|{proxy_name}|{proxy_setup}|{domain_name}|{page_type}|{exception_type}|{validation}|{geo}|{custom_tag}|{custom_signal}|count')

    
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

            

    
                


    








    
        



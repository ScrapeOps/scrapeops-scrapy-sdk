
from twisted.internet import task

from scrapeops_scrapy.exceptions import ScrapeOpsMissingAPIKey
from scrapeops_scrapy.utils.utils import current_time
from scrapeops_scrapy.controller.core import SDKCore
from scrapeops_scrapy.stats.core import StatsCore


class ScrapeopsCore(SDKCore, StatsCore):
    """
        Where the core ScrapeOps Functionality Goes
    """

    def __init__(self):
        SDKCore.__init__(self)
        StatsCore.__init__(self)
        
        
    def start_job(self, spider=None, crawler=None):
        self.start_time = self.period_start_time = current_time()
        self.get_spider_details(spider, crawler=crawler)
        self.get_scrapeops_settings(crawler=crawler)
        if self.check_api_key_present():
            self.start_sdk(spider=spider, crawler=crawler)
            self.spider_open_stats()
            self.start_periodic_monitor()
        else:
            self.deactivate_sdk(reason='no_api_key')
            raise ScrapeOpsMissingAPIKey()
            
    def start_periodic_monitor(self):
        if self.sdk_enabled():
            self.loop = task.LoopingCall(self.periodic_monitor)
            self.periodic_loop = self.loop.start(1, now=False) # Start looping every 1 second (1.0).

    def get_periodic_frequency(self):
        self.period_count = 0
        runtime = self.get_runtime()
        if len(self.period_freq_list) == 0:
            self.period_count = int(runtime//self.period_frequency)
            return self.period_frequency
        
        for index, row in enumerate(self.period_freq_list):
            if runtime > int(row.get('total_time')):
                if index == 0:
                    period_time = row.get('total_time') 
                else:
                    period_time = row.get('total_time') - self.period_freq_list[index - 1].get('total_time') 
                self.period_count += int(period_time/row.get('periodic_frequency'))
            if runtime <= int(row.get('total_time')):
                self.period_frequency = row.get('periodic_frequency')
                if index == 0:
                    diff = runtime
                else:
                    diff = runtime - int(self.period_freq_list[index - 1].get('total_time'))
                self.period_count += int(diff//self.period_frequency)
                return self.period_frequency 
        return self.period_freq_list.get('periodic_frequency') or self.period_frequency

    def periodic_monitor(self):
        period_time = current_time()
        if self.get_runtime(time=period_time) % self.get_periodic_frequency() == 0:
            self.period_finish_time = period_time
            if self.sdk_enabled():
                self.aggregate_stats(crawler=self.crawler) 
                self.send_stats(periodic_stats=self._periodic_stats, overall_stats=self._overall_stats, stats_type='periodic')
                self.reset_periodic_stats()
                self.period_start_time = current_time()
                self.inc_value(self._overall_stats, 'periodic_runs') 
            elif self.periodic_monitor_active(): 
                self.close_periodic_monitor()


    def close_periodic_monitor(self):
        if self.sdk_enabled() and self.periodic_monitor_active():
            self.loop.stop()

    def periodic_monitor_active(self):
        if self.loop is not None:
            if self.loop.running:
                return True
        return False

    def close_job(self, spider=None, reason=None):
        self.period_finish_time = current_time()
        self.spider_close_stats(reason=reason, crawler=self.crawler)
        self.send_stats(periodic_stats=self._periodic_stats, overall_stats=self._overall_stats, stats_type='finished', reason=reason)
        self.close_periodic_monitor()

    
    def response_stats(self, middleware=None, request=None, response=None):
        ## TODO - fallback if the middleware isn't enabled
        # domain = self.get_domain(response.url) 
        # ## TODO - validate response -> return a new status_code
        # ## --> include the domain check within this
        # self.domain_check(domain)
        # proxy = self.get_proxy(request=request, domain=domain)
        domain_data, proxy_data = self.process_domain_proxy(request=request, response=response)
        self.generate_response_stats(request=request, response=response, proxy=proxy_data, domain=domain_data)


    def request_stats(self, request=None):
        domain_data, proxy_data = self.process_domain_proxy(request=request)
        self.generate_request_stats(request=request, proxy=proxy_data, domain=domain_data)

    def exception_stats(self, request=None, exception_class=None):
        domain_data, proxy_data = self.process_domain_proxy(request=request)
        self.generate_exception_stats(request=request, proxy=proxy_data, domain=domain_data, exception_class=exception_class)

    def item_stats(self, signal_type=None, item=None, response=None, spider=None):
        domain_data, proxy_data = self.process_domain_proxy(request=response.request)
        self.generate_item_stats(signal=signal_type, response=response, domain=domain_data, proxy=proxy_data)
 






    






    






    
    

    





    
        



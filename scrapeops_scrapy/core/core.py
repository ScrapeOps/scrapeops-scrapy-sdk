
from twisted.internet import task

from scrapeops_scrapy.exceptions import ScrapeOpsMissingAPIKey
from scrapeops_scrapy.utils import utils
from scrapeops_scrapy.core.controllers import SDKControllers
from scrapeops_scrapy.stats.logger import StatsLogger
from scrapeops_scrapy.normalizer.request_response import RequestResponse



class ScrapeopsCore(SDKControllers, StatsLogger):
    """
        Where the core ScrapeOps Functionality Goes
    """

    def __init__(self):
        SDKControllers.__init__(self)
        StatsLogger.__init__(self)
        
    def start_sdk(self, spider=None, crawler=None):
        if self.not_scrapy_shell():
            self.start_time = self.period_start_time = utils.current_time()
            self.initialize_SDK(spider, crawler=crawler)
            if self.check_api_key_present():
                self.send_setup_request()
                self.spider_open_stats()
                self.start_periodic_monitor()
            else:
                err = ScrapeOpsMissingAPIKey()
                self.deactivate_sdk(reason='no_api_key', error=err)
                raise err
    

    def close_sdk(self, spider=None, reason=None):
        if self.sdk_enabled():
            self.period_finish_time = utils.current_time()
            self.spider_close_stats(reason=reason, crawler=self.crawler)
            self.send_stats(periodic_stats=self._periodic_stats, overall_stats=self._overall_stats, stats_type='finished', reason=reason)
            self.close_periodic_monitor()


    def request_stats(self, request=None):
        if self.sdk_enabled():
            request.meta['sops_time'] = utils.current_time()
            request_response_object = RequestResponse(request=request)
            self.request_response_middleware.normalise_domain_proxy_data(request_response_object)
            self.add_missed_urls_callback(request)
            self.generate_request_stats(request_response_object, request=request)


    def response_stats(self, request=None, response=None):
        if self.sdk_enabled():
            request_response_object = RequestResponse(request=request, response=response)
            self.request_response_middleware.process(request_response_object, response) 
            self.generate_response_stats(request_response_object, request=request, response=response)


    def exception_stats(self, request=None, exception_class=None):
        if self.sdk_enabled():
            request_response_object = RequestResponse(request=request)
            self.request_response_middleware.normalise_domain_proxy_data(request_response_object)
            self.generate_exception_stats(request_response_object, request=request,  exception_class=exception_class)


    def item_stats(self, signal_type=None, item=None, response=None, spider=None):
        if self.sdk_enabled():
            request_response_object = RequestResponse(response=response)
            if response is not None:
                self.request_response_middleware.normalise_domain_proxy_data(request_response_object) 
            if signal_type == 'item_scraped':
                self.item_validation_middleware.validate(request_response_object, item)
            self.generate_item_stats(request_response_object, signal=signal_type, response=response)


    def add_missed_urls_callback(self, request):
        if request.errback is None:
            request.errback = self.failed_url_middleware.log_failure
    
    
            
    """
        PERIODIC MONITOR
    """
    def start_periodic_monitor(self):
        if self.sdk_enabled():
            self.loop = task.LoopingCall(self.periodic_monitor)
            self.periodic_loop = self.loop.start(1, now=False) # Start looping every 1 second (1.0).

    def periodic_monitor(self):
        period_time = utils.current_time()
        if self.get_runtime(time=period_time) % self.get_periodic_frequency() == 0:
            self.period_finish_time = period_time
            if self.sdk_enabled():
                self.aggregate_stats(crawler=self.crawler, middleware=self.scrapeops_middleware_enabled()) 
                self.send_stats(periodic_stats=self._periodic_stats, overall_stats=self._overall_stats, stats_type='periodic')
                self.reset_periodic_stats()
                self.period_start_time = utils.current_time()
                self.inc_value(self._overall_stats, 'periodic_runs') 
            elif self.periodic_monitor_active(): 
                self.close_periodic_monitor()

    def close_periodic_monitor(self):
        if self.periodic_monitor_active():
            self.loop.stop()

    def periodic_monitor_active(self):
        if self.loop is not None:
            if self.loop.running:
                return True
        return False
    
    def get_periodic_frequency(self):
        self.period_count = 0
        runtime = self.get_runtime()
        if self._period_freq_list is None:
            self.period_count = int(runtime//self._period_frequency)
            return self._period_frequency
        for index, row in enumerate(self._period_freq_list):
            if runtime > int(row.get('total_time')):
                if index == 0:
                    period_time = row.get('total_time') 
                else:
                    period_time = row.get('total_time') - self._period_freq_list[index - 1].get('total_time') 
                self.period_count += int(period_time/row.get('periodic_frequency'))
            if runtime <= int(row.get('total_time')):
                self._period_frequency = row.get('periodic_frequency')
                if index == 0:
                    diff = runtime
                else:
                    diff = runtime - int(self._period_freq_list[index - 1].get('total_time'))
                self.period_count += int(diff//self._period_frequency)
                return self._period_frequency 
        return self._period_frequency

    

    
    
 






    






    






    
    

    





    
        



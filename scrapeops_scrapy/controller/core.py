from scrapeops_scrapy.controller.model import SDKModel 
from scrapeops_scrapy.controller.api import SOPSRequest 




class SDKCore(SDKModel):
    """
        Where the core ScrapeOps Functionality Goes
        - send requests to the API
        - deal with errors
    """

    SETUP_ATTEMPT_LIMIT = 3

    def __init__(self):
        SDKModel.__init__(self)

    def send_setup_request(self):
        post_body = self.setup_data()
        data, status = SOPSRequest().setup_request(body=post_body)
        if status.valid:
            self.initialize_job_details(data)
        elif status.action == 'retry' and self._setup_attempts < SDKCore.SETUP_ATTEMPT_LIMIT:
            self._setup_attempts += 1
            self._error_logger.log_error(reason='setup_failed', 
                                         error=status.error, 
                                         data={'setup_attempts': self._setup_attempts})
        elif status.action == 'retry' and self._setup_attempts >= SDKCore.SETUP_ATTEMPT_LIMIT:
            self.deactivate_sdk(reason='exceeded_max_setup_attempts', 
                                error=status.error, 
                                data={'setup_attempts': self._setup_attempts}, 
                                request_type='setup')
        else:
            self.deactivate_sdk(reason=status.error, data=data, request_type='setup')


    def send_stats(self, periodic_stats=None, overall_stats=None, reason=None, stats_type=None):
        self._sdk_run_time = self._sdk_run_time + self._period_frequency ## _period_frequency ???
        post_body = self.stats_data(periodic_stats=periodic_stats, overall_stats=overall_stats, stats_type=stats_type, reason=reason)

        if self.job_active() is False:
            self.send_setup_request()

        ## retest if job is inactive
        if self.job_active() is False:
            self.failed_periods += 1
            self.cache_failed_stats(post_body)
            self._error_logger.log_error(reason=f'sending_{stats_type}_stats_failure', 
                                        data={'failed_periods': self.failed_periods})

        if self.job_active():
            if stats_type == 'finished' and self.export_logs():
                log_body = self.log_data()
                with open(self.log_file, 'rb') as f:
                    data, status = SOPSRequest().stats_request(body=post_body, log_body=log_body, files={'file': f}) 
            else:
                data, status = SOPSRequest().stats_request(body=post_body) 
            
            if status.valid:
                self.update_sdk_settings(data)
                self.reset_failed_stats()
            elif status.action == 'retry' and self.failed_periods < 3:
                self.failed_periods += 1
                self.cache_failed_stats(post_body)
                self._error_logger.log_error(reason=f'sending_{stats_type}_stats_failure', 
                                            error=status.error, 
                                            data={'failed_periods': self.failed_periods})
            else:
                self.deactivate_sdk(reason=f'sending_{stats_type}_stats_failure', error=status.error,
                                    data={'failed_periods': self.failed_periods}, request_type=stats_type)   

            

    """
        SDK CONTROLLERS
    """

    def check_api_key_present(self):
        if self._scrapeops_api_key == None:
            self._sdk_active = False
            return False
        self._sdk_active = True
        return True

    def sdk_enabled(self):
        if self._sdk_active:
            return True
        return False

    def deactivate_sdk(self, reason=None, error=None, request_type=None, data=None):
        self._sdk_active = False
        self._error_logger.sdk_error_close(reason=reason, error=error, request_type=request_type)

    def job_active(self):
        if self.job_id is None and self._sdk_active:
            return False
        return True

    def cache_failed_stats(self, post_body):
        self.cached_failed_stats.append(post_body)
        self.failed_periods = len(self.cached_failed_stats)

    def reset_failed_stats(self):
        self.cached_failed_stats = []
        self.failed_periods = 0

    def update_sdk_settings(self, data):
        self.multi_server = data.get('multi_server', self.multi_server)







    
    
    








         
    

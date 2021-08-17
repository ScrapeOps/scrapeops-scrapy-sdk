from scrapeops_scrapy.controller.model import SDKModel 
from scrapeops_scrapy.controller.api import SDKAPI 
from scrapeops_scrapy.processors.domains import DomainProcessor
from scrapeops_scrapy.processors.proxies import ProxyNormaliser


class SDKCore(SDKModel):
    """
        Where the core ScrapeOps Functionality Goes
        - send requests to the API
        - deal with errors
    """

    def __init__(self):
        SDKModel.__init__(self)


    def start_sdk(self, spider=None, crawler=None):
        self.get_server_details()
        post_body = self.setup_data()
        data = SDKAPI.post_request(body=post_body, request_type='setup', 
                                scrapeops_endpoint=self.scrapeops_endpoint, api_key=self.api_key) 
        valid_setup = SDKAPI.validate_scrapeops_response(data, 'setup')
        if valid_setup:
            self.job_id = data.get('job_id')
            self.job_name = data.get('job_name')
            self.job_group_id = data.get('job_group_id')
            self.multi_server = data.get('multi_server', False)
            self.period_frequency = data.get('stats_period_frequency')
            self.period_freq_list = data.get('stats_period_freq_list', self.period_freq_list )
        elif valid_setup == False and self._setup_attempts < 2:
            self._setup_attempts += 1
        else:
            self.deactivate_sdk(reason='invalid_scrapeops_setup_response', data=data, request_type='setup')

    def send_setup_request(self):
        post_body = self.setup_data()
        data = SDKAPI.post_request(body=post_body, request_type='setup', 
                                scrapeops_endpoint=self.scrapeops_endpoint, api_key=self.api_key) 
        valid_setup = SDKAPI.validate_scrapeops_response(data, 'setup')
        if valid_setup:
            self.job_id = data.get('job_id')
            self.job_name = data.get('job_name')
            self.job_group_id = data.get('job_group_id')
            self.multi_server = data.get('multi_server', False)
            self.period_frequency = data.get('stats_period_frequency')
            self.period_freq_list = data.get('stats_period_freq_list', self.period_freq_list )
        elif valid_setup == False and self._setup_attempts < 3:
            self._setup_attempts += 1
        else:
            self.deactivate_sdk(reason='invalid_scrapeops_setup_response', data=data, request_type='setup')
    
    def job_active(self):
        if self.job_id is None:
            return False
        return True


    def send_stats(self, periodic_stats=None, overall_stats=None, reason=None, stats_type=None):
        self.incremement_sdk_runtime()
        post_body = self.stats_data(periodic_stats=periodic_stats, overall_stats=overall_stats, stats_type=stats_type, reason=reason)

        if self.job_active() == False:
            self.send_setup_request()

        ## fallback if setup attempt failed
        if self.job_active() == False:
            self.send_setup_request()
            self.cache_failed_stats(post_body)

        if self.job_active():
            try:
                data = SDKAPI.post_request(body=post_body, request_type=stats_type, 
                                    scrapeops_endpoint=self.scrapeops_endpoint, api_key=self.api_key) 
                if SDKAPI.validate_scrapeops_response(data, stats_type):
                    self.update_sdk_settings(data)
                    self.reset_failed_stats()
            except:
                self.cache_failed_stats(post_body)
                if self.failed_periods > 3:
                    self.deactivate_sdk(reason=f'sending_{stats_type}_stats_failure', data=data, request_type=stats_type)
        
        



    def cache_failed_stats(self, post_body):
        self.cached_failed_stats.append(post_body)
        self.failed_periods = len(self.cached_failed_stats)

    def reset_failed_stats(self):
        self.cached_failed_stats = []
        self.failed_periods = 0

    def update_sdk_settings(self, data):
        self.multi_server = data.get('multi_server', self.multi_server)


    def process_domain_proxy(self, request=None, response=None):
        url, domain_settings, proxy_settings, proxy_port = self.get_domain_proxy_data(request=request)
        proxy_type = proxy_settings.get('proxy_type', 'no_proxy')
        # print('')
        # print('domain_settings', domain_settings)
        # print('proxy_settings', proxy_settings)
        # print('')

        if proxy_type == 'proxy_api':
            normalised_request = DomainProcessor.normalise_request(url, domain_data=domain_settings)
            normalised_proxy = ProxyNormaliser.normalise_proxy_api(request.url, proxy_data=proxy_settings)
            
        if proxy_type == 'proxy_port':
            normalised_request = DomainProcessor.normalise_request(url, domain_data=domain_settings)
            normalised_proxy = ProxyNormaliser.normalise_proxy_port(proxy_port, proxy_data=proxy_settings)
            
        if proxy_type == 'ip_list_proxy':
            normalised_request = DomainProcessor.normalise_request(url, domain_data=domain_settings)
            normalised_proxy = ProxyNormaliser.normalise_other_proxies(proxy_data=proxy_settings)

        if proxy_type == 'no_proxy':
            normalised_request = DomainProcessor.normalise_request(url, domain_data=domain_settings)
            normalised_proxy = ProxyNormaliser.normalise_other_proxies(proxy_data=proxy_settings)

        if response is not None:
            ## validators
            pass

        return normalised_request, normalised_proxy


    def get_domain_proxy_data(self, request=None):
        ## using proxy port
        proxy_port = ProxyNormaliser.get_proxy_port2(request=request)
        proxy_port_settings = None
        ip_list_proxy = False

        if proxy_port is not None:

            ## need to put something in place for IPs to catch them
            ip_list_proxy = ProxyNormaliser.check_ip_address(proxy_port)
            proxy_provider = ProxyNormaliser.named_proxy(proxy_port)

            if not ip_list_proxy:
                proxy_port_settings = self._proxies.get(proxy_provider, None) ## returns stored settings (known + unknown)

                if proxy_port_settings is None:
                    proxy_port_settings = SDKAPI.post_request(body={'proxy':proxy_port}, request_type='proxy_data',
                                                            scrapeops_endpoint=self.scrapeops_endpoint, api_key=self.api_key) 
                    self._proxies[proxy_provider] = proxy_port_settings

            if ip_list_proxy:
                ip_list_proxy = True 

        ## domain settings
        domain = DomainProcessor.get_domain(request.url)

        ## if domain is proxy_api
        ## --> me now

        domain_settings = self._domains.get(domain, None)
        proxy_api_settings = None

        if domain_settings is None:
            url, domain_settings, proxy_api_settings = self.get_domain_settings(domain=domain, input_url=request.url)
        
        elif domain_settings is not None:

            ## check if domain is proxy_api 
            proxy_api = domain_settings.get('proxy_api', False)
            if proxy_api:

                ## check if using proxy api endpoint
                using_proxy_api_endpoint = domain_settings.get('valid_endpoint') in request.url
                if using_proxy_api_endpoint:
                    proxy_api_settings = domain_settings 
                    url = DomainProcessor.get_url_proxy_api(url=request.url, proxy_settings=proxy_api_settings)
                    domain = DomainProcessor.get_domain(url)
                    domain_settings = self._domains.get(domain, None)

                    if domain_settings is None:
                        url, domain_settings, _ = self.get_domain_settings(domain=domain, input_url=url) 
                
                if not using_proxy_api_endpoint:
                    proxy_api = False
        
            if not proxy_api:
                url = request.url
                domain_settings = domain_settings
                proxy_api_settings = None

        ## set proxy_settings
        if proxy_api_settings is not None:
            proxy_settings = proxy_api_settings
        elif proxy_port_settings is not None:
            proxy_settings = proxy_port_settings
        elif ip_list_proxy:
            proxy_settings = ProxyNormaliser.create_proxy_settings('ip_list_proxy')
        else:
            proxy_settings = ProxyNormaliser.create_proxy_settings('no_proxy')
        
        return url, domain_settings, proxy_settings, proxy_port


    def get_domain_settings(self, domain=None, input_url=None, request_type=None):
        response_data = SDKAPI.post_request(body={'url':input_url, 'domain': domain}, request_type='domain_data',
                                                                scrapeops_endpoint=self.scrapeops_endpoint, api_key=self.api_key) 
        
        if response_data.get('proxy_api', False):
            proxy_api_settings = response_data.get('proxy_api_settings')
            self._domains[domain] = proxy_api_settings

            true_url = response_data.get('true_url')
            true_domain = DomainProcessor.get_domain(true_url)
            domain_settings = response_data.get('domain_parsing_data')
            if domain_settings.get('domain', '') == '': domain_settings['domain'] =  true_domain
            self._domains[true_domain] = domain_settings
            return true_url, domain_settings, proxy_api_settings

        if response_data.get('proxy_api') == False:
            domain_settings = response_data.get('domain_parsing_data')
            self._domains[domain] = domain_settings
            url = input_url
            return url, domain_settings, None

        
    def get_proxy_settings(self, proxy_provider):
        proxy_settings = self._proxies.get(proxy_provider, None) ## returns stored settings (known + unknown)

        if proxy_settings is None:
            proxy_settings = SDKAPI.post_request(self, body={'proxy':proxy_provider}, request_type='proxy_data',
                                                                scrapeops_endpoint=self.scrapeops_endpoint, api_key=self.api_key) 
            self._proxies[proxy_provider] = proxy_settings
        
        return proxy_settings


    """
        SDK CONTROLLERS
    """

    def check_api_key_present(self):
        if self.api_key == None:
            self.sdk_active = False
            return False
        self.sdk_active = True
        return True

    def sdk_enabled(self):
        if self.sdk_active == True and self.job_id is not None:
            return True
        return False
    
    def incremement_sdk_runtime(self):
        self.sdk_run_time = self.sdk_run_time + self.period_frequency

    def deactivate_sdk(self, reason=None, error=None, request_type=None, data=None):
        self.sdk_active = False
        ## log the error and send
        pass

    def send_sdk_diagnostic_report(self):
        pass

    def catch_errors(self):
        ## decorator
        pass
    
    








         
    

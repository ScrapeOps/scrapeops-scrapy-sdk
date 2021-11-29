from scrapeops_scrapy.core.api import SOPSRequest 
from scrapeops_scrapy.validators.response_validator import ResponseValidator
from scrapeops_scrapy.normalizer.proxies import ProxyNormalizer
from scrapeops_scrapy.normalizer.proxy_port_normalizer import ProxyPortStringNormalizer


class RequestResponseMiddleware(object):

    PROXY_DOMAIN_NORMALIZATION = True
    RESPONSE_VALIDATION = True
    PROXY_ALERTS = False
    FAILED_URL_LOGGER_ENABLED = True
    LOG_MISSED_URLS = False

    def __init__(self, job_group_id, proxy_apis, generic_validators, error_logger, allowed_response_codes):
        self.job_group_id = job_group_id
        self._proxy_apis = proxy_apis
        self._data_coverage_validation = False
        self._domains = {}
        self._proxies = {}
        self._proxy_port_setups = {}
        self._generic_validators = generic_validators
        self._allowed_response_codes = allowed_response_codes
        self._error_logger = error_logger
        self._error_count = 0
        self._error_alerts_sent = {}
        self._missed_urls = {}


    def process(self, request_response_object, response):
        self.normalise_domain_proxy_data(request_response_object)
        self.check_proxy_responses(request_response_object, response)
        self.validate_response_data(request_response_object, response)


    def normalise_domain_proxy_data(self, request_response_object):
        if RequestResponseMiddleware.PROXY_DOMAIN_NORMALIZATION:

            proxy_api = self.normalise_proxy_api(request_response_object)
            if proxy_api is False:
                self.normalise_proxy_port(request_response_object)
            self.normalise_domain_data(request_response_object)

        if RequestResponseMiddleware.PROXY_DOMAIN_NORMALIZATION is False:
            request_response_object.fallback_domain_proxy_details(reason='disabled')
    

    def normalise_proxy_api(self, request_response_object):
        try:
            proxy_api, update = request_response_object.check_proxy_api(self._proxy_apis)
            if proxy_api and update:
                data, status = SOPSRequest().proxy_api_normalisation_request(request_response_object)
                if status.valid:
                    self._proxy_apis[request_response_object.get_proxy_api_name()] = data.get('proxy_parsing_data')
                    request_response_object.update_proxy_api(data.get('proxy_parsing_data'))
                else:
                    if self._proxy_apis.get(request_response_object.get_proxy_api_name()) is None:
                            self._proxy_apis[request_response_object.get_proxy_api_name()] = {}
                    self._proxy_apis[request_response_object.get_proxy_api_name()]['proxy_setup'] = {}
                    self._error_logger.log_error(reason='get_proxy_api_details_failed', 
                                            error=status.error, 
                                            data={'proxy_api': request_response_object.get_proxy_api_name()})
                    request_response_object.fallback_proxy_details(proxy_type='proxy_api', proxy_apis=self._proxy_apis)
            
        except Exception:
            request_response_object.fallback_proxy_details(proxy_type='proxy_api', proxy_apis=self._proxy_apis)
        
        return proxy_api or False


    def normalise_proxy_port(self, request_response_object):
        try:
            if request_response_object.active_proxy_port():
                named_proxy, update = request_response_object.check_proxy_port_type(self._proxies)
                if named_proxy and update:
                    data, status = SOPSRequest().proxy_port_normalisation_request(request_response_object)
                    if status.valid:
                        ProxyNormalizer.update_proxy_details(self._proxies, request_response_object, data, valid=True)
                        ProxyPortStringNormalizer.proxy_port_test(self._proxies, request_response_object, data, valid=True)
                    else:
                        ProxyNormalizer.update_proxy_details(self._proxies, request_response_object, data, valid=False)
                        self._error_logger.log_error(reason='get_proxy_port_details_failed', 
                                                error=status.error, 
                                                data={'proxy_port': request_response_object.get_raw_proxy()})
                
            ## Using No Proxy
            if request_response_object.active_proxy() is False:
                request_response_object.update_no_proxy()

        except Exception:
            request_response_object.fallback_proxy_details(proxy_type='proxy_port')


    def normalise_domain_data(self, request_response_object):
        try:
            ## Normalise domain/page type data
            unknown = request_response_object.check_domain(self._domains)
            if unknown:
                data, status = SOPSRequest().domain_normalisation_request(request_response_object)
                if status.valid:
                    self._domains[request_response_object.get_domain()] = data.get('domain_parsing_data')
                    request_response_object.update_page_type(data.get('domain_parsing_data'))
                else:
                    if self._domains.get(request_response_object.get_domain()) is None:
                        self._domains[request_response_object.get_domain()] = {}
                    self._domains[request_response_object.get_domain()]['url_contains_page_types'] = {}
                    self._domains[request_response_object.get_domain()]['query_param_page_types'] = {}
                    self._domains[request_response_object.get_domain()]['validation_details'] = [] 
                    self._error_logger.log_error(reason='get_domain_details_failed', 
                                            error=status.error, 
                                            data={'real_url': request_response_object.get_real_url()})
                    request_response_object.fallback_domain_data()
        
        except Exception:
            request_response_object.fallback_domain_data()


    def check_proxy_responses(self, request_response_object, response):
        if RequestResponseMiddleware.PROXY_ALERTS:
            if request_response_object.active_proxy_api():
                proxy_details = self._proxy_apis.get(request_response_object.get_proxy_api_name())
                if proxy_details is not None:
                    self.check_proxy_error_codes(request_response_object, proxy_details, response)
            
            if request_response_object.active_named_proxy():
                proxy_details = self._proxies.get(request_response_object.get_proxy_port_name())
                if proxy_details is not None:
                    self.check_proxy_error_codes(request_response_object, proxy_details, response)


    def check_proxy_error_codes(self, request_response_object, proxy_details, response):
        error_codes = proxy_details.get('error_codes')
        if error_codes is not None:
            status_code = str(response.status)
            error_response = error_codes.get(status_code)
            if error_response is not None:
                if error_response.get('action') == 'alert' and self.should_alert(error_response, status_code):
                    _, status = SOPSRequest().proxy_alert_request(request_response_object, self.job_group_id, error_response, self._error_alerts_sent.get(status_code))
                    if status.valid:
                        self._error_alerts_sent[status_code] += 1
                elif error_response.get('action') == 'monitor':
                    self._error_count += 1
                    if self._error_count  > error_response.get('error_limit', 0) and self.should_alert(error_response, status_code): 
                        _, status = SOPSRequest().proxy_alert_request(request_response_object, self.job_group_id, error_response, self._error_alerts_sent.get(status_code))
                    if status.valid:
                        self._error_alerts_sent[status_code] += 1


    def should_alert(self, error_response, status_code):
        if self._error_alerts_sent.get(status_code) is None:
            self._error_alerts_sent[status_code] = 0
            return True
        if self._error_alerts_sent.get(status_code) is not None:
            if self._error_alerts_sent[status_code] < error_response.get('alert_limit'):
                return True
        return False


    def validate_response_data(self, request_response_object, response=None):
        if RequestResponseMiddleware.RESPONSE_VALIDATION and response is not None:
            if response.status == 200:
                domain_tests = ResponseValidator.get_domain_tests(request_response_object, self._domains)
                ResponseValidator.validate(request_response_object, response, domain_tests=domain_tests, generic_tests=self._generic_validators)

            if response.status != 200 and ResponseValidator.failed_scan(request_response_object, self._domains):
                ResponseValidator.validate(request_response_object, response, generic_tests=self._generic_validators)


    def failed_url(self, request_response_object, response=None):
        if RequestResponseMiddleware.FAILED_URL_LOGGER_ENABLED:
            if (response.status < 200 and response.status > 300) and (response.status not in self._allowed_response_codes):
                if self._missed_urls.get('count') is None:
                    self._missed_urls['count'] = 0
                self._missed_urls['count'] += 1

                if RequestResponseMiddleware.LOG_MISSED_URLS:
                    if self._missed_urls.get(response.status) is None:
                        self._missed_urls[response.status] = []
                    self._missed_urls[response.status].append(request_response_object.get_real_url())








        
        


        

        




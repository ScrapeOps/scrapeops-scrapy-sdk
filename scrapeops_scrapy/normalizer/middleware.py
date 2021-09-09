from scrapeops_scrapy.controller.api import SOPSRequest 


class RequestResponseMiddleware(object):

    RESPONSE_VALIDATION = False
    FALLBACK_PROXY_SETUP = {}
    FALLBACK_DOMAIN_SETUP = {}

    def __init__(self, proxy_apis, error_logger):
        self._proxy_apis = proxy_apis
        self._data_coverage_validation = False
        self._domains = {}
        self._proxies = {}
        ##self._generic_validators = {}
        self._error_logger = error_logger
        

    def normalise_domain_proxy_data(self, request_response_object):
        """
            Function to determine the proxy and domain of the request. 
            It updates the attributes of the request_response_object, and gets
            normalisation schema from ScrapeOps.
        """
        ## Using Proxy API
        proxy_api, update = request_response_object.check_proxy_api(self._proxy_apis)
        if proxy_api and update:
            data, status = SOPSRequest().proxy_api_normalisation_request(request_response_object)
            if status.valid:
                self._proxy_apis[request_response_object.get_proxy_api_name()] = data.get('proxy_parsing_data')
                request_response_object.update_proxy_api(data.get('proxy_parsing_data'))
            else:
                if self._proxy_apis.get(request_response_object.get_proxy_api_name()) is None:
                        self._proxy_apis[request_response_object.get_proxy_api_name()] = {}
                self._proxy_apis[request_response_object.get_proxy_api_name()]['proxy_setup'] = RequestResponseMiddleware.FALLBACK_PROXY_SETUP
                self._error_logger.log_error(reason='get_proxy_api_details_failed', 
                                         error=status.error, 
                                         data={'proxy_api': request_response_object.get_proxy_api_name()})
                request_response_object.fallback_proxy_details(proxy_type='proxy_api', proxy_apis=self._proxy_apis)
       
        ## Using Proxy Port
        if request_response_object.active_proxy_port() and proxy_api is False:

            named_proxy, unknown = request_response_object.check_proxy_port_type(self._proxies)
            if named_proxy and unknown:
                data, status = SOPSRequest().proxy_normalisation_request(request_response_object)
                if status.valid:
                    self._proxies[request_response_object.get_proxy_name()] = data.get('proxy_parsing_data')
                    request_response_object.update_proxy_port(data.get('proxy_parsing_data'))
                else:
                    if self._proxies.get(request_response_object.get_proxy_name()) is None:
                        self._proxies[request_response_object.get_proxy_name()] = {}
                    self._proxies[request_response_object.get_proxy_name()]['proxy_setup'] = RequestResponseMiddleware.FALLBACK_PROXY_SETUP
                    self._error_logger.log_error(reason='get_proxy_port_details_failed', 
                                            error=status.error, 
                                            data={'proxy_port': request_response_object.get_raw_proxy()})
                    request_response_object.fallback_proxy_details(proxy_type='proxy_port')

            else:
                request_response_object.fallback_proxy_details(proxy_type='proxy_port')

        ## Using No Proxy
        if request_response_object.active_proxy() is False:
            request_response_object.update_no_proxy()

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
                self._domains[request_response_object.get_domain()]['url_contains_page_types'] = RequestResponseMiddleware.FALLBACK_DOMAIN_SETUP
                self._domains[request_response_object.get_domain()]['query_param_page_types'] = RequestResponseMiddleware.FALLBACK_DOMAIN_SETUP
                self._error_logger.log_error(reason='get_domain_details_failed', 
                                        error=status.error, 
                                        data={'real_url': request_response_object.get_real_url()})
                request_response_object.fallback_domain_data()
        


    def validate_response_data(self, request_response_object, response=None):
        if RequestResponseMiddleware.RESPONSE_VALIDATION:
            return request_response_object
        return request_response_object



    def calculate_stats(request_response_object):
        pass







        
        


        

        




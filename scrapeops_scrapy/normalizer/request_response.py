from scrapeops_scrapy.normalizer.domains import DomainNormalizer
from scrapeops_scrapy.normalizer.proxies import ProxyNormalizer
from scrapeops_scrapy.normalizer.proxy_port_normalizer import ProxyPortStringNormalizer


class BaseRequestResponse(object):
    """
        Normalised request/response data structure.
    """

    def __init__(self):
        self.signal_type = None
        self.request = None
        self.raw_url = None
        self.raw_proxy_port = None
        self.raw_domain = None
        self.raw_headers = None
 
        ## Proxy Checks
        self._active_proxy = None
        self._active_proxy_port=None
        self._real_url = None
        self._ip_proxy_list = False
        self._named_proxy = False

        ## Proxy Port
        self._proxy_port_name = None
        self._complete_proxy_port_string = None
        self._proxy_setup_key = None

        self._proxy_port_scheme = ''
        self._proxy_port_username = ''
        self._proxy_port_password = ''
        self._proxy_port_host = ''
        self._proxy_port_port = ''
        self._proxy_port_headers = {}

        self._normalized_proxy_port_username = None
        self._normalized_proxy_port_password = None
        self._normalized_proxy_port_host = None
        self._normalized_proxy_port_port = None
        self._normalized_proxy_port_header_string = None


        ## Proxy API
        self._proxy_api = False
        self._proxy_api_name = None

        ## Validation
        self._validation_test = None
        self._geo = None
        self._custom_tag = None 
        self.json_response_keys = []

        ## Final
        self._domain = None
        self._page_type = None
        self._proxy_type = None
        self._proxy_name = None
        self._proxy_setup = None
        

    """
        Getters
    """

    def get_proxy_name(self):
        return self._proxy_name or 'unknown'
    
    def get_proxy_setup(self):
        return self._proxy_setup or 'unknown'

    def get_domain(self):
        return self._domain or 'unknown'
    
    def get_page_type(self):
        return self._page_type or 'unknown'

    def get_proxy_api_name(self):
        return self._proxy_api_name

    def get_proxy_port_name(self):
        return self._proxy_port_name

    def get_raw_proxy(self):
        return self.raw_proxy_port

    def get_real_url(self):
        return self._real_url or 'unknown'

    def get_validation_test(self):
        return self._validation_test or 'pass'

    def get_geo(self):
        return self._geo or 'none'

    def get_custom_tag(self):
        return self._custom_tag or 'none'

    def get_proxy_port_username(self):
        return self._proxy_port_username

    def get_proxy_port_password(self):
        return self._proxy_port_password

    def get_proxy_port_host(self):
        return self._proxy_port_host

    def get_proxy_port_port(self):
        return self._proxy_port_port
    
    def get_proxy_port_headers(self):
        if self._proxy_port_headers == {}:
            self._proxy_port_headers = ProxyNormalizer.convert_headers(self.raw_headers)
        return self._proxy_port_headers

    def get_complete_proxy_string(self):
        if self._complete_proxy_port_string is None:
            self._complete_proxy_port_string = "{}://{}:{}@{}:{}".format(self._proxy_port_scheme, self._proxy_port_username, self._proxy_port_password,
                                                                            self._proxy_port_host, self._proxy_port_port)
        return self._complete_proxy_port_string

    def get_normalized_proxy_port_username(self):
        if self._normalized_proxy_port_username is None:
            return self._proxy_port_username
        return self._normalized_proxy_port_username

    def get_normalized_proxy_port_password(self):
        if self._normalized_proxy_port_password is None:
            return self._proxy_port_password
        return self._normalized_proxy_port_password

    def get_normalized_proxy_port_host(self):
        if self._normalized_proxy_port_host is None:
            return self._proxy_port_host
        return self._normalized_proxy_port_host

    def get_normalized_proxy_port_port(self):
        if self._normalized_proxy_port_port is None:
            return self._proxy_port_port
        return self._normalized_proxy_port_port

    def get_normalized_proxy_port_header_string(self):
        if self._normalized_proxy_port_header_string is not None:
            return f' -H {self._normalized_proxy_port_header_string}'
        return ''

    def is_json_response(self):
        if len(self.json_response_keys) > 0:
            return True
        return False
    
    def get_json_response_keys(self):
        return self.json_response_keys


    """
        SETTERS
    """

    def set_normalized_proxy_port_username(self, username):
        self._normalized_proxy_port_username = username

    def set_normalized_proxy_port_password(self, password):
        self._normalized_proxy_port_password = password

    def set_normalized_proxy_port_host(self, host):
        self._normalized_proxy_port_host = host

    def set_normalized_proxy_port_port(self, port):
        self._normalized_proxy_port_port = port

    def update_normalized_proxy_port_header_string(self, header_string):
        if self._normalized_proxy_port_header_string is None:
            self._normalized_proxy_port_header_string = header_string
        else:
            self._normalized_proxy_port_header_string = f'{self._normalized_proxy_port_header_string} {header_string}' 

        
    """
        Proxy Type Methods
    """
    
    def active_proxy(self):
        return True if self._active_proxy else False
    
    def active_proxy_port(self):
        return True if self._active_proxy_port else False

    def active_proxy_api(self):
        return self._proxy_api

    def active_named_proxy(self):
        return self._named_proxy

    




class RequestResponse(BaseRequestResponse):

    def __init__(self, signal_type=None, request=None, response=None):
        BaseRequestResponse.__init__(self)
        self.signal_type = signal_type
        if request is not None or response is not None:
            self.request = response.request if request is None else request
            self.raw_url = request.url if response is None else response.url
            self.raw_proxy_port = self.request.meta.get('proxy') 
            self.raw_domain = DomainNormalizer.get_domain(self.raw_url)
            self._active_proxy = self._active_proxy_port = False if self.raw_proxy_port is None else True
            self.raw_headers = self.request.headers

    """
        Domain Normalization
    """

    def check_domain(self, domain_obj):
        domain_details = domain_obj.get(self._domain)
        if domain_details is not None:
            self._page_type = DomainNormalizer.get_page_type(self._real_url, domain_data=domain_details)
            return False
        return True


    def update_page_type(self, domain_details):
        if domain_details is not None:
            self._page_type = DomainNormalizer.get_page_type(self._real_url, domain_data=domain_details)


    def fallback_domain_data(self):
        if self._domain is None:
            self._domain = DomainNormalizer.get_domain(self.raw_url)
        self._page_type = 'none'


    """
        Proxy Port Normalization
    """

    def check_proxy_port_type(self, proxy_ports):
        if ProxyNormalizer.check_ip_address(self.raw_proxy_port):
            self._proxy_type = 'proxy_ip_list'
            self._real_url = self.raw_url
            self._domain = self.raw_domain
            self._proxy_name = 'unknown_ip'
            self._proxy_setup = 'ip_address'
            return False, False
        
        self._named_proxy, self._proxy_port_host, self._proxy_port_name = ProxyNormalizer.check_named_proxy(self.raw_proxy_port) 

        if self._named_proxy:
            self._proxy_type = 'named_proxy_port'
            self._real_url = self.raw_url
            self._domain = self.raw_domain
            self.get_proxy_port_details()
            
            proxy_details = proxy_ports.get(self._proxy_port_name)
            
            if proxy_details is not None:

                if proxy_details.get(self._complete_proxy_port_string) is not None:
                    self._proxy_setup = proxy_details.get(self._complete_proxy_port_string) 
                elif proxy_details.get(self._complete_proxy_port_string) is None and proxy_details.get('known', False):
                    ProxyPortStringNormalizer.run_proxy_string_normalization(self, proxy_ports[self._proxy_port_name].get('normalization_actions'))
                    self.create_normalized_proxy_port_string()
                    self._proxy_setup = proxy_details.get(self._normalized_proxy_port_string) 

                if self._proxy_setup is None:
                    self._proxy_setup = proxy_details.get('fallback') 
                    if proxy_details.get('count') > proxy_details.get('max_count') or proxy_details.get('known') is False:
                        return True, False
                    ## Get details
                    return True, True
                return True, False

            ## get proxy details
            return True, True
    

    def get_proxy_port_details(self):
        self._proxy_name = self._proxy_port_name
        self._proxy_port_port = ProxyNormalizer.get_proxy_port(self.raw_proxy_port)
        self._proxy_port_scheme = ProxyNormalizer.get_proxy_scheme(self.raw_proxy_port)
        if self.raw_headers.get('Proxy-Authorization') is not None:
                auth_string = self.raw_headers.get('Proxy-Authorization').decode('utf-8') 
                self._proxy_port_username, self._proxy_port_password = ProxyNormalizer.decode_basic_auth(auth_string)
        self._complete_proxy_port_string = "{}://{}:{}@{}:{}".format(self._proxy_port_scheme, self._proxy_port_username, self._proxy_port_password,
                                                                            self._proxy_port_host, self._proxy_port_port)

    def create_normalized_proxy_port_string(self):
        username = self.get_normalized_proxy_port_username()
        password = self.get_normalized_proxy_port_password()
        host = self.get_normalized_proxy_port_host()
        port = self.get_normalized_proxy_port_port()
        header_string = self.get_normalized_proxy_port_header_string()
        self._normalized_proxy_port_string = "{}://{}:{}@{}:{}".format(self._proxy_port_scheme, username, password, host, port)
        if header_string != '':
            self._normalized_proxy_port_string = self._normalized_proxy_port_string + header_string

    def proxy_port_setup(self, proxy_details):
        proxy_setup = proxy_details.get('proxy_setup')
        if proxy_setup is None:
            return 'none'
        proxy_string = 'port'
        ## Generate settings string
        return proxy_string

    def update_proxy_port(self, proxy_name, proxy_setup_value):
        self._active_proxy = True
        self._proxy_api = False
        self._proxy_type = 'named_proxy_port'
        self._proxy_name = proxy_name
        self._proxy_setup = proxy_setup_value



    """
        Proxy API Normalization
    """

    def check_proxy_api(self, proxy_apis):
        proxy_details = proxy_apis.get(self.raw_domain)
        if proxy_details is not None:
            if proxy_details.get('proxy_setup') is None:
                self._proxy_api_name = proxy_details.get('proxy_name')
                return True, True
            self.update_proxy_api(proxy_details)
            return True, False
        return False, False


    def update_proxy_api(self, proxy_details):
        self._real_url = DomainNormalizer.get_url_proxy_api(url=self.raw_url, proxy_settings=proxy_details)
        self._domain = DomainNormalizer.get_domain(self._real_url)
        self._active_proxy = True
        self._proxy_api = True
        self._proxy_type = 'proxy_api'
        self._proxy_name = self._proxy_api_name = proxy_details.get('proxy_name')
        self._proxy_setup = self.proxy_api_setup(proxy_details) ## into new file
        self.json_response_keys = proxy_details.get('json_response_keys', [])


    def proxy_api_setup(self, proxy_details):
        proxy_string = 'api'
        proxy_setup = proxy_details.get('proxy_setup')
        if proxy_setup is None:
            return proxy_string
        query_params = DomainNormalizer.parse_url(self.raw_url)
        for key, value in query_params.items():
            key_mapping = proxy_setup.get(key)
            if key_mapping is not None:
                if key_mapping.startswith('**'):
                    proxy_string = f'{proxy_string}_{key_mapping[2:]}'
                elif key_mapping.startswith('--'):
                    proxy_string = f'{proxy_string}_{key_mapping[2:]}={value.lower()}'
                elif key_mapping.startswith('^^'):
                    proxy_string = f'{proxy_string}_{key_mapping[2:]}=false'
                else:
                    proxy_string = f'{proxy_string}_{key_mapping}=true'
        return proxy_string

    
    
    """
        Fallback Proxy Details
    """

    def update_no_proxy(self):
        self._proxy_type = self._proxy_name = 'no_proxy'
        self._proxy_setup = 'none'
        self._real_url = self.raw_url
        self._domain = self.raw_domain
    
    def fallback_proxy_details(self, proxy_type=None, proxy_apis=None):
        if proxy_type == 'proxy_api':
            proxy_details = proxy_apis.get(self.raw_domain)
            if proxy_details is not None:
                self.update_proxy_api(proxy_details)
            else:
                self._proxy_name = 'unknown_proxy_api' if self._proxy_api_name is None else self._proxy_api_name
                self._proxy_setup = 'fallback' if self._proxy_setup is None else self._proxy_setup
        else:
            self._proxy_name = 'unknown_proxy_port' if self._proxy_name is None else self._proxy_name
            self._proxy_setup = 'fallback' if self._proxy_setup is None else self._proxy_setup


    """
        Fallback Proxy + Domain Details
    """
    
    def fallback_domain_proxy_details(self, reason='fallback'):
        """
            Fallback -> if issue with domain/proxy normalising
        """
        self._domain = DomainNormalizer.get_domain(self.raw_url)
        self._page_type = 'none'
        self._proxy_name = reason
        self._proxy_setup = 'none'

    
    """
        Response Validation Tests
    """

    def failed_validation_test(self, test):
        if self._validation_test is None:
            self._validation_test = test.get('validation_msg', 'failed')
        else:
            self._validation_test = f'{self._validation_test}&&{test.get("validation_msg", "failed")}' 
        if test.get('validation_test_id', -1) != -1:
          self._validation_test = f'{self._validation_test}_{test.get("validation_test_id")}'   
















        
        


        

        




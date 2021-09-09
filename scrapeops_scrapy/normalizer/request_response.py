from scrapeops_scrapy.normalizer.domains import DomainNormalizer
from scrapeops_scrapy.normalizer.proxies import ProxyNormalizer


class RequestResponse(object):
    """
        Normalised request/response data structure.
    """

    def __init__(self, signal_type=None, request=None, response=None):
        self.signal_type = signal_type
        self.request = response.request if request is None else request
        self.raw_url = request.url if response is None else response.url
        self.raw_proxy_port = self.request.meta.get('proxy') 
        self.raw_domain = DomainNormalizer.get_domain(self.raw_url)
 
        ## Proxy Checks
        self._active_proxy = self._active_porxy_port = False if self.raw_proxy_port is None else True
        self._real_url = None
        self._ip_proxy_list = False
        self._named_proxy = False

        ## Proxy API
        self._proxy_api = False
        self._proxy_api_name = None

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
        return self._proxy_name
    
    def get_proxy_setup(self):
        return self._proxy_setup

    def get_domain(self):
        return self._domain
    
    def get_page_type(self):
        return self._page_type

    def get_proxy_api_name(self):
        return self._proxy_api_name

    def get_raw_proxy(self):
        return self.raw_proxy_port

    def get_real_url(self):
        return self._real_url

        
    """
        Proxy Type Methods
    """
    
    def active_proxy(self):
        return True if self._active_proxy else False
    
    def active_proxy_port(self):
        return True if self._active_porxy_port else False


    """
        Domain Normalization
    """

    def check_domain(self, domain_obj):
        """
        Checks to see if domain is in list of known domains. If yes, determines the page type.

        Returns: 
            - Boolean -> if it unknown domain
        """
        domain_details = domain_obj.get(self._domain)
        if domain_details is not None:
            self._page_type = DomainNormalizer.get_page_type(self._real_url, domain_data=domain_details)
            return False
        return True


    def update_page_type(self, domain_details):
        self._page_type = DomainNormalizer.get_page_type(self._real_url, domain_data=domain_details)


    def fallback_domain_data(self):
        self._page_type = 'none'


    """
        Proxy Normalization
    """

    def check_proxy_port_type(self, proxy_ports):
        """
        Returns: 
            - Boolean -> if named_proxy
            - Boolean -> if it is a unknown named_proxy
        """
        if ProxyNormalizer.check_ip_address(self.raw_proxy_port):
            self._proxy_type = 'proxy_ip_list'
            self._real_url = self.raw_url
            self._domain = self.raw_domain
            self._proxy_name = 'unknown_ip'
            self._proxy_setup = 'ip_address'
            return False, False
        
        self._named_proxy, self._proxy_name = ProxyNormalizer.check_named_proxy(self.raw_proxy_port) 
        if self._named_proxy:
            self._proxy_type = 'named_proxy_port'
            self._real_url = self.raw_url
            self._domain = self.raw_domain

            if proxy_ports.get(self._proxy_name) is not None:
                proxy_details = proxy_ports.get(self._proxy_name)
                self._proxy_name = proxy_details.get('proxy_name')
                self._proxy_setup = self.proxy_port_setup(proxy_details)

                return True, False

            ## get proxy details
            return True, True


    def check_proxy_api(self, proxy_apis):
        """
            Check if the url is for a known proxy api. 
            If YES, then check if proxy setup detail present. 
            
            If YES, update:
                - active_proxy
                - proxy_api
                - proxy_type
                - proxy_name
                - proxy_setup
            If NO:
                - set proxy_api_name
                - tell RequestResponseMiddleware to get proxy details

            Returns: 
            - Boolean -> if proxy_api
            - Boolean -> if it should be updated
        """
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
        self._proxy_name = proxy_details.get('proxy_name')
        self._proxy_setup = self.proxy_api_setup(proxy_details) ## into new file


    def proxy_api_setup(self, proxy_details):
        proxy_setup = proxy_details.get('proxy_setup')
        if proxy_setup is None:
            return 'none'
        query_params = DomainNormalizer.parse_url(self.raw_url)
        proxy_string = 'api'
        for key, value in query_params.items():
            key_mapping = proxy_setup.get(key, None)
            if key_mapping is not None:
                if len(proxy_string) != 0:
                    proxy_string = proxy_string + '-'
                
                if value.isnumeric():
                    proxy_string = proxy_string + key

                elif value in ['true', 'false', 'True', 'False', 'TRUE', 'FALSE']:
                    proxy_string = proxy_string + key

                else:
                    proxy_string = proxy_string + key + '=' + value
        return proxy_string

    
    def proxy_port_setup(self, proxy_details):
        proxy_setup = proxy_details.get('proxy_setup')
        if proxy_setup is None:
            return 'none'
        proxy_string = 'port'
        return proxy_string

    def update_proxy_port(self, proxy_details):
        self._active_proxy = True
        self._proxy_api = False
        self._proxy_type = 'named_proxy_port'
        self._proxy_name = proxy_details.get('proxy_name')
        self._proxy_setup = self.proxy_port_setup(proxy_details)

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

    
    def fallback_domain_proxy_details(self):
        """
            Fallback -> if issue with domain/proxy normalising
        """
        self._domain = DomainNormalizer.get_domain(self.raw_url)
        self._page_type = 'fallback'
        self._proxy_name = 'fallback' 
        self._proxy_setup = 'fallback'

    def print_request_details(self):
        print('self._real_url', self._real_url)
        print('self._active_proxy', self._active_proxy)
        print('self._proxy_type', self._proxy_type)
        print('')
        print('self._domain', self._domain)
        print('self._page_type', self._page_type)
        print('self._proxy_name', self._proxy_name)
        print('self._proxy_setup', self._proxy_setup)













        
        


        

        




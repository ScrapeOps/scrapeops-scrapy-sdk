import re
import socket

from scrapeops_scrapy.processors.domains import DomainProcessor

class ProxyNormaliser(object):

    def __init__(self):
        pass
    
    @staticmethod
    def get_proxy_port(request=None):
        proxy = request.meta.get('proxy', None)
        if proxy is not None:
            return True, proxy
        return False, proxy

    @staticmethod
    def get_proxy_port2(request=None):
        return request.meta.get('proxy', None)

    @staticmethod
    def named_proxy(proxy_string):
        try: 
            proxy_host = DomainProcessor.get_full_domain(proxy_string)
            return proxy_host
        except:
            return 'ip_list_proxy'

    
    @staticmethod
    def create_proxy_settings(proxy_type):
        return {
            'proxy_name': proxy_type,
            'proxy_type': proxy_type,
            'proxy_setup': ''
        } 


    @staticmethod
    def normalise_proxy(url=None, proxy_data=None):
        proxy_name = proxy_data.get('proxy_name', 'none')
        proxy_type = proxy_data.get('proxy_type', 'none')
        
        if proxy_type == 'proxy_api':
            pass

        if proxy_type == 'proxy_port':
            pass

        if proxy_type == 'proxy_unknown':
            pass

        proxy_settings = proxy_data.get('proxy_settings')
        for key, value in  proxy_settings.items():
            pass

    
    @staticmethod
    def normalise_proxy_api(url, proxy_data=None):
        query_params = DomainProcessor.parse_url(url)
        proxy_settings = proxy_data.get('proxy_settings', None)
        proxy_setup = 'api'
        for key, value in query_params.items():
            key_mapping = proxy_settings.get(key, None)
            if key_mapping is not None:
                if len(proxy_setup) != 0:
                    proxy_setup = proxy_setup + '-'
                
                if value.isnumeric():
                    proxy_setup = proxy_setup + key

                elif value in ['true', 'false', 'True', 'False', 'TRUE', 'FALSE']:
                    proxy_setup = proxy_setup + key

                else:
                    proxy_setup = proxy_setup + key + '=' + value
                
        if proxy_setup == '': proxy_setup = 'none'

        return {
            'proxy_name': proxy_data.get('proxy_name', 'no_proxy_api'),
            'proxy_setup': proxy_setup
        }


    @staticmethod
    def normalise_proxy_port(port_port, proxy_data=None):
        proxy_setup = 'none'
        ## need to normalise proxy parameters
        return {
            'proxy_name': proxy_data.get('proxy_name', 'no_proxy_port'),
            'proxy_setup': proxy_setup
        }

    @staticmethod
    def normalise_other_proxies(proxy_data=None):
        return {
            'proxy_name': proxy_data.get('proxy_type', 'no_proxy'),
            'proxy_setup': 'none'
        }

    @staticmethod
    def remove_brackets(string):
        characters_to_remove = ['[',']']
        new_string = string
        for character in characters_to_remove:
            new_string = new_string.replace(character, "")
        return new_string
    
    
    @staticmethod
    def check_ip_address(proxy_string):
        s = ProxyNormaliser.remove_brackets(proxy_string)
        ipv6_split_string = re.split('://|@|/', s)
        for el in ipv6_split_string:
            if ProxyNormaliser.is_valid_ipv6_address(el): return True
            
        ipv4_split_string = re.split('://|:|@', proxy_string)
        for el in ipv4_split_string:
            if ProxyNormaliser.is_valid_ipv4_address(el): return True
        return False


    @staticmethod
    def is_valid_ipv4_address(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:  # not a valid address
            return False

        return True

    @staticmethod
    def is_valid_ipv6_address(address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:  # not a valid address
            return False
        return True





    @staticmethod
    def get_proxy(request=None, response=None, domain=None, proxy_domains=None, proxy_normalisation=None):
        proxy = 'no_proxy'
        if domain in ProxyNormaliser.PROXY_DOMAINS:

            if ProxyNormaliser.api_proxy_validation(request.url, domain, ProxyNormaliser.PROXY_DICT):
                proxy = domain


        elif request.meta.get('proxy', None) != None:

            ## is it a IP address or proxy port
            return request.meta.get('proxy')
        else:
            proxy = 'no_proxy'
    

    @staticmethod
    def api_proxy_validation(url, domain, proxy_details):
        if proxy_details[domain]['vaild_endpoint'] in url:
            return True
        return False


    @staticmethod
    def check_proxy_api(url, domain, proxy_details):
        api_proxy_domain = proxy_details.get(domain, None)
        if api_proxy_domain != None:
            if proxy_details[domain]['vaild_endpoint'] in url:
                return True, domain            
        return False, None

    @staticmethod
    def api_proxy_settings(url, domain, proxy_details):
        pass 

    
 



   


    







         
    

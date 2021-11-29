import re
import socket

from base64 import b64decode
from urllib.parse import unquote, urlparse

from scrapeops_scrapy.normalizer.domains import DomainNormalizer
from scrapeops_scrapy.exceptions import DecodeError


class ProxyNormalizer(object):

    def __init__(self):
        pass
    
    @staticmethod
    def check_named_proxy(proxy_string):
        try: 
            proxy_address = DomainNormalizer.get_full_domain(proxy_string)
            proxy_domain = DomainNormalizer.get_domain(proxy_string)
            return True, proxy_address, proxy_domain
        except Exception:
            return False, 'ip_list_proxy'

    @staticmethod
    def remove_brackets(string):
        characters_to_remove = ['[',']']
        new_string = string
        for character in characters_to_remove:
            new_string = new_string.replace(character, "")
        return new_string
    
    
    @staticmethod
    def check_ip_address(proxy_string):
        s = ProxyNormalizer.remove_brackets(proxy_string)
        ipv6_split_string = re.split('://|@|/', s)
        for el in ipv6_split_string:
            if ProxyNormalizer.is_valid_ipv6_address(el): return True
            
        ipv4_split_string = re.split('://|:|@', proxy_string)
        for el in ipv4_split_string:
            if ProxyNormalizer.is_valid_ipv4_address(el): return True
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
    def get_proxy_port(proxy_string):
        try:
            return urlparse(proxy_string).port
        except Exception:
            return '80'  
    
    @staticmethod
    def get_proxy_host(proxy_string):
        try: 
            return DomainNormalizer.get_full_domain(proxy_string)
        except Exception:
            return 'ip_list_proxy'

    @staticmethod
    def get_proxy_scheme(proxy_string):
        try:
            return urlparse(proxy_string).scheme
        except Exception:
            return ''

    @staticmethod
    def unknown_proxy_scheme(proxy_string):
        if ProxyNormalizer.get_proxy_scheme(proxy_string) == '':
            return True
        return False

    @staticmethod
    def convert_bytes_to_string(inputValue):
        if isinstance(inputValue, (str, int)):
            return inputValue 
        if isinstance(inputValue, (bytes, bytearray)):
            return inputValue.decode('utf-8') 
        if isinstance(inputValue, list):
            tempList = []
            for el in inputValue:
                if isinstance(el, (bytes, bytearray)):
                   tempList.append(el.decode('utf-8')) 
                elif isinstance(el, list):
                    tempList.append([''])
                elif isinstance(el, dict):
                    tempList.append({'': ''})
                else:
                    tempList.append(el)
            return tempList
        return inputValue

    @staticmethod
    def convert_headers(raw_headers):
        header_dict = {}
        try:
            for key, value in raw_headers.items():
                k = ProxyNormalizer.convert_bytes_to_string(key)
                v = ProxyNormalizer.convert_bytes_to_string(value)
                header_dict[k] = v 
            return header_dict
        except Exception:
            return header_dict

    @staticmethod
    def decode_basic_auth(auth_string):
        """Decode an encrypted HTTP basic authentication string. Returns a tuple of
        the form (username, password), and raises a DecodeError exception if
        nothing could be decoded.
        """
        split = auth_string.strip().split(' ')

        # If split is only one element, try to decode the username and password
        # directly.
        if len(split) == 1:
            try:
                username, password = b64decode(split[0]).decode().split(':', 1)
            except Exception:
                raise DecodeError

        # If there are only two elements, check the first and ensure it says
        # 'basic' so that we know we're about to decode the right thing. If not,
        # bail out.
        elif len(split) == 2:
            if split[0].strip().lower() == 'basic':
                try:
                    username, password = b64decode(split[1]).decode().split(':', 1)
                except Exception:
                    raise DecodeError
            else:
                raise DecodeError

        # If there are more than 2 elements, something crazy must be happening.
        # Bail.
        else:
            raise DecodeError

        return unquote(username), unquote(password)

    @staticmethod
    def create_dict_if_none_exists(dict, key):
        if dict.get(key) is None:
            dict[key] = {}

    @staticmethod
    def update_proxy_details(proxy_dict, request_response_object, data, valid=False):
        proxy_name = request_response_object.get_proxy_port_name()
        if proxy_dict.get(proxy_name) is None:
            proxy_dict[proxy_name] = {}

        ## Update counter
        proxy_port_details = data.get('proxy_port_details')
        count = proxy_dict[proxy_name].get('count', 0)
        proxy_dict[proxy_name]['count'] = count + 1
        proxy_dict[proxy_name]['max_count'] = proxy_port_details.get('max_count', 3)

        if valid:
            proxy_dict[proxy_name]['normalization_actions'] = data.get('normalization_actions')
            proxy_dict[proxy_name]['fallback'] = data.get('fallback', 'port')

            
            proxy_setup_key = proxy_port_details.get('proxy_setup_key')
            proxy_setup_value = proxy_port_details.get('proxy_setup_value')
            if proxy_setup_value is None: 
                proxy_setup_value = data.get('fallback', 'port_type=unknown')
            proxy_dict[proxy_name][proxy_setup_key] = proxy_setup_value
            proxy_dict[proxy_name]['known'] = proxy_port_details.get('proxy_known_domain', False)
            request_response_object.update_proxy_port(proxy_name, proxy_setup_value)

        
        else:
            proxy_dict[proxy_name]['fallback'] = 'port'
            request_response_object.fallback_proxy_details(proxy_type='proxy_port')

        

    

    


    
 



   


    







         
    

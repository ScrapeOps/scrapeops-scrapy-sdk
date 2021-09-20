import re
import socket

from scrapeops_scrapy.normalizer.domains import DomainNormalizer

class ProxyNormalizer(object):

    def __init__(self):
        pass
    
    @staticmethod
    def check_named_proxy(proxy_string):
        try: 
            proxy_host = DomainNormalizer.get_full_domain(proxy_string)
            return True, proxy_host
        except:
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


    
 



   


    







         
    

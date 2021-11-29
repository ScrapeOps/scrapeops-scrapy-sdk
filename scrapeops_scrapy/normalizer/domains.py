from tld import get_tld
from urllib.parse import urlparse, parse_qs

class DomainNormalizer(object):

    def __init__(self):
        pass
    
    @staticmethod
    def get_domain(url):
        #if 'http://' not in url or 'http://' not in url or 'socks5://' not in url
        try:
            if DomainNormalizer.if_localhost(url):
                return 'localhost'
            res = get_tld(url, as_object=True)
            return res.fld
        except Exception:
            return 'unknown'

    @staticmethod
    def get_full_domain(url):
        try:
            if DomainNormalizer.if_localhost(url):
                return 'localhost'
            res = get_tld(url, as_object=True)
            if res.subdomain != '':
                return res.subdomain + '.' + res.fld
            return res.fld
        except Exception:
            return 'unknown'


    @staticmethod
    def if_localhost(url):
        if 'http://localhost:' in url or 'http://127.0.0.1:' in url:
                return True
        return False


    @staticmethod
    def parse_url(url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_dict = {}
        for key, value in query_params.items():
            query_dict[key] = value[0]
        return query_dict


    @staticmethod
    def get_url_proxy_api(url=None, proxy_settings=None):
        url_identifier = proxy_settings.get('url_identifier')
        query_params = DomainNormalizer.parse_url(url)
        url = query_params.get(url_identifier)
        return url

    
    @staticmethod
    def get_page_type(url, domain_data):
        if domain_data.get('url_classification'):
            url_classifiers = domain_data.get('url_contains_page_types', {})
            for k, v in url_classifiers.items():
                if k in url:
                    return v
            query_param_page_types = domain_data.get('query_param_page_types', {})
            query_params = DomainNormalizer.parse_url(url)
            for k, v in query_params.items():
                key_mapping = query_param_page_types.get(k, None)
                if key_mapping is not None:
                    return v
        return 'none'    
    
 



   


    







         
    

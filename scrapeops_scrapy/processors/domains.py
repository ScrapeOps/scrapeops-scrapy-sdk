from tld import get_tld
from urllib.parse import urlparse, parse_qs

class DomainProcessor(object):

    def __init__(self):
        pass
    
    @staticmethod
    def get_domain(url):
        try:
            if DomainProcessor.if_localhost(url):
                return 'localhost'
            res = get_tld(url, as_object=True)
            return res.fld
        except:
            return 'unknown'

    @staticmethod
    def get_full_domain(url):
        try:
            if DomainProcessor.if_localhost(url):
                return 'localhost'
            res = get_tld(url, as_object=True)
            if res.subdomain != '':
                return res.subdomain + '.' + res.fld
            return res.fld
        except:
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
        query_params = DomainProcessor.parse_url(url)
        url = query_params.get(url_identifier)
        return url

    @staticmethod
    def normalise_request(url, domain_data=None):
        if domain_data.get('domain', None) is None:
            return {
            'domain_name': DomainProcessor.get_domain(url),
            'page_type': DomainProcessor.get_page_type(url, domain_data)
        }

        return {
            'domain_name': domain_data.get('domain', 'no_domain'),
            'page_type': DomainProcessor.get_page_type(url, domain_data)
        }

    
    @staticmethod
    def get_page_type(url, domain_data):
        if domain_data.get('url_classification'):
            url_classifiers = domain_data.get('url_contains_page_types', {})
            for k, v in url_classifiers.items():
                if k in url:
                    return v
        return 'none'

    

    
 



   


    







         
    

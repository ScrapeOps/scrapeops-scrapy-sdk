from scrapeops_scrapy.exceptions import ScrapeOpsAPIResponseError
from scrapeops_scrapy.utils.utils import merge_dicts
from scrapeops_scrapy.normalizer.proxies import ProxyNormalizer
import requests
import time

    
class SOPSRequest(object):

    TIMEOUT = 30
    RETRY_LIMIT = 3
    API_KEY = None
    JOB_GROUP_ID = None
    SCRAPEOPS_ENDPOINT = 'https://api.scrapeops.io/'
    SCRAPEOPS_API_VERSION = 'api/v1/'
    SCRAPEOPS_LOGGING_DATA = None
    HIGH_FREQ_ACC = True

    def __init__(self):
        self.data = None
        self.valid = None
        self.action = None
        self.error = None
        
    
    def setup_request(self, body=None):
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'setup/'
        data, error = SOPSRequest.post(url, body=body)
        data, self.valid, self.action, self.error = SOPSRequest.setup_stats_validation(data, error)
        return data, self


    def stats_request(self, body=None, log_body=None, files=None):
        post_body = merge_dicts(SOPSRequest.SCRAPEOPS_LOGGING_DATA, body)
        if files is not None:
           url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'logs/?log_type=scrapy' 
           _, _ = SOPSRequest.post_file(url, body=log_body, files=files)
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'stats/'
        data, error = SOPSRequest.post(url, body=post_body)
        data, self.valid, self.action, self.error = SOPSRequest.setup_stats_validation(data, error)
        return data, self


    def error_report_request(self, error_type=None, body=None, files=None):
        post_body = merge_dicts(SOPSRequest.SCRAPEOPS_LOGGING_DATA, body)
        if files is None:
            url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'errors/?error_type={error_type}'
            data, error = SOPSRequest.post(url, body=post_body, files=files)
        else:
            url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'errors/logs/?error_type={error_type}'
            data, error = SOPSRequest.post_file(url, body=post_body, files=files)
        data, self.valid, self.action, self.error = SOPSRequest.error_report_validation(data, error)
        return data, self
    

    def proxy_normalisation_request(self, request_response_object):
        proxy_name = request_response_object.get_proxy_port_name() 
        proxy_string = request_response_object.get_raw_proxy()
        post_body = merge_dicts(SOPSRequest.SCRAPEOPS_LOGGING_DATA, {'proxy_string': proxy_string})
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'normalizer/proxy/?proxy_name={proxy_name}'
        data, error = SOPSRequest.post(url, body=post_body)
        data, self.valid, self.action, self.error = SOPSRequest.normaliser_validation(data, error, request_type='proxy')
        return data, self


    def proxy_api_normalisation_request(self, request_response_object):
        proxy_name = request_response_object.get_proxy_api_name()
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'normalizer/proxy_api/?proxy_name={proxy_name}'
        data, error = SOPSRequest.post(url, body=SOPSRequest.SCRAPEOPS_LOGGING_DATA)
        data, self.valid, self.action, self.error = SOPSRequest.normaliser_validation(data, error, request_type='proxy_api')
        return data, self

    def proxy_port_normalisation_request(self, request_response_object, test_data=None):
        post_body = merge_dicts(SOPSRequest.SCRAPEOPS_LOGGING_DATA, {
            'proxy_string': request_response_object.get_complete_proxy_string(), 
            'proxy_headers': request_response_object.get_proxy_port_headers(), 
            'domain': request_response_object.get_proxy_port_name()})
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'normalizer/proxy_port/?job_id={SOPSRequest.JOB_GROUP_ID}'
        if test_data is not None:
            post_body['test_data'] = test_data
        data, error = SOPSRequest.post(url, body=post_body)
        data, self.valid, self.action, self.error = SOPSRequest.normaliser_validation(data, error, request_type='proxy_port')
        return data, self


    def domain_normalisation_request(self, request_response_object):
        domain = request_response_object.get_domain()
        real_url = request_response_object.get_real_url()
        post_body = merge_dicts(SOPSRequest.SCRAPEOPS_LOGGING_DATA, {'url': real_url})
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'normalizer/domain/?domain={domain}'
        data, error = SOPSRequest.post(url, body=post_body)
        data, self.valid, self.action, self.error = SOPSRequest.normaliser_validation(data, error, request_type='domain')
        return data, self

    def proxy_alert_request(self, request_response_object, job_group_id, error_response, alerts_sent):
        data = error_response
        data['domain'] = request_response_object.get_domain()
        data['proxy_provider'] = request_response_object.get_proxy_name()
        data['alerts_sent'] = alerts_sent
        post_body = merge_dicts(SOPSRequest.SCRAPEOPS_LOGGING_DATA, data)
        url = SOPSRequest.SCRAPEOPS_ENDPOINT + SOPSRequest.SCRAPEOPS_API_VERSION + f'alerts/proxy/?job_group_id={job_group_id}'
        data, error = SOPSRequest.post(url, body=post_body)
        data, self.valid, self.error = SOPSRequest.generic_validation(data, error)
        return data, self

    def proxy_test_request(self, url, request_response_object):
        data, _ = SOPSRequest.get(url, proxy=request_response_object.get_complete_proxy_string())
        return data

    @staticmethod
    def generic_validation(data, error):
        if data is None:
            return data, False, str(error)
        elif data.get('api_key') == 'invalid':
            return data, False, 'invalid_api_key'
        elif data.get('job_id') == 'invalid':
            return data, False, 'invalid_job'
        return data, True, None


    @staticmethod
    def setup_stats_validation(data, error):
        if data is None:
            return data, False, 'retry', str(error)
        elif data.get('api_key') == 'invalid':
            return data, False, 'close', 'invalid_api_key'
        elif data.get('job_valid') is not True and data.get('job_id') is None:
            return data, False, 'retry', 'invalid_job'
        return data, True, 'valid', None


    @staticmethod
    def normaliser_validation(data, error, request_type=None):
        if data is None:
            return data, False, 'fallback', str(error)
        elif data.get('api_key') == 'invalid':
            return data, False, 'close', 'invalid_api_key'
        
        ## proxy port 
        elif request_type=='proxy_port' and data.get('proxy_port_details') is None:
            return data, False, 'fallback', 'no_proxy_port_details'

        ## proxy api
        elif request_type=='proxy_api' and data.get('proxy_parsing_data') is None:
            return data, False, 'fallback', 'no_proxy_parsing_data'
        elif request_type=='proxy_api' and data.get('proxy_parsing_data') is not None:
            proxy_parsing_data = data.get('proxy_parsing_data')
            if proxy_parsing_data.get('known_proxy') is False:
                return data, False, 'fallback', 'unknown_proxy'
        
        ## domain specific
        elif request_type=='domain' and data.get('domain_parsing_data') is None:
            return data, False, 'fallback', 'no_domain_parsing_data'
        return data, True, 'valid', None

    
    @staticmethod
    def error_report_validation(data, error):
        if data is None:
            return data, False, 'retry', str(error)
        elif data.get('error_logged') is False:
            return data, False, 'close', 'error_not_logged'
        return data, True, 'valid', None

    @staticmethod
    def condense_stats_body(body):
        return {
            'job_id': body.get('job_id'),
            'job_group_id': body.get('job_group_id'),
        }

    @staticmethod
    def get(url, proxy=None, check=True):
        proxies = None
        if ProxyNormalizer.unknown_proxy_scheme(proxy) is not True:
            proxies = {ProxyNormalizer.get_proxy_scheme(proxy): proxy}
        for _ in range(SOPSRequest.RETRY_LIMIT):
            try:
                response = requests.get(url, timeout=SOPSRequest.TIMEOUT, proxies=proxies, headers={'api_key': SOPSRequest.API_KEY}) 
                if check and response.status_code == 401:
                    return None, 'invalid_api_key'
                if response.status_code == 200:
                    data = response.json()
                    return data, None
                else:
                    raise ScrapeOpsAPIResponseError
            except requests.exceptions.ConnectionError as e:
                error = e
                continue
            except ScrapeOpsAPIResponseError as e:
                error = e
                continue
            except Exception as e:
                error = e
                continue
        return None, str(error)


    @staticmethod
    def post(url, body=None, files=None, proxy=None):
        proxies = None
        if ProxyNormalizer.unknown_proxy_scheme(proxy) is not True:
            proxies = {ProxyNormalizer.get_proxy_scheme(proxy): proxy}
        for _ in range(SOPSRequest.RETRY_LIMIT):
            try:
                response = requests.post(url, json=body, timeout=SOPSRequest.TIMEOUT, files=files, proxies=proxies, headers={'api_key': SOPSRequest.API_KEY}) 
                if response.status_code == 401:
                    return None, 'invalid_api_key'
                if response.status_code == 200:
                    data = response.json()
                    return data, None
                else:
                    time.sleep(3)
                    raise ScrapeOpsAPIResponseError
            except requests.exceptions.ConnectionError as e:
                error = e
                continue
            except ScrapeOpsAPIResponseError as e:
                error = e
                continue
            except Exception as e:
                error = e
                continue
        return None, str(error)


    @staticmethod
    def post_file(url, body=None, files=None):
        for _ in range(SOPSRequest.RETRY_LIMIT):
            try:
                response = requests.post(url, data=body, timeout=SOPSRequest.TIMEOUT, files=files, headers={'api_key': SOPSRequest.API_KEY}) 
                if response.status_code == 401:
                    return None, 'invalid_api_key'
                if response.status_code == 200:
                    data = response.json()
                    return data, None
                else:
                    raise ScrapeOpsAPIResponseError
            except requests.exceptions.ConnectionError as e:
                error = e
                continue
            except ScrapeOpsAPIResponseError as e:
                error = e
                continue
            except Exception as e:
                error = e
                continue
        return None, str(error)
    
    


    






    
 



   


    







         
    

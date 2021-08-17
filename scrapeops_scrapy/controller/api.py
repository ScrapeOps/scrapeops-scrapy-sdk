from scrapeops_scrapy.exceptions import ScrapeOpsAPIResponseError
from scrapeops_scrapy.utils.error_handling import exception_handler
import requests


class SDKAPI(object):
    """
        Where the core ScrapeOps Functionality Goes
        - send requests to the API
        - deal with errors
    """

    SDK_RETRIES = 3

    def __init__(self):
        pass
        
    @staticmethod
    @exception_handler
    def post_request(body=None, request_type=None, scrapeops_endpoint=None, api_key=None):
        url = SDKAPI.get_scrapeops_url(request_type, scrapeops_endpoint, api_key)
        for _ in range(SDKAPI.SDK_RETRIES):
            try:
                response = requests.post(url, json=body) 
                if response.status_code == 200:
                    data = response.json()
                    return data
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
        raise error
    
    @staticmethod
    def get_scrapeops_url(request_type, scrapeops_endpoint, api_key):
        if request_type == 'setup':
            return scrapeops_endpoint + 'api/v1/setup/'
        elif request_type in ['periodic', 'finished']:
            return scrapeops_endpoint + f'api/v1/stats/?api_key={api_key}'
        elif request_type == 'error_report':
            return scrapeops_endpoint + 'api/v1/error/'
        elif request_type == 'proxy_data':
            return scrapeops_endpoint + f'api/v1/normalise/proxy?api_key={api_key}'
        elif request_type == 'domain_data':
            return scrapeops_endpoint + f'api/v1/normalise/domain?api_key={api_key}'
        elif request_type == 'normalise':
            return scrapeops_endpoint + f'api/v1/normalise?api_key={api_key}'
    
        
    @staticmethod
    def validate_scrapeops_response(data, request_type):
        if data is None:
            return False
        job_valid = data.get('job_valid', False)
        job_id = data.get('job_id', None)
        stats_period_frequency = data.get('stats_period_frequency', None)

        if request_type == 'setup':
            if job_valid == True and job_id != None and stats_period_frequency != None: 
                return True
            return False
                
        if request_type in ['periodic', 'finished']:
            if job_valid == True and job_id != None: 
                return True
            return False
                
        return False

    


    
 



   


    







         
    

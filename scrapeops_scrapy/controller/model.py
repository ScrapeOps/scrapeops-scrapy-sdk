##import uuid
import socket
import scrapy.settings.default_settings as default_settings
from scrapeops_scrapy.utils import utils
from scrapeops_scrapy.controller.error_logger import ErrorLogger
from scrapeops_scrapy.controller.api import SOPSRequest
from scrapeops_scrapy.normalizer.middleware import RequestResponseMiddleware
from scrapeops_scrapy.utils.error_handling import exception_handler

class SDKModel(object):

    """
        SDK Model:
        The core data types used to control the SDK's operation. 
    """
    
    def __init__(self):
        ## User Data
        self._scrapeops_api_key = None

        ## SDK Data
        self._sdk_active = None
        self._scrapeops_endpoint = None
        self._scrapeops_middleware = None
        self._scrapeops_settings_exclusion_list = []
        self._scrapeops_export_scrapy_logs = False
        self._period_frequency = 60 
        self._period_freq_list = None
        self._sdk_run_time = 0
        self._sdk_retries = 3 ## --> not used
        self._setup_attempts = 0
        self._scrapeops_test_id = None
        self._error_logger = None
        

        ## Spider Data
        self.crawler = None
        self.spider = None
        self.spider_name = None
        self.spider_settings = None
        self.project_name = None
        self.bot_name = None
        self.retry_enabled = None
        self.retry_times = None
        self.log_file = None

        ## Overall Job Data
        self.job_id = None
        self.job_group_id = None
        self.job_group_uuid = None
        self.job_group_version = None
        self.start_time = None
        self.finish_time = None
        self.server_hostname = None
        self.server_ip = None
        self._proxy_apis  = {}
        self._generic_validators = {}
        self.multi_server = False
        self.failed_urls = []

        ## Period Data
        self.period_start_time = None
        self.period_finish_time = None
        self.period_run_time = 0
        self.period_concurrency = 0
        self.period_count = 0
        
        ## ScrapeOps Triggered Jobs
        self._scrapeops_server_id = None
        self.job_group_type = None

        ## Periodic Monitor
        self.loop = None
        self.periodic_loop = None

        ## Validation/Normalisation Data
        self.proxy_domains = []

        ## Failure 
        self.failed_periods = 0
        self.cached_failed_stats = []

        ## Middleware
        self.request_response_middleware = None

     
    def initialize_SDK(self, spider, crawler=None):

        ## Spider Data
        self.spider = spider
        self.crawler = crawler
        self.spider_name = spider.name
        self.project_name = crawler.settings.get('PROJECT', None) 
        self.bot_name = crawler.settings.get('BOT_NAME', None)
        self.retry_enabled = crawler.settings.get('RETRY_ENABLED', None) 
        self.retry_times = crawler.settings.get('RETRY_TIMES', None) 
        self.log_file = crawler.settings.get('LOG_FILE', None) 

        ## Job Data
        self.job_args = utils.get_args()
        self.job_group_name = crawler.settings.get('SCRAPEOPS_JOB_NAME', self.get_job_name())
        self.job_group_uuid = crawler.settings.get('SCRAPEOPS_JOB_GROUP_IDENTIFIER', self.get_uuid()) ## Multi-server
        self.job_group_version = crawler.settings.get('SCRAPEOPS_JOB_VERSION', self.get_job_version())

        ## SDK Setup Data
        self.check_spider_attributes(spider)
        self.get_settings(spider)
        self._scrapeops_api_key = SOPSRequest.API_KEY = crawler.settings.get('SCRAPEOPS_API_KEY', None)
        self._scrapeops_endpoint = SOPSRequest.SCRAPEOPS_ENDPOINT = crawler.settings.get('SCRAPEOPS_ENDPOINT', 'https://api.scrapeops.io/')
        self._scrapeops_middleware = utils.scrapeops_middleware_installed(self.spider_settings)
        self._scrapeops_job_start = crawler.settings.get('SCRAPEOPS_JOB_START', utils.current_time()) ## Multi-server
        self._scrapeops_server_id = crawler.settings.get('SCRAPEOPS_SERVER_ID', "-1")
        self._scrapeops_debug_mode = crawler.settings.get('SCRAPEOPS_DEBUG_MODE', False)
        self._scrapeops_settings_exclusion_list = crawler.settings.get('SCRAPEOPS_SETTINGS_EXLUSION_LIST', [])
        self._scrapeops_export_scrapy_logs = self.get_export_logs(crawler) 
        self.get_server_details()
        self.check_scrapeops_triggered_job(crawler)
        self.initialize_error_logger()

    

    def initialize_job_details(self, data):
        self.job_id = data.get('job_id')
        self.job_name = data.get('job_name')
        self.job_group_id = SOPSRequest.JOB_GROUP_ID = data.get('job_group_id')
        self.multi_server = data.get('multi_server', False)
        self._period_frequency = data.get('stats_period_frequency')
        self._period_freq_list = data.get('stats_period_freq_list')
        self._proxy_apis = data.get('proxy_apis', {})
        self._generic_validators = data.get('generic_validators', [])
        self._error_logger.update_error_logger(self.job_group_name, self.job_group_id)
        self.update_sdk_settings(data)
        self.initialize_request_response_middleware()
        

    def initialize_request_response_middleware(self):
        if self.request_response_middleware is None:
            self.request_response_middleware = RequestResponseMiddleware(self.job_group_id, 
                                                                            self._proxy_apis, 
                                                                            self._generic_validators, 
                                                                            self._error_logger)
    

    def update_sdk_settings(self, data):
        self._sdk_active = data.get('sdk_active', self._sdk_active) 
        self.multi_server = data.get('multi_server', self.multi_server)
        self._scrapeops_export_scrapy_logs = data.get('scrapeops_export_scrapy_logs', self._scrapeops_export_scrapy_logs) 
        SOPSRequest.SCRAPEOPS_ENDPOINT = data.get('scrapeops_endpoint', SOPSRequest.SCRAPEOPS_ENDPOINT) 
        SOPSRequest.SCRAPEOPS_API_VERSION = data.get('scrapeops_api_version', SOPSRequest.SCRAPEOPS_API_VERSION) 
        RequestResponseMiddleware.PROXY_DOMAIN_NORMALIZATION = data.get('proxy_domain_normalization', RequestResponseMiddleware.PROXY_DOMAIN_NORMALIZATION) 
        RequestResponseMiddleware.PROXY_ALERTS = data.get('proxy_alerts', RequestResponseMiddleware.PROXY_ALERTS)
        RequestResponseMiddleware.RESPONSE_VALIDATION = data.get('response_validation', RequestResponseMiddleware.RESPONSE_VALIDATION)
        ErrorLogger.ERROR_LOGGER_ACTIVE = data.get('error_logger', ErrorLogger.ERROR_LOGGER_ACTIVE)


    def initialize_error_logger(self):
        self._error_logger = ErrorLogger(
                                        self.spider, 
                                        self.crawler,
                                        self.spider_settings, 
                                        self.server_hostname, 
                                        self.server_ip,
                                        self.start_time,
                                        self.log_file)


    def check_spider_attributes(self, spider):
        if hasattr(spider, 'sops_test'):
            if spider.sops_test.test_active():
                self._scrapeops_test_id = spider.sops_test.generate_test_id()


    def get_settings(self, spider):
        default_scrapy_settings = default_settings.__dict__
        full_settings = spider.settings.copy_to_dict()
        self.spider_settings = {}
        for key, value in full_settings.items():
            if key not in default_scrapy_settings and self.include_setting(key):
                self.spider_settings[key] = value
            elif default_scrapy_settings.get(key) != value and self.include_setting(key):
                self.spider_settings[key] = value

    def include_setting(self, key):
        exclusion_terms = ['API_KEY', 'APIKEY', 'SECRET_KEY', 'SECRETKEY']
        if key in self._scrapeops_settings_exclusion_list:
            return False
        for term in exclusion_terms:
            if term in key.upper(): return False 
        return True
        

    def setup_data(self):
        return {
            'sops_api_key': self._scrapeops_api_key,
            'job_group_name': self.job_group_name,
            'job_group_version': self.job_group_version,
            'job_group_identifier': self.job_group_uuid,
            'job_group_type': self.job_group_type, 
            'job_settings': self.spider_settings,
            'job_args': self.job_args,
            'job_start_time': self.start_time,
            'sops_sdk': 'scrapy',
            'sops_scrapeops_version': utils.get_scrapeops_version(),
            'sops_scrapy_version': utils.get_scrapy_version(),
            'sops_python_version': utils.get_python_version(),
            'sops_system_version': utils.get_system_version(),
            'sops_middleware_enabled': self._scrapeops_middleware,
            'sops_test_id': self._scrapeops_test_id,
            'sops_server_id': self._scrapeops_server_id,
            'scrapeops_job_start': self._scrapeops_job_start,
            'spider_name': self.spider_name,
            'server_ip': self.server_ip,
            'server_hostname': self.server_hostname,
            'project_name': self.project_name, 
            'bot_name': self.bot_name, 
            'multi_server': self.multi_server,
            'retry_enabled': self.retry_enabled,
            'retry_times': self.retry_times,
        }


    def stats_data(self, periodic_stats=None, overall_stats=None, stats_type=None, reason=None):
        data = {
            'job_id': self.job_id,
            'job_group_id': self.job_group_id,
            'type': stats_type,
            'period_start_time': self.period_start_time,
            'period_finish_time': self.period_finish_time,
            'period_run_time': self._period_frequency, 
            'sdk_run_time': self._sdk_run_time,
            'periodic': periodic_stats,
            'overall': overall_stats,
            'cached_failed_stats': self.cached_failed_stats,
            'periodic_warnings': periodic_stats.get('log_count/WARNING', 0),
            'periodic_errors': periodic_stats.get('log_count/ERROR', 0),
            'periodic_criticals': periodic_stats.get('log_count/CRITICAL', 0),
            'overall_warnings': overall_stats.get('log_count/WARNING', 0),
            'overall_errors': overall_stats.get('log_count/ERROR', 0),
            'overall_criticals': overall_stats.get('log_count/CRITICAL', 0),
            'multi_server': self.multi_server,
            'period_count': self.period_count,
        }

        if stats_type == 'finished':
            data['job_finish_time'] = self.period_finish_time
            data['job_status'] = stats_type
            data['job_finish_reason'] = reason
        return data
    
    def log_data(self):
        return {
            'job_group_id': self.job_group_id,
            'job_group_name': self.job_group_name,
            'job_group_identifier': self.job_group_uuid,
            'spider_name': self.spider_name,
            'sops_sdk': 'scrapy',
        }

    def get_server_details(self):
        try:
            self.server_hostname = socket.gethostname()
            self.server_ip = socket.gethostbyname(self.server_hostname)
        except:
            self.server_hostname = 'unknown'
            self.server_ip = 'unknown'

    def get_runtime(self, time=None):
        if time is None:
            return utils.current_time() - self._scrapeops_job_start 
        return time - self._scrapeops_job_start 

    def scrapeops_middleware_enabled(self):
        if self._scrapeops_middleware == True:
            return True
        return False

    # @exception_handler
    # def get_uuid(self):
    #     self.multi_server = False
    #     return str(uuid.uuid4())

    @exception_handler
    def get_uuid(self):
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_JOB_GROUP_IDENTIFIER' in arg:
                return arg.split('=')[1]
        if hasattr(self.spider, 'sops_job_group_identifier'):
            return self.spider.sops_job_group_identifier
        self.multi_server = False
        return ''

        

    
    def get_job_name(self):
        ## check args
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_JOB_NAME' in arg:
                return arg.split('=')[1]

        ## check spider defined
        if hasattr(self.spider, 'sops_job_name'):
            return self.spider.sops_job_name
        if hasattr(self.spider, 'name'):
            return self.spider.name
        return 'no_spider_name'


    

    def get_job_version(self):
        ## check args
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_JOB_VERSION' in arg:
                return arg.split('=')[1]

        ## check spider defined
        if hasattr(self.spider, 'sops_job_version'):
            return self.spider.sops_job_version
        return 'default'


    def get_export_logs(self, crawler):
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_EXPORT_SCRAPY_LOGS' in arg:
                try: 
                    if arg.split('=')[1] == 'True':
                        return True
                except:
                    pass
        if crawler.settings.get('SCRAPEOPS_EXPORT_SCRAPY_LOGS') is not None:
            return True
        return False

    def export_logs(self):
        if self._scrapeops_export_scrapy_logs and self.log_file is not None:
            return True
        return False

    
    def get_server_id(self, crawler):
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_SERVER_ID' in arg:
                return arg.split('=')[1]
        if crawler.settings.get('SCRAPEOPS_SERVER_ID') is not None:
            return crawler.settings.get('SCRAPEOPS_SERVER_ID')
        return '-1'

    
    def check_scrapeops_triggered_job(self, crawler):
        self._scrapeops_server_id = self.get_server_id(crawler)
        if self._scrapeops_server_id != '-1':
            self.job_group_type = 'scrapeops_triggered'
        else:
            self.job_group_type = 'user_triggered'
    


    

    
         
    
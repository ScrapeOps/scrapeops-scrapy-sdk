from scrapeops_scrapy.utils import utils
from scrapeops_scrapy.core.error_logger import ErrorLogger
from scrapeops_scrapy.core.api import SOPSRequest
from scrapeops_scrapy.normalizer.middleware import RequestResponseMiddleware 
from scrapeops_scrapy.validators.item_validator import ItemValidator 
from scrapeops_scrapy.stats.failed_urls import FailedUrlsHandler
from scrapeops_scrapy.core.model import SDKData



class SDKSetup(SDKData):

    def __init__(self):
        SDKData.__init__(self)


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
        self.allowed_response_codes = crawler.settings.get('HTTPERROR_ALLOWED_CODES', []) 
        self._scrapeops_settings_exclusion_list = crawler.settings.get('SCRAPEOPS_SETTINGS_EXCLUSION_LIST', [])
        self.check_spider_attributes(spider)
        self.get_settings(spider)

        ## Job Data
        self.job_args = utils.get_args()
        self.job_group_name = crawler.settings.get('SCRAPEOPS_JOB_NAME', self.get_job_name())
        self.job_group_uuid = crawler.settings.get('SCRAPEOPS_JOB_GROUP_IDENTIFIER', self.get_uuid()) ## Multi-server
        self.job_group_version = crawler.settings.get('SCRAPEOPS_JOB_VERSION', self.get_job_version())
        self.check_scrapeops_triggered_job(crawler)

        ## System Settings
        self._scrapeops_sdk_version = utils.get_scrapeops_version()
        self._scrapeops_scrapy_version = utils.get_scrapy_version()
        self._scrapeops_python_version = utils.get_python_version()
        self._scrapeops_system_version = utils.get_system_version()
        self.get_server_details()

        ## SDK Setup Data
        self._scrapeops_middleware = utils.scrapeops_middleware_installed(self.spider_settings)
        self._scrapeops_job_start = crawler.settings.get('SCRAPEOPS_JOB_START', utils.current_time()) ## Multi-server
        self._scrapeops_server_id = crawler.settings.get('SCRAPEOPS_SERVER_ID', "-1")
        self._scrapeops_debug_mode = crawler.settings.get('SCRAPEOPS_DEBUG_MODE', False)
        self._scrapeops_export_scrapy_logs = self.get_export_logs(crawler) 

        ## SOPS API
        SOPSRequest.SCRAPEOPS_ENDPOINT = crawler.settings.get('SCRAPEOPS_ENDPOINT', 'https://api.scrapeops.io/')
        SOPSRequest.API_KEY = self._scrapeops_api_key = crawler.settings.get('SCRAPEOPS_API_KEY', None)
        SOPSRequest.SCRAPEOPS_LOGGING_DATA = {'logging_data': self.logging_data()}
        
        ## Middlewares
        self.initialize_middlewares()
        self.initialize_error_logger()

    

    def initialize_middlewares(self):
        if self.item_validation_middleware is None: 
            self.item_validation_middleware = ItemValidator()

        if self.failed_url_middleware is None:
            self.failed_url_middleware = FailedUrlsHandler()
    

    def initialize_error_logger(self):
        self._error_logger = ErrorLogger(
                                        self.spider, 
                                        self.crawler,
                                        self.spider_settings, 
                                        self.server_hostname, 
                                        self.server_ip,
                                        self.start_time,
                                        self.log_file)
        

    def initialize_job_details(self, data):
        self.job_id = data.get('job_id')
        self.job_group_name = data.get('job_group_name', self.job_group_name)
        self.job_group_id = SOPSRequest.JOB_GROUP_ID = data.get('job_group_id')
        self.spider_id= data.get('spider_id')
        self.server_id= data.get('server_id')
        self.project_id= data.get('project_id')
        self.multi_server = data.get('multi_server', False)
        SOPSRequest.HIGH_FREQ_ACC = data.get('high_freq', False)
        self._period_frequency = data.get('stats_period_frequency')
        self._period_freq_list = data.get('stats_period_freq_list')
        self._error_logger.update_error_logger(self.job_group_name, self.job_group_id)
        self.update_sdk_settings(data)
        self.initialize_normalizer_middleware(data)
        SOPSRequest.SCRAPEOPS_LOGGING_DATA = {'logging_data': self.logging_data()}
        

    def initialize_normalizer_middleware(self, data=None):
        if data is not None:
            self._proxy_apis = data.get('proxy_apis', {})
            self._generic_validators = data.get('generic_validators', [])
        if self.request_response_middleware is None:
            self.request_response_middleware = RequestResponseMiddleware(self.job_group_id, 
                                                                            self._proxy_apis, 
                                                                            self._generic_validators, 
                                                                            self._error_logger,
                                                                            self.allowed_response_codes)


    def update_sdk_settings(self, data):
        self._sdk_active = data.get('sdk_active', self._sdk_active) 
        self.multi_server = data.get('multi_server', self.multi_server)
        self.job_group_name = data.get('job_group_name', self.job_group_name)
        self._scrapeops_export_scrapy_logs = data.get('scrapeops_export_scrapy_logs', self._scrapeops_export_scrapy_logs) 

        ## SOPS API Endpoints
        SOPSRequest.SCRAPEOPS_ENDPOINT = data.get('scrapeops_endpoint', SOPSRequest.SCRAPEOPS_ENDPOINT) 
        SOPSRequest.SCRAPEOPS_API_VERSION = data.get('scrapeops_api_version', SOPSRequest.SCRAPEOPS_API_VERSION) 

        ## Normalisation Middleware
        RequestResponseMiddleware.PROXY_DOMAIN_NORMALIZATION = data.get('proxy_domain_normalization', RequestResponseMiddleware.PROXY_DOMAIN_NORMALIZATION) 
        RequestResponseMiddleware.PROXY_ALERTS = data.get('proxy_alerts', RequestResponseMiddleware.PROXY_ALERTS)
        RequestResponseMiddleware.RESPONSE_VALIDATION = data.get('response_validation', RequestResponseMiddleware.RESPONSE_VALIDATION)

        ## Item Validation Middleware
        ItemValidator.ITEM_COVERAGE_ENABLED = data.get('item_coverage_enabled', ItemValidator.ITEM_COVERAGE_ENABLED) 
        ItemValidator.INVALID_ITEM_URLS_LOGGING_ENABLED = data.get('ivalid_item_coverage_url_logging_enabled', ItemValidator.INVALID_ITEM_URLS_LOGGING_ENABLED) 
        ItemValidator.MAX_ITEM_URLS = data.get('max_item_urls', ItemValidator.MAX_ITEM_URLS) 

        ## Failed URL Middleware
        FailedUrlsHandler.FAILED_URL_LOGGER_ENABLED = data.get('FAILED_URL_LOGGER_ENABLED', FailedUrlsHandler.FAILED_URL_LOGGER_ENABLED) 
        FailedUrlsHandler.LOG_MISSED_URLS = data.get('log_missed_urls', FailedUrlsHandler.LOG_MISSED_URLS) 
        FailedUrlsHandler.MAX_LOGGED_URLS = data.get('max_failed_urls', FailedUrlsHandler.MAX_LOGGED_URLS) 

        ## Error Logger
        ErrorLogger.ERROR_LOGGER_ACTIVE = data.get('error_logger', ErrorLogger.ERROR_LOGGER_ACTIVE)


    

    


    







    

    
         
    
import socket
import scrapy.settings.default_settings as default_settings
from scrapeops_scrapy.core.api import SOPSRequest


class BaseSDKModel(object):

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
        self._setup_attempts = 0
        self._scrapeops_test_id = None
        self._error_logger = None
        self._scrapeops_sdk_version = None
        self._scrapeops_scrapy_version = None
        self._scrapeops_python_version = None
        self._scrapeops_system_version = None
        self._scrapeops_job_start = None
        
        ## Spider Data
        self.crawler = None
        self.spider = None
        self.spider_name = None
        self.spider_id= None
        self.spider_settings = None
        self.server_id= None
        self.project_id = None
        self.project_name = None
        self.bot_name = None
        self.retry_enabled = None
        self.retry_times = None
        self.log_file = None

        ## Overall Job Data
        self.job_args = None
        self.job_id = None
        self.job_group_id = None
        self.job_group_uuid = None
        self.job_group_name = None
        self.job_group_version = None
        self.job_custom_groups = None
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
        self.item_validation_middleware = None
        self.failed_url_middleware = None

        self.allowed_response_codes = []


class SDKData(BaseSDKModel):

    def __init__(self):
        BaseSDKModel.__init__(self)


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
            'sops_scrapeops_version': self._scrapeops_sdk_version,
            'sops_scrapy_version': self._scrapeops_scrapy_version,
            'sops_python_version': self._scrapeops_python_version,
            'sops_system_version': self._scrapeops_system_version,
            'sops_middleware_enabled': self._scrapeops_middleware,
            'sops_test_id': self._scrapeops_test_id,
            'sops_server_id': self._scrapeops_server_id,
            'scrapeops_job_start': self._scrapeops_job_start,
            'spider_name': self.spider_name,
            'job_custom_groups': self.job_custom_groups,
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
            'multi_server': self.multi_server,
            'period_count': self.period_count,
            'data_coverage': self.item_validation_middleware.get_item_coverage_data(),
            'invalid_items_count': self.item_validation_middleware.get_num_invalid_items(),
            'field_coverage': self.item_validation_middleware.get_field_coverage(),
            'failed_urls_count': self.failed_url_middleware.get_url_count(),
            'failed_urls_enabled': self.failed_url_middleware.enabled(),
            'scrapy_stats': self.get_scrapy_stats(), 
            'job_custom_groups': self.job_custom_groups,
            'error_details': self.tail.contents(),
            'error_details_cumulative': self.tail.contents('cumulative'),
            'high_freq': SOPSRequest.HIGH_FREQ_ACC
        }

        if stats_type == 'finished':
            data['job_finish_time'] = self.period_finish_time
            data['job_status'] = stats_type
            data['job_finish_reason'] = reason
            data['failed_urls_list'] = self.failed_url_middleware.get_url_list()
            data['invalid_items_urls_list'] = self.item_validation_middleware.get_invalid_items_urls()
        return data
    

    def log_data(self):
        return {
            'job_group_id': self.job_group_id,
            'job_group_name': self.job_group_name,
            'job_group_identifier': self.job_group_uuid,
            'spider_name': self.spider_name,
            'sops_sdk': 'scrapy',
        }

    

    def logging_data(self):
        return {
            'sops_api_key': self._scrapeops_api_key,
            'job_id': self.job_id,
            'job_group_id': self.job_group_id,
            'job_group_identifier': self.job_group_uuid,
            'job_group_name': self.job_group_name,
            'spider_name': self.spider_name,
            'spider_id': self.spider_id,
            'server_id': self.server_id,
            'project_id': self.project_id,
            'project_name': self.project_name, 
            'bot_name': self.bot_name, 
            'server_ip': self.server_ip,
            'server_hostname': self.server_hostname,
            'sops_scrapeops_version': self._scrapeops_sdk_version,
            'sops_scrapy_version': self._scrapeops_scrapy_version,
            'sops_python_version': self._scrapeops_python_version,
            'sops_system_version': self._scrapeops_system_version,
            'sops_middleware_enabled': self._scrapeops_middleware,
            'sops_sdk': 'scrapy',
        }

    def check_spider_attributes(self, spider):
        if hasattr(spider, 'sops_test'):
            if spider.sops_test.test_active():
                self._scrapeops_test_id = spider.sops_test.generate_test_id()
        
        if hasattr(spider, 'sops_custom_groups'):
            if isinstance(spider.sops_custom_groups, dict):
                clean_dict = {}
                for k, v in spider.sops_custom_groups.items():
                    clean_dict[str(k)] = str(v)
                self.job_custom_groups = clean_dict


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
        exclusion_terms = ['API_KEY', 'APIKEY', 'SECRET_KEY', 'SECRETKEY', 'PASSWORD', 'CONNECTION_STRING']
        if key in self._scrapeops_settings_exclusion_list:
            return False
        for term in exclusion_terms:
            if term in key.upper(): return False 
        return True

    
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

    
    def get_server_id(self, crawler):
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_SERVER_ID' in arg:
                return arg.split('=')[1]
        if crawler.settings.get('SCRAPEOPS_SERVER_ID') is not None:
            return crawler.settings.get('SCRAPEOPS_SERVER_ID')
        return '-1'

    
    def check_scrapeops_triggered_job(self, crawler):
        self._scrapeops_server_id = self.get_server_id(crawler)
        if isinstance(self._scrapeops_server_id, str) is False: self._scrapeops_server_id = str(self._scrapeops_server_id)
        if self._scrapeops_server_id != '-1':
            self.job_group_type = 'scrapeops_triggered'
        else:
            self.job_group_type = 'user_triggered'

    def get_server_details(self):
        try:
            self.server_hostname = socket.gethostname()
            self.server_ip = socket.gethostbyname(self.server_hostname)
        except Exception:
            self.server_hostname = 'unknown'
            self.server_ip = 'unknown'

    
    def get_uuid(self):
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_JOB_GROUP_IDENTIFIER' in arg:
                return arg.split('=')[1]
        if hasattr(self.spider, 'sops_job_group_identifier'):
            return self.spider.sops_job_group_identifier
        self.multi_server = False
        return ''


    def get_export_logs(self, crawler):
        for arg in self.job_args.get('args'):
            if 'SCRAPEOPS_EXPORT_SCRAPY_LOGS' in arg:
                try: 
                    if arg.split('=')[1] == 'True':
                        return True
                except Exception:
                    pass
        if crawler.settings.get('SCRAPEOPS_EXPORT_SCRAPY_LOGS') is not None:
            return True
        return False

    def get_scrapy_stats(self):
        scrapy_stats = self.crawler.stats.get_stats()
        return {k:str(v) for (k,v) in scrapy_stats.items()}


import sys
import scrapy
import socket
import scrapeops_scrapy
import platform
import uuid

import scrapy.settings.default_settings as default_settings
from scrapeops_scrapy.utils.utils import current_time, get_args


class SDKModel(object):

    """
        SDK Model:
        The core data types used to control the SDK's operation. 
    """
    
    def __init__(self):
        ## SDK Data
        self.sdk_active = None
        self.api_key = None
        self.scrapeops_endpoint = None
        self._scrapeops_middleware = None
        self.period_frequency = 30 ## default is 30
        self.period_freq_list = []
        self.sdk_run_time = 0
        self.sdk_retries = 3
        self._sops_test_id = None
        self._setup_attempts = 0

        ## Spider Data
        self.spider = None
        self.spider_name = None
        self.spider_settings = None
        self.project_name = None
        self.bot_name = None
        self.retry_enabled = None
        self.retry_times = None

        ## Overall Job Data
        self.job_id = None
        self.job_group_id = None
        self.job_group_uuid = None
        self.start_time = None
        self.finish_time = None
        self.server_hostname = None
        self.server_ip = None
        self._domains = {}
        self._proxies = {}
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
        self.scrapeops_server_id = None
        self.job_group_type = None

        ## Periodic Monitor
        self.loop = None
        self.periodic_loop = None

        ## Validation/Normalisation Data
        self.proxy_domains = []

        ## Failure 
        self.failed_periods = 0
        self.cached_failed_stats = []

        

    def get_spider_details(self, spider, crawler=None):
        self.spider_name = spider.name
        self.spider_id = id(spider)
        if hasattr(spider, 'sops_test'):
            if spider.sops_test.test_active():
                self._sops_test_id = spider.sops_test.generate_test_id()
        self.get_settings(crawler=crawler, spider=spider)
        self.project_name = crawler.settings.get('PROJECT', None)
        self.bot_name = crawler.settings.get('BOT_NAME', None)
        self.retry_enabled = crawler.settings.get('RETRY_ENABLED', None) 
        self.retry_times = crawler.settings.get('RETRY_TIMES', None) 

    def get_settings(self, crawler=None, spider=None):
        default_scrapy_settings = default_settings.__dict__
        full_settings = spider.settings.copy_to_dict()
        #full_settings = crawler.settings.copy_to_dict()
        self.spider_settings = {}
        for key, value in full_settings.items():
            if key not in default_scrapy_settings:
                self.spider_settings[key] = value
            elif default_scrapy_settings.get(key) != value:
                self.spider_settings[key] = value

    def setup_data(self):
        return {
            'sops_api_key': self.api_key,
            'job_group_identifier': self.job_group_uuid,
            'job_group_type': self.job_group_type, 
            'job_settings': self.spider_settings,
            'job_args': self.job_args,
            'job_start_time': self.start_time,
            'sops_sdk': 'scrapy',
            'sops_scrapeops_version': self.get_scrapeops_version(),
            'sops_scrapy_version': self.get_scrapy_version(),
            'sops_python_version': self.get_python_version(),
            'sops_system_version': self.get_system_version(),
            'sops_middleware_enabled': self.scrapeops_middleware_enabled(),
            'sops_test_id': self._sops_test_id,
            'sops_server_id': self.scrapeops_server_id,
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
            'period_run_time': self.period_frequency, 
            'sdk_run_time': self.sdk_run_time,
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
    

    def get_scrapeops_settings(self, crawler=None):
        self.api_key = crawler.settings.get('SCRAPEOPS_API_KEY', None)
        self.scrapeops_endpoint = crawler.settings.get('SCRAPOPS_ENDPOINT', 'https://api.scrapeops.io/')
        self.export_logs = crawler.settings.get('SCRAPEOPS_EXPORT_LOGS', True)

        self.scrapeops_server_id= crawler.settings.get('SCRAPEOPS_SERVER_ID', "-1")
        self.job_group_type = crawler.settings.get('SCRAPEOPS_JOB_GROUP_TYPE', 'user_triggered')
        self.job_group_uuid = crawler.settings.get('SCRAPEOPS_JOB_GROUP_IDENTIFIER', self.get_uuid()) ## passed from scrapyd/SOPS
        
        self.debug_mode = crawler.settings.get('SCRAPEOPS_DEBUG_MODE', False) ## whether the stats are outputted at 
        self.sdk_monitoring_mode = crawler.settings.get('SCRAPEOPS_SDK_MONITORING_MODE', True)

        self._scrapeops_middleware = self.scrapeops_middleware_installed()
        self._scrapeops_job_start = crawler.settings.get('SCRAPEOPS_JOB_START', current_time()) ## need to do properly
        self.job_args = get_args()


    def get_server_details(self):
        try:
            self.server_hostname = socket.gethostname()
            self.server_ip = socket.gethostbyname(self.server_hostname)
        except:
            self.server_hostname = 'unknown'
            self.server_ip = 'unknown'


    def get_python_version(self):
        verions_string = sys.version
        split_string = verions_string.split(' ')
        return split_string[0]

    def get_scrapy_version(self):
        return scrapy.__version__

    def get_scrapeops_version(self):
        return scrapeops_scrapy.__version__

    def get_system_version(self):
        return platform.platform()

    def scrapeops_middleware_enabled(self):
        if self._scrapeops_middleware == True:
            return True
        return False

    def scrapeops_middleware_installed(self):
        downloader_middlerwares = self.spider_settings.get('DOWNLOADER_MIDDLEWARES', {})
        scrapeops_stats = downloader_middlerwares.get('scrapeops.middleware.custom_stats.CustomStats', None)
        if scrapeops_stats is not None:
            return True
        return False
        
    def get_uuid(self):
        self.multi_server = False
        return str(uuid.uuid4())

    def get_runtime(self, time=None):
        if time is None:
            return current_time() - self._scrapeops_job_start 
        return time - self._scrapeops_job_start 

    
         
    
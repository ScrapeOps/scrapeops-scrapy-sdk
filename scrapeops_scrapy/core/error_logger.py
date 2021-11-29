from scrapeops_scrapy.core.api import SOPSRequest 
from scrapeops_scrapy.utils import utils

class ErrorLogger(object):

    ERROR_LOGGER_ACTIVE = True

    def __init__(self, spider, crawler, spider_settings, server_hostname, server_ip, start_time, log_file):
        self.spider = spider
        self.crawler = crawler
        self.bot_name = crawler.settings.get('BOT_NAME', 'None')
        self.spider_settings = spider_settings
        self.server_hostname = server_hostname
        self.server_ip = server_ip
        self.start_time = start_time
        self.log_file = log_file
        self._error_history = []
        self.job_group_name = None
        self.job_group_id = None

    def update_error_logger(self, job_name, job_id):
        self.job_group_name = job_name
        self.job_group_id = job_id

    def log_error(self, reason=None, error=None, data=None, request_type=None):
        if ErrorLogger.ERROR_LOGGER_ACTIVE:
            self._error_history.append({
                'time': utils.current_time(),
                'reason': reason,
                'error': str(error),
                'data': data,
                'request_type': request_type,
            })
    

    def send_error_report(self, error_type=None, body=None, log_data=False):
        if ErrorLogger.ERROR_LOGGER_ACTIVE:
            try:
                data, status = SOPSRequest().error_report_request(error_type=error_type, body=body)
                if status.valid:
                    if log_data and self.log_file is not None and data.get('sdk_error_id') is not None:
                        with open(self.log_file, 'rb') as f:
                            post_body = {
                                            'sops_sdk': 'scrapy',
                                            'spider_name': self.spider.name,
                                            'job_group_id': self.job_group_id,
                                            'job_group_name': self.job_group_name,
                                            'sdk_error_id': data.get('sdk_error_id')
                                        }
                            _, status = SOPSRequest().error_report_request(error_type=error_type, body=post_body, files={'file': f})  
                            if status.valid is False:
                                self.log_error(reason='send_error_logs_failed', error=status.error)  

                if status.valid is False:
                        self.log_error(reason='send_error_report_failed', error=status.error) 
            except Exception:
                pass


    def sdk_error_close(self, reason=None, error=None, request_type=None, data=None):
        if ErrorLogger.ERROR_LOGGER_ACTIVE:
            self.log_error(reason=reason, error=error, data=data, request_type=request_type)
            error_data = {
                'final_reason': reason,
                'sops_sdk': 'scrapy',
                'spider_name': self.spider.name,
                'bot_name': self.bot_name, 
                'server_ip': self.server_ip,
                'server_hostname': self.server_hostname,
                'job_group_id': self.job_group_id,
                'job_group_name': self.job_group_name,
                'job_args': utils.get_args(),
                'job_start_time': self.start_time,
                'sops_scrapeops_version': utils.get_scrapeops_version(),
                'sops_scrapy_version': utils.get_scrapy_version(),
                'sops_python_version': utils.get_python_version(),
                'sops_system_version': utils.get_system_version(),
                'sops_middleware_enabled': utils.scrapeops_middleware_installed(self.spider_settings),
                'error_history': self._error_history,
            }
            
            self.send_error_report(error_type='sdk_close', body=error_data, log_data=True)
    

         



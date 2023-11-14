from scrapeops_scrapy.core.api import SOPSRequest 
from scrapeops_scrapy.normalizer.domains import DomainNormalizer
from scrapeops_scrapy.utils import utils
import json
import logging
import re

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
    

         

class TailLogHandler(logging.Handler):

    retryErrors = [
        "Couldn't bind",
        "Hostname couldn't be looked up'"
        "No route to host",
        "Connection was refused by other side",
        "TCP connection timed out",
        "File used for UNIX socket is no good",
        "Service name given as port is unknown",
        "User aborted connection",
        "User timeout caused connection failure",
        "An SSL error occurred",
        "Could not verify something that was supposed to be signed.",
        "The peer rejected our verify error.",
        "We did not find a certificate where we expected to find one.",
        "Bad Request",
        "Unauthorized",
        "Payment Required",
        "Forbidden",
        "Not Found",
        "Method Not Allowed",
        "Request Time-out",
        "Internal Server Error",
        "Bad Gateway",
        "Service Unavailable",
        "HTTP Version not supported",
        "Gateway Time-out",
        "Unknown Status",
    ]

    def __init__(self, log_dict, log_dict_cumulative):
        logging.Handler.__init__(self)
        self.log_dict = log_dict
        self.log_dict_cumulative = log_dict_cumulative


    def flush(self):
        self.log_dict.clear()
        

    def emit(self, record):

        try:
           
            if(record.levelname == "ERROR" or record.levelname == "WARNING" or record.levelname == "CRITICAL"):
     
                if hasattr(record, 'message'):
                    errorMessage = record.message
                    fileAndLine = record.pathname + ', line: ' + str(record.lineno)
                    dateTime = record.asctime
                    type = record.levelname
                    engine = record.name


                    #covering warnings/probableCause/traceback missing
                    traceback = 'No traceback available'
                    probableCause = ''

                    if record.exc_text is not None:
                        traceback = record.exc_text
                        splitTraceback = traceback.split('\n')
                        probableCause = splitTraceback[len(splitTraceback) - 1]


                    #covering retrys
                    if("Gave up retrying <" in record.message):

                        for retryError in self.retryErrors:
                            if(retryError in record.message):
                                method = record.message.split('<')[1].split(' ')[0]
                                errorMessage = "Error: Gave up retrying " + method + " request - " + retryError
                                fileAndLine = ''
                                probableCause = retryError
                                break
                    
                    # Deprecation Warnings
                    if "ScrapyDeprecationWarning:" in record.message and record.message[0] == "/":
                        splitString = record.message.split("ScrapyDeprecationWarning:")
                        errorMessage = "ScrapyDeprecationWarning: " + splitString[1]
                        probableCause = splitString[0]


                    # "Some Other Error Occurred"
                    if "Some other error occurred: " in record.message: 
                        splitError = record.message.split(' /')
                        cleanError = splitError[0].split(">: ")[1]
                        errorMessage = "Some other error occurred: " + cleanError
                        probableCause = cleanError
                        traceback = record.message


                    # Convert Urls To Domains in Error Messages
                    urls = re.findall(r'(https?://[^\s]+)', errorMessage)
                    for url in urls:
                        domain = DomainNormalizer.get_domain(url)
                        errorMessage = errorMessage.replace(url, domain)


                    if errorMessage in self.log_dict:
                        self.log_dict[errorMessage]['count'] = self.log_dict[errorMessage]['count'] + 1
                    else:
                        self.log_dict[errorMessage] = {
                            'type': type,
                            'engine': engine,
                            'name': errorMessage,
                            'count': 1, 
                            'traceback': traceback, 
                            'message' : probableCause, 
                            'filepath': fileAndLine, 
                            'dateTime': dateTime
                            }

                    if(SOPSRequest.HIGH_FREQ_ACC == True):

                        if(errorMessage in self.log_dict_cumulative):
                            self.log_dict_cumulative[errorMessage]['count'] = self.log_dict_cumulative[errorMessage]['count'] + 1
                        else:

                            self.log_dict_cumulative[errorMessage] =  {
                                'type': type,
                                'engine': engine,
                                'name': errorMessage,
                                'count': 1, 
                                'traceback': traceback, 
                                'message' : probableCause, 
                                'filepath': fileAndLine, 
                                'dateTime': dateTime
                            }
                        
        except Exception as e:
            logging.info('Error: Error in error logger')
            logging.info(e, exc_info=True)

class TailLogger(object):

    def __init__(self):
        self._log_dict = {}
        self._log_dict_cumulative = {}
        self._log_handler = TailLogHandler(self._log_dict, self._log_dict_cumulative)

    def contents(self, type = "diff"):

        if(type == "cumulative"):
            jsonLogsCumulative = json.dumps(self._log_dict_cumulative, indent= 2)
            return jsonLogsCumulative

        else:
            jsonLogs = json.dumps(self._log_dict, indent= 2)
            self._log_handler.flush()
            return jsonLogs

    @property
    def log_handler(self):
        return self._log_handler


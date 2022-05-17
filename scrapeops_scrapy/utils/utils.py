import re
import time
import sys
import sys
import scrapy
import scrapeops_scrapy
import platform

from scrapeops_scrapy.utils.error_handling import exception_handler
from scrapy.utils.python import to_bytes
from twisted.web import http


def current_time():
    t = time.time()
    return int(round(t, 0))

@exception_handler
def get_args():
    arg_dict = {'raw_string': '', 'args': [], 'options': []}
    if sys.argv[0] == 'crawl' or sys.argv[0]  == 'runspider': 
        args = sys.argv[2:]
    else:
        args = sys.argv[1:]
    for index, arg in enumerate(args):
        arg_dict['raw_string'] += append_raw_string(arg)
        if arg.startswith('--'):
            arg_dict['options'].append(arg)
        if arg.startswith('-a'):
            try:                   
                if args[index + 1].startswith('-') is False and args[index + 1].startswith('--') is False: arg_dict['args'].append(args[index + 1])  
            except Exception:
                arg_dict['args'].append(arg)
    return arg_dict


def scrapeops_middleware_installed(spider_settings):
    downloader_middlerwares = spider_settings.get('DOWNLOADER_MIDDLEWARES', {})
    if downloader_middlerwares.get('scrapeops_scrapy.middleware.stats.ScrapeOpsStats') is not None:
        return True
    if downloader_middlerwares.get('scrapeops_scrapy.middleware.retry.RetryMiddleware') is not None:
        return True
    return False

@exception_handler
def get_python_version():
    verions_string = sys.version
    split_string = verions_string.split(' ')
    return split_string[0]

@exception_handler
def get_scrapy_version():
    return scrapy.__version__

@exception_handler
def get_scrapeops_version():
    return scrapeops_scrapy.__version__

@exception_handler
def get_system_version():
    return platform.platform()

def append_raw_string(arg):
    if ' ' in arg:
         return '"{}"  '.format(arg)
    return "{}  ".format(arg)

def merge_dicts(x, y):
    z = x.copy()   
    z.update(y)
    return z

# from scrapy
def get_header_size(headers):
    size = 0
    for key, value in headers.items():
        if isinstance(value, (list, tuple)):
            for v in value:
                size += len(b": ") + len(key) + len(v)
    return size + len(b'\r\n') * (len(headers.keys()) - 1)


def get_status_size(response_status):
    return len(to_bytes(http.RESPONSES.get(response_status, b''))) + 15
    # resp.status + b"\r\n" + b"HTTP/1.1 <100-599> "


def remove_url(string, replacement=""):
    return re.sub(r'http\S+', replacement, string)



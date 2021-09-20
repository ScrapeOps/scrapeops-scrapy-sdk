import functools

from scrapeops_scrapy.exceptions import ScrapeOpsAPIResponseError

def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ScrapeOpsAPIResponseError as e:
            pass
        except Exception as e:
            pass
    return wrapper



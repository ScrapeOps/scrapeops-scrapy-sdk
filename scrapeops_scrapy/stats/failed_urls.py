

class FailedUrlsHandler(object):

    FAILED_URL_LOGGER_ENABLED = True
    LOG_MISSED_URLS = False
    MAX_LOGGED_URLS = 100

    def __init__(self):
        self.failed_urls_count = 0
        self.failed_urls_list = []
        self.errback_free = True

    def log_failure(self, failure):
        if FailedUrlsHandler.FAILED_URL_LOGGER_ENABLED:
            self.failed_urls_count += 1
            if FailedUrlsHandler.LOG_MISSED_URLS and len(self.failed_urls_list) < FailedUrlsHandler.MAX_LOGGED_URLS:
                request = failure.request
                self.failed_urls_list.append(request.url)

    def get_url_count(self):
        return self.failed_urls_count

    def get_url_list(self):
        return self.failed_urls_list

    def disable_errback(self):
        self.errback_free = False

    def enabled(self):
        return self.errback_free



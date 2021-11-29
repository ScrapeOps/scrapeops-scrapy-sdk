

class ScrapeOpsMissingAPIKey(Exception):
    """Indicates that no ScrapeOps API key added"""
    def __init__(self):
        self.message = 'No ScrapeOps API key defined.'
        super().__init__(self.message)
    
    def __str__(self):
        return f'ScrapeOpsMissingAPIKey: {self.message}'


class ScrapeOpsAPIResponseError(Exception):
    
    def __init__(self):
        super().__init__()


class DecodeError(Exception):
    pass
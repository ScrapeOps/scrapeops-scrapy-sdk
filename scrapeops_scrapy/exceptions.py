

class ScrapeOpsMissingAPIKey(Exception):
    """Indicates that no ScrapeOps API key added"""

    pass


class ScrapeOpsAPIResponseError(Exception):
    
    def __init__(self):
        super().__init__()
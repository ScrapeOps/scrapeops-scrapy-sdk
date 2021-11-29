import requests

class ScrapeOpsTest:

    def __init__(self):
        self.active = True
        self.test_id = None
    
    def test_active(self):
        if self.active is True:
            return True
        return False

    def get_test_id(self):
        return self.test_id 

    def generate_test_id(self):
        response = requests.post('https://api.scrapeops.io/api/v1/start_test?api_key=1234&sdk_type=scrapy')
        data = response.json() 
        self.test_id = data.get('test_id', None)
        return self.test_id

    @staticmethod
    def generate_test_settings():
        return {
            'RETRY_TIMES': 0,
            'RETRY_ENABLED': False,
        }

    
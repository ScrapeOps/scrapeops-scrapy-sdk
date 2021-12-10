from itemadapter import ItemAdapter, is_item

class ItemValidator(object):

    ITEM_COVERAGE_ENABLED = True
    INVALID_ITEM_URLS_LOGGING_ENABLED = False
    MAX_ITEM_URLS = 1000

    def __init__(self):
        self.item_coverage = {
            '_SOP_OVERAL_STATS': {
                    'num_items': 0,
                    'num_invalid_items': 0,
                    'num_total_fields': 0,
                    'num_invalid_fields': 0,
                }
        }
        self.items = 0
        self.invalid_items = 0
        self.invalid_items_urls = {}


    def extract_name_fields_item(item):
        return 

    def validate(self, request_response_object, item):
        if ItemValidator.ITEM_COVERAGE_ENABLED and is_item(item):
            try:
                self.increment_items()
                adapter = ItemAdapter(item)
                item_name = ItemValidator.get_item_name(item)
                dict_item = adapter.asdict()
                field_keys = dict_item.keys()
                if item_name is not None and field_keys is not None:
                    domain = request_response_object.get_domain()
                    invalid_fields = []
                    valid_item = True
                    self.check_item_exists(domain, item_name, field_keys)
                    self.item_coverage[domain][item_name]['num_items'] += 1
                    self.increment_total_fields(field_keys)
                    for k in field_keys:
                        if(dict_item.get(k) is not None and dict_item.get(k) != ''):
                            self.item_coverage[domain][item_name]['coverage'][k] += 1
                        else:
                            valid_item = False
                            self.increment_invalid_fields()
                            invalid_fields.append(k)
                    
                    if valid_item is False:
                        self.item_coverage[domain][item_name]['num_invalid_items'] += 1
                        self.increment_invalid_items()
                    if ItemValidator.INVALID_ITEM_URLS_LOGGING_ENABLED and len(invalid_fields) > 0:
                        self.log_invalid_item_url(request_response_object.get_real_url(), item_name, invalid_fields)
            except Exception:
                pass


    def check_item_exists(self, domain, item_name, field_keys):
        if self.item_coverage.get(domain) is None:
            self.item_coverage[domain] = {}
        if self.item_coverage[domain].get(item_name) is None:
            self.item_coverage[domain][item_name] = {
                'coverage': {},
                'num_fields': 0,
                'num_items': 0,
                'num_invalid_items': 0,
            }
            self.item_coverage[domain][item_name]['num_fields'] = len(field_keys)
            for k in field_keys:
                self.item_coverage[domain][item_name]['coverage'][k] = 0
                

    def log_invalid_item_url(self, url, item_name, invalid_fields):
        if self.invalid_items_urls.get(item_name) is None:
            self.invalid_items_urls[item_name] = {}
        missing_fields_string = ItemValidator.generate_fields_key(invalid_fields)
        if self.invalid_items_urls[item_name].get(missing_fields_string) is None:
            self.invalid_items_urls[item_name][missing_fields_string] = []
        if url not in self.invalid_items_urls[item_name][missing_fields_string] and len(self.invalid_items_urls[item_name][missing_fields_string]) < ItemValidator.MAX_ITEM_URLS:
            self.invalid_items_urls[item_name][missing_fields_string].append(url)


    def increment_total_fields(self, fields):
        self.item_coverage['_SOP_OVERAL_STATS']['num_total_fields'] += len(fields)

    def increment_invalid_fields(self):
        self.item_coverage['_SOP_OVERAL_STATS']['num_invalid_fields'] += 1

    def increment_items(self):
        self.items += 1
        self.item_coverage['_SOP_OVERAL_STATS']['num_items'] += 1

    def increment_invalid_items(self):
        self.invalid_items += 1
        self.item_coverage['_SOP_OVERAL_STATS']['num_invalid_items'] += 1

    def get_item_coverage_data(self):
        return self.item_coverage

    def get_num_items(self):
        return self.items

    def get_num_invalid_items(self):
        return self.invalid_items

    def get_invalid_items_urls(self):
        return self.invalid_items_urls
    
    def get_field_coverage(self):
        overall_stats = self.item_coverage.get('_SOP_OVERAL_STATS')
        if overall_stats is None: return 0
        if overall_stats.get('num_total_fields', 0) == 0: return 0
        valid_fields = overall_stats.get('num_total_fields') - overall_stats.get('num_invalid_fields')
        return round((valid_fields / overall_stats.get('num_total_fields'))*100)
    

    @staticmethod
    def get_item_fields(item):
        return item.fields

    @staticmethod
    def get_item_name(item):
        return item.__class__.__name__

    @staticmethod
    def generate_fields_key(fields):
        missing_fields_string = ''
        for field in fields:
            if len(missing_fields_string) > 0:
                 missing_fields_string += '&&'
            missing_fields_string += field
        return missing_fields_string








        
        


        

        




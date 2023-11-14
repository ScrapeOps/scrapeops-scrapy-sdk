from scrapy.http import Response
from scrapeops_scrapy.utils.utils import get_header_size, get_status_size
from random import randint
import json

class ResponseValidator(object):

    def __init__(self):
        pass
    
    @staticmethod
    def validate(request_response_object, response, domain_tests=None, generic_tests=None, geotargeting_tests=None):
        if domain_tests is not None:
            for test in domain_tests:
                if ResponseValidator.run_validation_test(request_response_object, response, test.get('validation_tests', [])) is False:
                    request_response_object.failed_validation_test(test)
                    break
        
        if generic_tests is not None:
            for test in generic_tests:
                if ResponseValidator.run_validation_test(request_response_object, response, test.get('validation_tests', [])) is False:
                    request_response_object.failed_validation_test(test)
                    break


    @staticmethod
    def run_validation_test(request_response_object, response, test_array):
        """
        Returns True if test is passed, False if test is failed.
        """
        fail_counter = 0
        for test in test_array:

            if test.get('test_type') == 'bytes_check':
                if ResponseValidator.bytes_check(response, test.get('threshold', 0), test.get('comparison_type')):
                    fail_counter += 1
                else: return True

            if test.get('test_type') == 'response_length_check':
                if ResponseValidator.response_length_check(ResponseValidator.get_response_text(request_response_object, response), test.get('threshold', 0), test.get('comparison_type')):
                    fail_counter += 1
                else: return True
            
            if test.get('test_type') == 'string_check' and test.get('test_location') == 'body':
                if ResponseValidator.string_check(ResponseValidator.get_response_text(request_response_object, response), test.get('text_check', ''), test.get('comparison_type'), text_slice=test.get('text_slice')):
                    fail_counter += 1
                else: return True
            
            if test.get('test_type') == 'string_check' and test.get('test_location') == 'user_agent':
                pass

            if test.get('test_type') == 'string_check' and test.get('test_location') == 'url':
                if ResponseValidator.string_check(request_response_object.get_real_url(), test.get('text_check', ''), test.get('comparison_type'), text_slice=test.get('text_slice')):
                    fail_counter += 1
                else: return True


        if fail_counter == len(test_array):
            return False
        return True


    @staticmethod
    def get_domain_tests(request_response_object, domains):
        domain_details = domains.get(request_response_object.get_domain()) 
        if domain_details is not None:
            return domain_details.get('validation_details')
        return None


    @staticmethod
    def failed_scan(request_response_object, domains):
        domain_details = domains.get(request_response_object.get_domain()) 
        if domain_details is not None:
            failed_scan_ratio = domain_details.get('failed_generic_scan', 0)
            if failed_scan_ratio == 0: return False
            if failed_scan_ratio == 1: return True
            if randint(1, failed_scan_ratio) == 1: return True
        return False


    @staticmethod
    def get_response_text(request_response_object, response):
        try:
            if isinstance(response, Response): 
                if request_response_object.is_json_response():
                    json_response = json.loads(response.text)
                    json_response_keys = request_response_object.get_json_response_keys()
                    for key in json_response_keys:
                        json_response = json_response.get(key)
                    return json_response or ''    
                return response.text 
            else: return ''
        except AttributeError:
            return ''


    @staticmethod
    def string_check(text, text_check, comparison, text_slice=None):
        if isinstance(text, str):
            if text_slice is not None:
                text = ResponseValidator.string_slice(text, text_slice)
            if comparison == 'contains' and text_check in text:
                return True
            elif comparison == 'not_contain' and text_check not in text:
                return True
        return False


    @staticmethod
    def string_slice(text, text_slice):
        if text_slice.get('active'):
            if (text_slice.get('slice_type') == 'first') and (len(text) > 0):
                return text[:text_slice.get('slice_upper_threshold', len(text))]
            if (text_slice.get('slice_type') == 'last') and (len(text) > 0):
                return text[-text_slice.get('slice_lower_threshold', 0)]
            if text_slice.get('slice_type') == 'range':
                return text[text_slice.get('slice_lower_threshold', 0):text_slice.get('slice_upper_threshold', len(text))]
        return text

    
    @staticmethod
    def bytes_check(response, threshold, comparison):
        if threshold == 0: return False
        reslen = len(response.body) + get_header_size(response.headers) + get_status_size(response.status) + 4
        return ResponseValidator.comparison_operators(reslen, threshold, comparison)


    @staticmethod
    def response_length_check(text, threshold, comparison):
        if threshold == 0: return False
        response_text_length = len(text)
        return ResponseValidator.comparison_operators(response_text_length, threshold, comparison)
    

    @staticmethod
    def comparison_operators(value, threshold, comparison):
        if comparison == 'less_than':
            return value < threshold
        if comparison == 'less_than_equal':
            return value <= threshold
        if comparison == 'greater_than':
            return value > threshold
        if comparison == 'greater_than_equal':
            return value >= threshold
        if comparison == 'equals':
            return value == threshold
        if comparison == 'not_equal':
            return value != threshold
        return False


   


    







         
    

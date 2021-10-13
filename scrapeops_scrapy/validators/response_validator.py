from scrapy.utils.response import response_httprepr
from scrapy.http import Response
from random import randint

class ResponseValidator(object):

    def __init__(self):
        pass
    
    @staticmethod
    def validate(request_response_object, response, domain_tests=None, generic_tests=None, geotargeting_tests=None):
        if domain_tests is not None:
            for test in domain_tests:
                if ResponseValidator.run_validation_test(response, test.get('validation_tests', [])) is False:
                    request_response_object.failed_validation_test(test)
                    break
        
        if generic_tests is not None:
            for test in generic_tests:
                if ResponseValidator.run_validation_test(response, test.get('validation_tests', [])) is False:
                    request_response_object.failed_validation_test(test)
                    break


    @staticmethod
    def run_validation_test(response, test_array):
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
                if ResponseValidator.response_length_check(response, test.get('threshold', 0), test.get('comparison_type')):
                    fail_counter += 1
                else: return True
            
            if test.get('test_type') == 'string_check' and test.get('test_location') == 'body':
                if ResponseValidator.string_check(response, test.get('text_check', ''), test.get('comparison_type'), text_slice=test.get('text_slice')):
                    fail_counter += 1
                else: return True
            
            if test.get('test_type') == 'string_check' and test.get('test_location') == 'user_agent':
                pass

            if test.get('test_type') == 'string_check' and test.get('test_location') == 'url':
                if ResponseValidator.string_check(response.url, test.get('text_check', ''), test.get('comparison_type'), text_slice=test.get('text_slice')):
                    fail_counter += 1
                else: return True

            if test.get('test_type') == 'xpath_check' and test.get('test_location') == 'body':
                if ResponseValidator.xpath_check(response, test.get('xpath_selector', ''), test.get('text_check', ''), test.get('comparison_type')):
                    fail_counter += 1
                else: return True
            
            if test.get('test_type') == 'css_selector_check' and test.get('test_location') == 'body':
                if ResponseValidator.css_selector_check(response, test.get('css_selector', ''), test.get('text_check', ''), test.get('comparison_type')):
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
            failed_scan_ratio = domain_details.get('failed_generic_scan')
            if failed_scan_ratio == 0: return False
            if failed_scan_ratio == 1: return True
            if randint(1, failed_scan_ratio) == 1: return True
        return False


    @staticmethod
    def string_check(response, text_check, comparison, text_slice=None):
        if text_check == '': return False
        text = response.text if isinstance(response, Response) else response
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
            if text_slice.get('slice_type') == 'first':
                return text[:text_slice.get('slice_upper_threshold', len(text))]
            if text_slice.get('slice_type') == 'last':
                return text[text_slice.get('slice_lower_threshold', 0):]
            if text_slice.get('slice_type') == 'range':
                return text[text_slice.get('slice_lower_threshold', 0):text_slice.get('slice_upper_threshold', len(text))]
        return text


    @staticmethod
    def xpath_check(response, xpath_selector, text_check, comparison):
        if xpath_selector == '' or text_check == '': return False
        if comparison == 'equals':
            if response.xpath(xpath_selector).get() == text_check:
                return True
        elif comparison == 'not_equal':
            if response.xpath(xpath_selector).get() != text_check:
                return True
        elif comparison == 'contains':
            text = response.xpath(xpath_selector).get()
            return ResponseValidator.string_check(text, text_check, comparison)
        elif comparison == 'not_contain':
            text = response.xpath(xpath_selector).get()
            return ResponseValidator.string_check(text, text_check, comparison)
        return False


    @staticmethod
    def css_selector_check(response, css_selector, text_check, comparison):
        if comparison == 'equals':
            if response.css(css_selector).get() == text_check:
                return True
        elif comparison == 'not_equal':
            if response.css(css_selector).get() != text_check:
                return True
        elif comparison == 'contains':
            text = response.css(css_selector).get()
            return ResponseValidator.string_check(text, text_check, comparison)
        elif comparison == 'not_contain':
            text = response.css(css_selector).get()
            return ResponseValidator.string_check(text, text_check, comparison)
        return False
    

    @staticmethod
    def bytes_check(response, threshold, comparison):
        if threshold == 0: return False
        reslen = len(response_httprepr(response))
        return ResponseValidator.comparison_operators(reslen, threshold, comparison)


    @staticmethod
    def response_length_check(response, threshold, comparison):
        if threshold == 0: return False
        response_text_length = len(response.text)
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


   


    







         
    

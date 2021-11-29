from scrapeops_scrapy.core.api import SOPSRequest 


class ProxyPortStringNormalizer(object):

    def __init__(self):
        pass
    

    @staticmethod
    def run_proxy_string_normalization(request_response_object, normalization_actions):

        if normalization_actions is not None:
            for action_type, actions in normalization_actions.items():
                if actions is not None:
                    if action_type == 'username':
                        for action_block in actions:
                            updated = ProxyPortStringNormalizer.process_action(request_response_object.get_normalized_proxy_port_username(), action_block)
                            request_response_object.set_normalized_proxy_port_username(updated)

                    if action_type == 'password':
                        for action_block in actions:
                            updated = ProxyPortStringNormalizer.process_action(request_response_object.get_normalized_proxy_port_password(), action_block)
                            request_response_object.set_normalized_proxy_port_password(updated)

                    if action_type == 'host':
                        for action_block in actions:
                            updated = ProxyPortStringNormalizer.process_action(request_response_object.get_normalized_proxy_port_host(), action_block)
                            request_response_object.set_normalized_proxy_port_host(updated)

                    if action_type == 'port':
                        for action_block in actions:
                            updated = ProxyPortStringNormalizer.process_action(request_response_object.get_normalized_proxy_port_port(), action_block)
                            request_response_object.set_normalized_proxy_port_port(updated)

                    if action_type == 'headers':
                        for action_block in actions:
                            updated = ProxyPortStringNormalizer.process_action(request_response_object.get_proxy_port_headers(), action_block)
                            if updated is not None:
                                request_response_object.update_normalized_proxy_port_header_string(updated)


    @staticmethod
    def process_action(inputValue, action_block):

        if action_block.get('action') == 'contains_replace':
            return ProxyPortStringNormalizer.contains_replace(inputValue, action_block)

        if action_block.get('action') == 'contains_replace_all':
            return ProxyPortStringNormalizer.contains_replace_all(inputValue, action_block)

        if action_block.get('action') == 'not_contains_replace_all':
            return ProxyPortStringNormalizer.not_contains_replace_all(inputValue, action_block)
            
        if action_block.get('action') == 'replace_key_value':
            return ProxyPortStringNormalizer.replace_key_value(inputValue, action_block)

        if action_block.get('action') == 'replace_key_seperator_value':
            return ProxyPortStringNormalizer.replace_key_seperator_value(inputValue, action_block)

        if action_block.get('action') == 'check_headers_contains':
            return ProxyPortStringNormalizer.check_headers_contains(inputValue, action_block)

        if action_block.get('action') == 'not_ends_in_replace':
            return ProxyPortStringNormalizer.not_ends_in_replace(inputValue, action_block)
        
        if action_block.get('action') == 'ends_in_replace':
            return ProxyPortStringNormalizer.ends_in_replace(inputValue, action_block)

        if action_block.get('action') == 'equals_replace':
            return ProxyPortStringNormalizer.equals_replace(inputValue, action_block)

        if action_block.get('action') == 'not_equals_replace':
            return ProxyPortStringNormalizer.not_equals_replace(inputValue, action_block)

        if action_block.get('action') == 'is_none_replace':
            return ProxyPortStringNormalizer.is_none_replace(inputValue, action_block)

        if action_block.get('action') == 'in_list_replace':
            return ProxyPortStringNormalizer.in_list_replace(inputValue, action_block)

        if action_block.get('action') == 'not_in_list_replace':
            return ProxyPortStringNormalizer.not_in_list_replace(inputValue, action_block)
        
        
    """
        Conditional Checks
    """
    @staticmethod
    def conditional_checks(inputString, condition=None):
        if condition is not None and condition.get('type') is not None:
            
            ## If substring in string
            if condition.get('type') == "contains":
                if condition.get('value') in inputString:
                    return True
                return False

            if condition.get('type') == "not_contains":
                if condition.get('value') not in inputString:
                    return True
                return False

            if condition.get('type') == "equals":
                if condition.get('value') == inputString:
                    return True
                return False

            if condition.get('type') == "not_equal":
                if condition.get('value') != inputString:
                    return True
                return False

            if condition.get('type') == "not_none":
                if inputString is not None:
                    return True
                return False

            
            ## If all tests fail
            return False
        
        return True
    
    @staticmethod
    def get_condition_arguements(action_block):
        return action_block.get('condition'), action_block.get('arguements')


    """
        Actions
    """

    @staticmethod
    def replace_key_value(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        substring = arguements.get('substring')
        string_seperator = arguements.get('seperator')
        replacement = arguements.get('replacement')

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            outputString = inputString
            splitString = inputString.split(string_seperator)
            for el in splitString:
                if substring.startswith('**'):
                    if el.split('=')[0] == substring[2:]:
                        outputString = outputString.replace(el, replacement)
                elif substring in el:
                    outputString = outputString.replace(el, replacement)
            return outputString
        
        return inputString

    
    @staticmethod
    def replace_key_seperator_value(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        substring = arguements.get('substring')
        string_seperator = arguements.get('seperator')
        replacement = arguements.get('replacement')
        next_value = arguements.get('next_value')

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            outputString = inputString
            splitString = inputString.split(string_seperator)
            for i, el in enumerate(splitString):
                if substring == el:
                    if i + int(next_value) <= len(splitString):
                        outputString = outputString.replace(string_seperator + splitString[i + int(next_value)], replacement)
            return outputString
        
        return inputString


    @staticmethod
    def check_headers_contains(inputheaders, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)
        value = condition.get('value')
        if inputheaders.get(value) is not None:
            header_value = inputheaders.get(value)
            if type(header_value) is list:
                header_value = header_value[0]
            value_check = arguements.get('check_type')
            if value_check == 'equals':
                if header_value == arguements.get('value'):
                    return arguements.get('addition')
            if value_check == 'not_equal':
                if header_value != arguements.get('value'):
                    return arguements.get('addition')
            if value_check is None:
                return arguements.get('addition')
        return None

    @staticmethod
    def not_ends_in_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            if inputString.endswith(substring) is False:
                return arguements.get('replacement')
        
        return inputString

    @staticmethod
    def ends_in_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            if inputString.endswith(substring):
                return arguements.get('replacement')
        
        return inputString


    @staticmethod
    def not_equals_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            if inputString != substring:
                return arguements.get('replacement')
        
        return inputString


    @staticmethod
    def equals_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            if inputString == substring:
                return arguements.get('replacement')
        
        return inputString



    @staticmethod
    def contains_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            replacement = arguements.get('replacement')
            return inputString.replace(substring, replacement)
        
        return inputString

    
    @staticmethod
    def not_contains_replace_all(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            if substring not in inputString:
                return arguements.get('replacement')
        
        return inputString

    @staticmethod
    def contains_replace_all(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if isinstance(inputString, str) is False:
            inputString = str(inputString)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            substring = arguements.get('substring')
            if substring in inputString:
                return arguements.get('replacement')
        
        return inputString

    
    @staticmethod
    def is_none_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            if inputString is None:
                return arguements.get('replacement')
        
        return inputString

    @staticmethod
    def in_list_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            list = arguements.get('list', '').split(',')
            if inputString in list:
                return arguements.get('replacement')
        
        return inputString

    
    @staticmethod
    def not_in_list_replace(inputString, action_block):
        condition, arguements = ProxyPortStringNormalizer.get_condition_arguements(action_block)

        if ProxyPortStringNormalizer.conditional_checks(inputString, condition=condition):
            list = arguements.get('list', '').split(',')
            if inputString not in list:
                return arguements.get('replacement')
        
        return inputString


    @staticmethod
    def proxy_port_test(proxy_dict, request_response_object, data, valid=False):
        if valid:
            proxy_name = request_response_object.get_proxy_port_name()
            test_request = data.get('test_request')
            proxy_port_details = data.get('proxy_port_details')
            proxy_setup_key = proxy_port_details.get('proxy_setup_key')
            if proxy_dict[proxy_name].get('sops_test_request') is None:
                proxy_dict[proxy_name]['sops_test_request'] = test_request
            test_request_count = proxy_dict[proxy_name]['sops_test_request'].get('count', 0)
            if test_request.get('send') and test_request_count < test_request.get('max_count', 1):
                proxy_dict[proxy_name]['sops_test_request']['count'] = test_request_count + 1
                json = SOPSRequest().proxy_test_request(test_request.get('url'), request_response_object)
                json['test_id'] = test_request.get('test_id')
                updated_data, status = SOPSRequest().proxy_port_normalisation_request(request_response_object, test_data=json)
                if status.valid:
                    proxy_port_details = updated_data.get('proxy_port_details')
                    proxy_setup_value = proxy_port_details.get('proxy_setup_value')
                    proxy_dict[proxy_name][proxy_setup_key] = proxy_setup_value


    



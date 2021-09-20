class ExceptionNormalizer(object):

    def __init__(self):
        pass
    
    @staticmethod
    def normalise_exception(exception_class):
        
        if 'ResponseNeverReceived' in exception_class:
            return 'ResponseNeverReceived'

        if 'Timeout' in exception_class:
            return 'Timeout'
        
        if 'TimedOut' in exception_class:
            return 'Timeout'

        if 'PotentialDataLoss' in exception_class:
            return 'PotentialDataLoss'

        if 'ConnectionLost' in exception_class:
            return 'ConnectionLost'

        return exception_class

    

    
 



   


    







         
    

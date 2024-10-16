class EnvironmentContext(object):
    
    def __init__(self, **kwargs):
        '''
        Initialize the environment context.
        '''
        
        # Set the environment variables.
        self.__dict__.update(kwargs)

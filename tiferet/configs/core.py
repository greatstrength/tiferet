# *** imports

# ** core
import json


# *** exceptions

# ** exception: tiferet_error
class TiferetError(Exception):
    '''
    A base exception for Tiferet.
    '''

    def __init__(self, error_code: str, *args):
        '''
        Initialize the exception.
        :param message: The message.
        :type message: str
        '''

        # Set the error code and arguments.
        self.error_code = error_code
        self.args = args
        
        super().__init__(
            json.dumps(dict(
                error_code=error_code,
                args=args
            ))
        )


# ** exception: invalid_model_object
class InvalidModelObject(TiferetError):
    '''
    Exception raised when the model object is invalid.
    '''

    def __init__(self, module_path: str, class_name: str, *args):
        '''
        Initialize the exception.
        :param message: The message.
        :type message: str
        '''

        # Set the module path and class name.
        super().__init__(
            'INVALID_MODEL_OBJECT',
            module_path,
            class_name,
            *args
        )

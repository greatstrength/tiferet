# *** imports

# ** app
from ..app import *
from ..container import *
from ..error import *
from ..feature import *


# *** classes

# ** class: TestProxy
class TestProxy:
    '''
    A test proxy class.
    '''
    
    def __init__(self, config_file: str):
        self.config_file = config_file
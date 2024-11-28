# *** imports

# ** app
from ...repos.tests import *

# ** classes 

# ** class: TestFeatureCommand
class TestFeatureCommand(object):
    '''
    A test feature command class.
    '''
    
    test_repo: TestRepository = None

    def __init__(self, test_repo: TestRepository):
        self.test_repo = test_repo

    def execute(self, param1: str, param2: str, throw_error: bool = False, **kwargs) -> bool:

        # Throw an error if requested.
        assert throw_error == False, 'FEATURE_COMMAND_ERROR'

        # Return the result.
        return (param1, param2)
    
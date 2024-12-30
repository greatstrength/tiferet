# *** imports

# ** app
from ...repos.tests import *

# ** classes 

# ** class: TestServiceCommand
class TestServiceCommand(object):
    '''
    A test feature command class.
    '''
    
    test_repo: TestRepository = None

    def __init__(self, test_repo: TestRepository):
        self.test_repo = test_repo

    def execute(self, param1: str, param2: str, throw_error: bool = False, **kwargs) -> bool:

        # Throw an error if requested.
        assert throw_error == False, 'MY_ERROR'

        # Return the result.
        return (param1, param2)
    

# ** class test_feature_command_with_env_var
class TestServiceCommandWithEnvVar(object):
    '''
    A test feature command class with an environment variable.
    '''

    def execute(self, test_env_var: str, **kwargs) -> str:

        # Return the environment variable.
        return (True, test_env_var)
    
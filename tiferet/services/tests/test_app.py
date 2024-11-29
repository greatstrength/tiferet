# *** imports

# ** app
from . import *


# *** tests
    
# ** test: load_app_context
def test_load_app_context(test_app_repo):
    '''
    Test loading an app interface.
    '''
    
    # Load the app interface.
    app_interface = app_service.load_app_context('test', test_app_repo)
    
    # Ensure the app interface was loaded.
    assert app_interface is not None
    assert app_interface.interface_id == 'test'
    assert app_interface.name == 'Test Interface'

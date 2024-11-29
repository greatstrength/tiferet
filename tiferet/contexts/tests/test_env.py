# *** imports

# ** app
from . import *


# *** fixtures

# ** fixture: app_interface_context
@pytest.fixture
def app_interface_context(environment_context, test_app_interface, feature_context, error_context):
    app_context = environment_context.load_app_context(test_app_interface.id)
    app_context.features = feature_context
    app_context.errors = error_context
    return app_context

# *** tests
    
# ** test: test_environment_context_init
def test_environment_context_init(environment_context, test_app_interface):
    
    # Test initialization
    assert len(environment_context.interfaces) == 1
    assert list(environment_context.interfaces.values())[0] == test_app_interface


# ** test: test_environment_context_load_app_context
def test_environment_context_load_app_context(app_interface_context, test_app_interface):

    # Assert the app context.
    assert isinstance(app_interface_context, AppInterfaceContext)
    assert app_interface_context.interface_id == test_app_interface.id
    assert app_interface_context.name == test_app_interface.name

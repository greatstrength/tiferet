# *** imports

# ** infra
import pytest

# ** app
from ..app import *
from ..container import *
from ..error import *
from ..feature import *


# *** classes

# ** class: TestRepository
class TestRepository:
    '''
    A test repository class.
    '''
    
    pass


# ** class: TestProxy
class TestProxy(TestRepository):
    '''
    A test proxy class.
    '''
    
    def __init__(self, config_file: str):
        self.config_file = config_file


# ** class: MockContainerRepository
class MockContainerRepository(ContainerRepository):
    '''
    A mock container repository.
    '''

    # * method: init
    def __init__(self, attributes: List[ContainerAttribute] = None, constants: Dict[str, str] = None):
        '''
        Initialize the mock container repository.

        :param attributes: The container attributes.
        :type attributes: list
        :param constants: The container constants.
        :type constants: dict
        '''

        # Set the attributes.
        self.attributes = attributes or []

        # Set the constants.
        self.constants = constants or {}

    # * method: get_attribute
    def get_attribute(self, attribute_id, type):
        '''
        Get the container attribute.
        
        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param type: The container attribute type.
        :type type: str
        :return: The container attribute.
        :rtype: ContainerAttribute
        '''

        # Return the container attribute with the matching attribute ID and type.
        return next((attribute for attribute in self.attributes if attribute.id == attribute_id and attribute.type == type), None)
    
    # * method: get_container
    def list_all(self):
        '''
        List all the container attributes and constants.

        :return: The list of container attributes and constants.
        :rtype: List[ContainerAttribute]
        '''

        # Return the container attributes and constants.
        return self.attributes, self.constants
    
    # * method: save_attribute
    def save_attribute(self, attribute):
        '''
        Save the container attribute.

        :param attribute: The container attribute.
        :type attribute: ContainerAttribute
        '''

        # Add the container attribute to the list of attributes.
        self.attributes.append(attribute)


# ** class: MockErrorRepository
class MockErrorRepository(ErrorRepository):
    '''
    A mock error repository.
    '''

    # * method: init
    def __init__(self, errors: List[Error] = None):
        '''
        Initialize the mock error repository.

        :param errors: The errors.
        :type errors: list
        '''

        # Set the errors.
        self.errors = errors or []

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.

        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''

        # Return whether the error exists.
        return any(error.id == id for error in self.errors)
    
    # * method: get
    def get(self, id: str) -> Error:
        '''
        Get the error.

        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: Error
        '''

        # Find the error by ID.
        return next((error for error in self.errors if error.id == id), None)

    # * method: list
    def list(self):
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''
        return self.errors
    
    # * method: save
    def save(self, error: Error):
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''

        # Add the error to the errors.
        self.errors.append(error)


# ** class: MockFeatureRepository
class MockFeatureRepository(FeatureRepository):
    '''
    A mock feature repository.
    '''

    # * method: init
    def __init__(self, features: List[Feature] = None):
        '''
        Initialize the mock feature repository.

        :param features: The features.
        :type features: list
        '''

        # Set the features.
        self.features = features or []

    # * method: exists
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the feature exists.

        :param id: The feature id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the feature exists.
        :rtype: bool
        '''

        # Return whether the feature exists.
        return any(feature.id == id for feature in self.features)
    
    # * method: get
    def get(self, id: str) -> Feature:
        '''
        Get the feature.

        :param id: The feature id.
        :type id: str
        :return: The feature.
        :rtype: Feature
        '''

        # Find the feature by ID.
        return next((feature for feature in self.features if feature.id == id), None)
    
    # * method: list
    def list(self) -> List[Feature]:
        '''
        List all features.

        :return: The list of features.
        :rtype: List[Feature]
        '''

        # Return the features.
        return self.features
    
    # * method: save
    def save(self, feature: Feature):
        '''
        Save the feature.

        :param feature: The feature.
        :type feature: Feature
        '''

        # Add the feature to the list of features.
        self.features.append(feature)

# *** fixtures

# ** fixture: mock_container_repo
@pytest.fixture(scope='session')
def mock_container_repo():
    return MockContainerRepository


# ** fixture: mock_error_repo
@pytest.fixture(scope='session')
def mock_error_repo():
    return MockErrorRepository


# ** fixture: mock_feature_repo
@pytest.fixture(scope='session')
def mock_feature_repo():            
    return MockFeatureRepository


# ** mock: mock_app_repository
@pytest.fixture(scope='session')
def mock_app_repo():
    class MockAppRepository(AppRepository):
        '''
        A mock app repository.
        '''

        # * method: init
        def __init__(self, interfaces: List[AppInterface] = None):
            '''
            Initialize the mock app repository.

            :param interfaces: The app interfaces.
            :type interfaces: list
            '''

            # Set the app interfaces.
            self.interfaces = interfaces or []

        # * method: list_interfaces
        def list_interfaces(self) -> List[AppInterface]:
            '''
            List the app interfaces.

            :return: The app interfaces.
            '''
            return self.interfaces
        
        # * method: get_interface
        def get_interface(self, id: str) -> AppInterface:
            '''
            Get the app interface by ID.
            
            :param id: The app interface ID.
            :type id: str
            :return: The app interface.
            :rtype: AppInterface
            '''

            # Find the app interface by ID.
            return next((interface for interface in self.interfaces if interface.id == id), None)
        
    # Return the mock app repository.
    return MockAppRepository
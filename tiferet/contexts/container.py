# *** imports

# ** core

# ** app
from ..configs import *
from ..models.container import *
from ..repos.container import *


# *** functions

# ** function: create_injector
def create_injector(name: str, **dependencies) -> Any:
    '''
    Create an injector object with the given dependencies.

    :param name: The name of the injector.
    :type name: str
    :param dependencies: The dependencies.
    :type dependencies: dict
    :return: The injector object.
    :rtype: Any
    '''

    # Create container.
    try:
        from dependencies import Injector
        return type(f'{name.capitalize()}Container', (Injector,), {**dependencies})
    except Exception as e:
        raise CreateInjectorFailureError(name, e)


# ** function: import_dependency
def import_dependency(module_path: str, class_name: str) -> Any:
    '''
    Import an object dependency from its configured Python module.

    :param module_path: The module path.
    :type module_path: str
    :param class_name: The class name.
    :type class_name: str
    :return: The dependency.
    :rtype: Any
    '''

    # Import module.
    try:
        from importlib import import_module
        return getattr(import_module(module_path), class_name)
    except Exception as e:
        raise DependencyImportFailureError(module_path, class_name, e)


# *** contexts

# ** contexts: container_context
class ContainerContext(Model):
    '''
    A container context is a class that is used to create a container object.
    '''

    # * attribute: interface_id
    interface_id = StringType(
        required=True,
        metadata=dict(
            description='The interface ID.'
        ),
    )

    # * attribute: attributes
    attributes = DictType(
        ModelType(ContainerAttribute), 
        default={}, 
        required=True,
        metadata=dict(
            description='The container attributes.'
        ),
    )

    # * attribute: constants
    constants = DictType(
        StringType, 
        default={},
        metadata=dict(
            description='The container constants.'
        ),
    )

    # * attribute: feature_flag
    feature_flag = StringType(
        default='core',
        metadata=dict(
            description='The feature flag.'
        ),
    )

    # * attribute: data_flag
    data_flag = StringType(
        metadata=dict(
            description='The data flag.'
        ),
    )

    # * method: init
    def __init__(self, interface_id: str, container_repo: ContainerRepository, feature_flag: str = 'core', data_flag: str = None):
        '''
        Initialize the container context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param container_repo: The container repository.
        :type container_repo: ContainerRepository
        :param interface_flag: The interface flag.
        :type interface_flag: str
        :param feature_flag: The feature flag.
        :type feature_flag: str 
        :param data_flag: The data flag.
        :type data_flag: str
        '''

        # Add the attributes and constants as empty dictionaries.
        attributes = {}
        constants = {}

        # Get and set attributes and constants.
        try:
            attrs, consts = container_repo.list_all()
        except Exception as e:
            raise ContainerAttributeLoadingError(e)

        # Parse the constants.
        for key in consts:
            constants[key] = self.parse_parameter(consts[key])

        # Add the attributes to the context.
        for attr in attrs:

            # If the attribute already exists, set the dependencies.
            if attr.id in attributes:
                for dep in attr.dependencies:
                    attr.set_dependency(dep)
                    continue

            # Otherwise, add the attribute.
            attributes[attr.id] = attr

            # Add any parameters as constants.
            for dep in attr.dependencies:
                for key in dep.parameters:
                    constants[key] = self.parse_parameter(dep.parameters[key])


        # Add the constants and attributes to the context.
        super().__init__(dict(
            interface_id=interface_id,
            feature_flag=feature_flag,
            data_flag=data_flag,
            attributes=attributes,
            constants=constants,
        ))

    # * method: parse_parameter
    def parse_parameter(self, parameter: str) -> str:
        '''
        Parse a parameter.

        :param parameter: The parameter to parse.
        :type parameter: str
        :return: The parsed parameter.
        :rtype: str
        '''

        # Parse the parameter.
        # Raise a ParameterParsingError if the parameter parsing fails.
        try:
            # If the parameter is an environment variable, get the value.
            # Raise an exception if the environment variable is not found.
            if parameter.startswith('$env.'):
                result = os.getenv(parameter[5:]) 
                if not result:
                    raise Exception('Environment variable not found.')
                return result
            return parameter
        except Exception as e:
            raise ParameterParsingError(parameter, e)

    # * method: get_dependency
    def get_dependency(self, attribute_id: str, **kwargs) -> Any:
        '''
        Get a dependency from the container.

        :param attribute_id: The attribute id of the dependency.
        :type attribute_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The attribute value.
        :rtype: Any
        '''

        # Create the injector.
        injector = self.create_injector(**kwargs)

        # Get attribute.
        return getattr(injector, attribute_id)

    # * method: create_injector
    def create_injector(self, **kwargs) -> Any:
        '''
        Add a container to the context.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The container injector object.
        :rtype: Any
        '''

        # Import dependencies.
        dependencies = {}
        for attribute_id in self.attributes:
            attribute = self.attributes[attribute_id]
            flag_map = dict(
                feature=self.feature_flag,
                data=self.data_flag,
            )
            dependencies[attribute_id] = self.import_dependency(attribute, flag_map[attribute.type])

        # Create container.
        return create_injector( 
            self.interface_id, 
            **self.constants, 
            **dependencies, 
            **kwargs)

    # * method: import_dependency
    def import_dependency(self, attribute: ContainerAttribute, flag: str) -> Any:
        '''
        Import a container attribute dependency from its configured Python module.

        :param attribute: The container attribute.
        :type attribute: ContainerAttribute
        :param flag: The flag for the dependency.
        :type flag: str
        :return: The dependency.
        :rtype: Any
        '''

        # Get the dependency.
        dependency = attribute.get_dependency(flag)

        # If there is still no dependency, raise an exception.
        if not dependency:
            raise DependencyNotFoundError(attribute.id, flag)

        # Import the dependency.
        return import_dependency(dependency.module_path, dependency.class_name)


# *** exceptions

# ** exception: create_injector_failure_error
class CreateInjectorFailureError(TiferetError):
    '''
    An exception for when the injector fails to create.
    '''

    # * init
    def __init__(self, name: str, exception: Exception):
        '''
        Initialize the exception.

        :param name: The name of the injector.
        :type name: str
        :param exception: The exception.
        :type exception: Exception
        '''

        # Set the message.
        super().__init__(
            'CREATE_INJECTOR_FAILURE',
            f'Error creating injector: {name} - {exception}')


# ** exception: dependency_import_failure_error
class DependencyImportFailureError(Exception):
    '''
    An exception for when a dependency fails to import.
    '''

    # * init
    def __init__(self, module_path: str, class_name: str, exception: Exception):
        '''
        Initialize the exception.

        :param module_path: The module path.
        :type module_path: str
        :param class_name: The class name.
        :type class_name: str
        :param exception: The exception.
        :type exception: Exception
        '''

        # Set the message.
        super().__init__(f'Error importing dependency: {module_path}.{class_name} - {exception}')


# ** exception: container_attribute_loading_error
class ContainerAttributeLoadingError(Exception):
    '''
    An exception for when a container attributes fail to load.
    '''

    # * init
    def __init__(self, exception: Exception):
        '''
        Initialize the exception.

        :param exception: The exception.
        :type exception: Exception
        '''

        # Set the message.
        super().__init__(f'Error loading container attributes: {exception}')


# ** exception: parameter_parsing_error
class ParameterParsingError(Exception):
    '''
    An exception thrown when the parameter parsing fails.
    '''

    def __init__(self, parameter: str, exception: Exception):
        self.parameter = parameter
        super().__init__(f'Error parsing parameter: {parameter} - {exception}')


# ** exception: dependency_not_found_error
class DependencyNotFoundError(TiferetError):
    '''
    An exception for when a dependency is not found.
    '''

    # * init
    def __init__(self, attribute_id: str, flag: str):
        '''
        Initialize the exception.

        :param error_code: The error code.
        :type error_code: str
        :param attribute_id: The attribute ID.
        :type attribute_id: str
        :param flag: The flag.
        :type flag: str
        '''

        # Set the message.
        super().__init__(
            'DEPENDENCY_NOT_FOUND',
            f'Dependency not found for container attribute with flag: {attribute_id} ({flag})')
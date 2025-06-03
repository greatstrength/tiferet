# *** imports

# ** core
import os

# ** app
from ..configs import *
from ..models.container import *
from ..contracts.container import *
from .error import raise_error


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
    
    # Raise an error if the injector creation fails.
    except Exception as e:
        raise_error(
            'CREATE_INJECTOR_FAILED',
            f'Error creating injector: {name} - {e}',
            name,
            str(e),
        )


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
    
    # Raise an error if the dependency import fails.
    except Exception as e:
        raise_error(
            'IMPORT_DEPENDENCY_FAILED',
            f'Error importing dependency: {module_path}.{class_name} - {e}',
            module_path,
            class_name,
            str(e),
        )


# *** contexts

# ** contexts: container_context
class ContainerContext(Model):
    '''
    A container context is a class that is used to create a container object.
    '''

    # * attribute: app_name
    app_name = StringType(
        required=True,
        metadata=dict(
            description='The name of the application instance.'
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
    def __init__(self, app_name: str, container_repo: ContainerRepository, feature_flag: str = 'core', data_flag: str = None):
        '''
        Initialize the container context.

        :param app_name: The name of the application instance.
        :type app_name: str
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

        # Raise an error if the container attributes fail to load.
        except Exception as e:
            raise_error(
                'CONTAINER_ATTRIBUTE_LOADING_FAILED',
                f'Error loading container attributes: {e}',
                str(e),
            )

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
            app_name=app_name,
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
        try:
            # If the parameter is an environment variable, get the value.
            # Raise an exception if the environment variable is not found.
            if parameter.startswith('$env.'):
                result = os.getenv(parameter[5:]) 
                if not result:
                    raise Exception('Environment variable not found.')
                return result
            return parameter
        
        # Raise an error if the parameter parsing fails.
        except Exception as e:
            raise_error(
                'PARAMETER_PARSING_FAILED',
                f'Error parsing parameter: {parameter} - {e}',
                parameter,
                str(e)
            )

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
            self.app_name,
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
            raise_error(
                'DEPENDENCY_NOT_FOUND',
                f'Dependency not found: {attribute.id} - {flag}',
                attribute.id,
                flag,
            )

        # Import the dependency.
        return import_dependency(dependency.module_path, dependency.class_name)

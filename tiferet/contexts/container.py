# *** imports

# ** core
from typing import Any

# ** app
from ..domain import *
from ..services import container_service
from ..repos.container import ContainerRepository


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
        required=True,
        default='core',
        metadata=dict(
            description='The feature flag.'
        ),
    )

    # * attribute: data_flag
    data_flag = StringType(
        required=True,
        metadata=dict(
            description='The data flag.'
        ),
    )

    # * method: init
    def __init__(self, interface_id: str, container_repo: ContainerRepository, feature_flag: str, data_flag: str):
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

        # Add the attributes as an empty dictionary.
        attributes = {}
        
        # Get and set attributes and constants.
        attrs, consts = container_repo.list_all()
        
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
                    consts[key] = dep.parameters[key]

        # Add the constants and attributes to the context.
        super().__init__(dict(
            interface_id=interface_id,
            feature_flag=feature_flag,
            data_flag=data_flag,
            attributes=attributes,
            constants=consts,
        ))

    # * method: get_dependency
    def get_dependency(self, attribute_id: str):
        '''
        Get a dependency from the container.

        :param attribute_id: The attribute id of the dependency.
        :type attribute_id: str
        :return: The attribute value.
        :rtype: Any
        '''

        # Create the injector.
        injector = self.create_injector()

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
        return container_service.create_injector( 
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

        # If there is no dependency and the attribute is a feature, import the default feature.
        if not dependency and attribute.type == 'feature':
            dependency = attribute.get_dependency('core')

        # Import the dependency.
        return container_service.import_dependency(dependency.module_path, dependency.class_name)
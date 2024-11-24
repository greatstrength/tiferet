# *** imports

# ** core
from typing import Any, Dict

# ** app
from ..configs import *
from ..domain import DataObject
from ..domain.container import ContainerAttribute, ContainerDependency


# *** data

# ** data: container_dependency_yaml_data
class ContainerDependencyYamlData(ContainerDependency, DataObject):
    '''
    A data representation of a container dependency object.
    '''

    class Options():
        '''
        The options for the container dependency data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('params'),
            'to_data': DataObject.deny('flag')
        }

    # * attribute: flag
    flag = StringType(
        metadata=dict(
            description='The flag is no longer required due to the YAML format.'
        ),
    )

    # * attribute: parameters
    parameters = DictType(
        StringType, 
        default={}, 
        serialized_name='params', 
        deserialize_from=['params'],
        metadata=dict(
            description='The parameters need to now account for new data names in the YAML format.'
        ),
    )

    # * method: map
    def map(self, **kwargs) -> ContainerDependency:
        '''
        Maps the container dependency data to a container dependency object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new container dependency object.
        '''

        # Map to the container dependency object.
        obj = super().map(ContainerDependency, **kwargs, validate=False)
    
        # Set the parameters in due to the deserializer.
        obj.parameters = self.parameters

        # Validate and return the object.
        obj.validate()
        return obj
    
    # * method: new
    @staticmethod
    def from_data(**kwargs) -> 'ContainerDependencyYamlData':
        '''
        Initializes a new ContainerDependencyData object from YAML data.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerDependencyData object.
        :rtype: ContainerDependencyYamlData
        '''

        # Create a new ContainerDependencyData object.
        return super(
            ContainerDependencyYamlData, 
            ContainerDependencyYamlData
        ).from_data(
            ContainerDependencyYamlData,
            **kwargs
        )
    
    # * method: from_model
    @staticmethod
    def from_model(model: ContainerDependency, **kwargs) -> 'ContainerDependencyYamlData':
        '''
        Initializes a new ContainerDependencyData object from a model object.

        :param model: The container dependency model object.
        :type model: ContainerDependency
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Create and return a new ContainerDependencyData object.
        return super(ContainerDependencyYamlData, ContainerDependencyYamlData).from_model(
            ContainerDependencyYamlData,
            model,
            **kwargs,
        )


# ** data: container_attribute_yaml_data
class ContainerAttributeYamlData(ContainerAttribute, DataObject):
    '''
    A data representation of a container attribute object.
    '''

    class Options():
        '''
        The options for the container attribute data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('id')
        }

    # * attribute: dependencies
    dependencies = DictType(
        ModelType(ContainerDependencyYamlData), 
        default=[], 
        serialized_name='deps', 
        deserialize_from=['deps', 'dependencies'],
        metadata=dict(
            description='The dependencies are now a key-value pair keyed by the flags.'
        ),
    )

    # * method: map
    def map(self, **kwargs) -> ContainerAttribute:
        '''
        Maps the container attribute data to a container attribute object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Map to the container attribute object with the dependencies.
        return super().map(ContainerAttribute, 
            dependencies=[dep.map(flag=flag) for flag, dep in self.dependencies.items()],
            **kwargs)

    # * method: new
    @staticmethod
    def from_data(**kwargs) -> 'ContainerAttributeYamlData':
        '''
        Initializes a new ContainerAttributeData object from YAML data.

        :param deps: The dependencies data.
        :type deps: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''        

        # Create a new ContainerAttributeData object.
        obj = super(
            ContainerAttributeYamlData, 
            ContainerAttributeYamlData
        ).from_data(
            ContainerAttributeYamlData,
            **kwargs, 
            validate=False
        )
    
        # Set the dependencies.
        for flag, dep in obj.dependencies.items():
            dep.flag = flag

        # Validate and return the object.
        obj.validate()
        return obj
    
    # * method: from_model
    @staticmethod
    def from_model(model: ContainerAttribute, **kwargs) -> 'ContainerAttributeYamlData':
        '''
        Initializes a new ContainerAttributeData object from a model object.

        :param model: The container attribute model object.
        :type model: ContainerAttribute
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Create the dependency data.
        dependencies = {dep.flag: dep.to_primitive() for dep in model.dependencies}
        
        # Create a new model object without the dependencies.
        data = model.to_primitive()
        data['dependencies'] = dependencies

        # Create a new ContainerAttributeData object.
        obj = ContainerAttributeYamlData(
            dict(
                **data,
                **kwargs
            ), 
            strict=False
        )

        # Validate and return the object.
        obj.validate()
        return obj
    
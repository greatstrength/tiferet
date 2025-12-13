"""Tiferet Container Data Objects"""

# *** imports

# ** app
from ..models import (
    FlaggedDependency,
    ContainerAttribute,
    StringType,
    DictType,
    ModelType,
)
from ..contracts import (
    FlaggedDependencyContract,
    ContainerAttributeContract
)
from .settings import DataObject

# *** data

# ** data: flagged_dependency_config_data
class FlaggedDependencyConfigData(FlaggedDependency, DataObject):
    '''
    Represents the YAML data for a flagged dependency.
    '''

    class Options:
        '''
        Options for the data object.
        '''
        
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('params'),
            'to_data.yaml': DataObject.deny('flag'),
            'to_data.json': DataObject.deny('flag')
        }

    # * attribute: flag
    flag = StringType(
        metadata=dict(
            description='The flag for the dependency, not required in YAML format.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        serialized_name='params',
        deserialize_from=['params'],
        metadata=dict(
            description='The parameters for the dependency, supporting YAML data names.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> FlaggedDependencyContract:
        '''
        Maps the YAML data to a flagged dependency object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new flagged dependency object.
        :rtype: FlaggedDependencyContract
        '''
        
        # Map to the flagged dependency object.
        obj = super().map(FlaggedDependency, **kwargs, validate=False)

        # Set the parameters in due to the deserializer.
        obj.parameters = self.parameters
        
        # Validate and return the object.
        obj.validate()
        return obj

    # * method: from_data
    @staticmethod
    def from_data(**kwargs) -> 'FlaggedDependencyConfigData':
        '''
        Initializes a new FlaggedDependencyYamlData object from YAML data.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FlaggedDependencyYamlData object.
        :rtype: FlaggedDependencyYamlData
        '''
        
        # Create a new FlaggedDependencyYamlData object.
        return super(
            FlaggedDependencyConfigData,
            FlaggedDependencyConfigData
        ).from_data(
            FlaggedDependencyConfigData,
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(model: FlaggedDependency, **kwargs) -> 'FlaggedDependencyConfigData':
        '''
        Initializes a new FlaggedDependencyYamlData object from a model object.
        
        :param model: The flagged dependency model object.
        :type model: FlaggedDependency
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FlaggedDependencyYamlData object.
        :rtype: FlaggedDependencyYamlData
        '''
        
        # Create and return a new FlaggedDependencyYamlData object.
        return super(
            FlaggedDependencyConfigData,
            FlaggedDependencyConfigData
        ).from_model(
            FlaggedDependencyConfigData,
            model,
            **kwargs
        )

# ** data: container_attribute_config_data
class ContainerAttributeConfigData(ContainerAttribute, DataObject):
    '''
    Represents the YAML data for a container attribute.
    '''

    class Options:
        '''
        Options for the data object.
        '''
        
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('params'),
            'to_data.yaml': DataObject.deny('id'),
            'to_data.json': DataObject.deny('id')
        }

    # * attribute: dependencies
    dependencies = DictType(
        ModelType(FlaggedDependencyConfigData),
        default={},
        serialized_name='deps',
        deserialize_from=['deps', 'dependencies'],
        metadata=dict(
            description='The dependencies as key-value pairs, keyed by flags.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        serialized_name='params',
        deserialize_from=['params'],
        metadata=dict(
            description='The default parameters for the container attribute.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> ContainerAttributeContract:
        '''
        Maps the YAML data to a container attribute object.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new container attribute object.
        :rtype: ContainerAttributeContract
        '''
        
        # Map to the container attribute object with dependencies.
        return super().map(
            ContainerAttribute,
            dependencies=[dep.map(flag=flag) for flag, dep in self.dependencies.items()],
            parameters=self.parameters,
            **kwargs
        )

    # * method: from_data
    @staticmethod
    def from_data(**kwargs) -> 'ContainerAttributeConfigData':
        '''
        Initializes a new ContainerAttributeYamlData object from YAML data.
        
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerAttributeYamlData object.
        :rtype: ContainerAttributeYamlData
        '''
        
        # Create a new ContainerAttributeYamlData object.
        data_object = super(
            ContainerAttributeConfigData,
            ContainerAttributeConfigData
        ).from_data(
            ContainerAttributeConfigData,
            **kwargs,
            validate=False
        )

        # Set the dependencies.
        for flag, dep in data_object.dependencies.items():
            dep.flag = flag
        
        # Validate and return the object.

        data_object.validate()
        return data_object

    # * method: from_model
    @staticmethod
    def from_model(model_object: ContainerAttribute, **kwargs) -> 'ContainerAttributeConfigData':
        '''
        Initializes a new ContainerAttributeYamlData object from a model object.
        
        :param model_object: The container attribute model object.
        :type model_object: ContainerAttribute
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerAttributeYamlData object.
        :rtype: ContainerAttributeYamlData
        '''
                
        # Create the primitive of the model object.
        data = model_object.to_primitive()
        
        # Convert dependencies to YAML data format.
        data['dependencies'] = {dep.flag: dep.to_primitive() for dep in model_object.dependencies}
        
        # Create a new ContainerAttributeYamlData object.
        data_object = ContainerAttributeConfigData(
            dict(
                **data,
                **kwargs
            ),
            strict=False
        )
        
        # Validate and return the object.
        data_object.validate()
        return data_object
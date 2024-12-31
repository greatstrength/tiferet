# *** imports

# ** app
from ..configs import *
from ..models.container import *
from .core import *


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
            'to_model': DataObject.deny('parameters'),
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
        return super().map(
            ContainerDependency,
            parameters=self.parameters,
            **kwargs
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
        return super().map(
            ContainerAttribute,
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

        # Pop the dependencies from the keyword arguments.
        dependencies = kwargs.pop('deps', {})

        # Create the dependencies.
        dependencies = {flag: DataObject.from_data(
            ContainerDependencyYamlData,
            flag=flag, **dep
        ) for flag, dep in dependencies.items()}

        # Create a new ContainerAttributeData object.
        return DataObject.from_data(
            ContainerAttributeYamlData,
            dependencies=dependencies,
            **kwargs
        )

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
        dependencies = {dep.flag: dep.to_primitive()
                        for dep in model.dependencies}

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

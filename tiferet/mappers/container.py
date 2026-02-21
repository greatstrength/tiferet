"""Tiferet Container Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..domain import (
    FlaggedDependency,
    ContainerAttribute,
    StringType,
    DictType,
    ModelType,
)
from .settings import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: flagged_dependency_aggregate
class FlaggedDependencyAggregate(FlaggedDependency, Aggregate):
    '''
    An aggregate representation of a flagged dependency.
    '''

    # * method: new
    @staticmethod
    def new(
        flagged_dependency_data: Dict[str, Any],
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'FlaggedDependencyAggregate':
        '''
        Initializes a new flagged dependency aggregate.

        :param flagged_dependency_data: The data to create the flagged dependency aggregate from.
        :type flagged_dependency_data: dict
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new flagged dependency aggregate.
        :rtype: FlaggedDependencyAggregate
        '''

        # Create a new flagged dependency aggregate from the provided data.
        return Aggregate.new(
            FlaggedDependencyAggregate,
            validate=validate,
            strict=strict,
            **flagged_dependency_data,
            **kwargs
        )

    # * method: set_parameters
    def set_parameters(self, parameters: Dict[str, Any] | None = None) -> None:
        '''
        Update the parameters dictionary for this flagged dependency.

        :param parameters: New parameters, or None to clear all.
                           Keys with None values are removed.
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # If parameters is None, clear all.
        if parameters is None:
            self.parameters = {}
        else:
            # Merge existing parameters with new ones (new values win).
            merged = dict(self.parameters or {})
            merged.update(parameters)

            # Filter out keys where the value is None.
            self.parameters = {
                k: v for k, v in merged.items() if v is not None
            }


# ** mapper: flagged_dependency_yaml_object
class FlaggedDependencyYamlObject(FlaggedDependency, TransferObject):
    '''
    A YAML data representation of a flagged dependency object.
    '''

    class Options:
        '''
        The options for the flagged dependency data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny(),
            'to_data.yaml': TransferObject.deny('flag'),
            'to_data.json': TransferObject.deny('flag')
        }

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        serialized_name='params',
        deserialize_from=['params', 'parameters'],
        metadata=dict(
            description='The parameters for the dependency.'
        )
    )

    # * method: map
    def map(self, flag: str = None, **kwargs) -> FlaggedDependency:
        '''
        Maps the flagged dependency data to a flagged dependency object.

        :param flag: The flag for the dependency.
        :type flag: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new flagged dependency object.
        :rtype: FlaggedDependency
        '''

        # Map to the flagged dependency object.
        # Note: parent map() already calls to_primitive, so we only pass overrides.
        return super().map(
            FlaggedDependency,
            flag=flag or self.flag,
            parameters=self.parameters,
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(flagged_dependency: FlaggedDependency, **kwargs) -> 'FlaggedDependencyYamlObject':
        '''
        Creates a FlaggedDependencyYamlObject from a FlaggedDependency model.

        :param flagged_dependency: The flagged dependency model.
        :type flagged_dependency: FlaggedDependency
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FlaggedDependencyYamlObject.
        :rtype: FlaggedDependencyYamlObject
        '''

        # Create a new FlaggedDependencyYamlObject from the model.
        return TransferObject.from_model(
            FlaggedDependencyYamlObject,
            flagged_dependency,
            **kwargs,
        )

# ** mapper: container_attribute_aggregate
class ContainerAttributeAggregate(ContainerAttribute, Aggregate):
    '''
    An aggregate representation of a container attribute.
    '''

    # * method: new
    @staticmethod
    def new(
        container_attribute_data: Dict[str, Any],
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'ContainerAttributeAggregate':
        '''
        Initializes a new container attribute aggregate.

        :param container_attribute_data: The data to create the container attribute aggregate from.
        :type container_attribute_data: dict
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new container attribute aggregate.
        :rtype: ContainerAttributeAggregate
        '''

        # Create a new container attribute aggregate from the provided data.
        return Aggregate.new(
            ContainerAttributeAggregate,
            validate=validate,
            strict=strict,
            **container_attribute_data,
            **kwargs
        )

    # * method: set_default_type
    def set_default_type(
        self,
        module_path: str | None = None,
        class_name: str | None = None,
        parameters: Dict[str, Any] | None = None,
    ) -> None:
        '''
        Update the default type and parameters for this container attribute.

        :param module_path: New module path (or None to clear).
        :type module_path: str | None
        :param class_name: New class name (or None to clear).
        :type class_name: str | None
        :param parameters: New parameters dict (or None to clear all).
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # If both type fields are None, clear default type.
        if module_path is None and class_name is None:
            self.module_path = None
            self.class_name = None
            self.parameters = {}

        # Otherwise, set them to whatever is provided.
        else:
            self.module_path = module_path
            self.class_name = class_name

        # Update parameters: if parameters is None, clear all; otherwise replace.
        if parameters is None:
            self.parameters = {}
        else:
            self.parameters = {k: v for k, v in parameters.items() if v is not None}

    # * method: set_dependency
    def set_dependency(
        self,
        flag: str,
        module_path: str | None = None,
        class_name: str | None = None,
        parameters: Dict[str, Any] | None = None,
    ) -> None:
        '''
        Sets or updates a flagged container dependency.

        :param flag: The flag that identifies the dependency.
        :type flag: str
        :param module_path: The module path for the dependency.
        :type module_path: str | None
        :param class_name: The class name for the dependency.
        :type class_name: str | None
        :param parameters: The parameters for the dependency (empty dict by default).
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Normalize parameters to a dict.
        parameters = parameters or {}

        # Replace the value of the dependency if a dependency with the same flag exists.
        for dep in self.dependencies:
            if dep.flag == flag:
                dep.module_path = module_path
                dep.class_name = class_name
                dep.set_parameters(parameters)
                return

        # Create a new dependency if none exists with this flag.
        from ..domain import DomainObject
        dependency = DomainObject.new(
            FlaggedDependency,
            module_path=module_path,
            class_name=class_name,
            flag=flag,
            parameters=parameters,
        )

        self.dependencies.append(dependency)

    # * method: remove_dependency
    def remove_dependency(self, flag: str) -> None:
        '''
        Remove a flagged container dependency by its flag.

        :param flag: The flag identifying the dependency to remove.
        :type flag: str
        :return: None
        :rtype: None
        '''

        # Filter out any dependency whose flag matches the provided flag.
        self.dependencies = [
            dependency
            for dependency in self.dependencies
            if dependency.flag != flag
        ]


# ** mapper: container_attribute_yaml_object
class ContainerAttributeYamlObject(ContainerAttribute, TransferObject):
    '''
    A YAML data representation of a container attribute object.
    '''

    class Options:
        '''
        The options for the container attribute data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('dependencies', 'parameters'),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id')
        }

    # * attribute: dependencies
    dependencies = DictType(
        ModelType(FlaggedDependencyYamlObject),
        default={},
        serialized_name='deps',
        deserialize_from=['deps', 'dependencies', 'flags'],
        metadata=dict(
            description='The dependencies as key-value pairs, keyed by flags.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        serialized_name='params',
        deserialize_from=['params', 'parameters'],
        metadata=dict(
            description='The default parameters for the container attribute.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> ContainerAttributeAggregate:
        '''
        Maps the container attribute data to a container attribute aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new container attribute aggregate.
        :rtype: ContainerAttributeAggregate
        '''

        # Map the container attribute data.
        return super().map(
            ContainerAttributeAggregate,
            dependencies=[dep.map(flag=flag) for flag, dep in self.dependencies.items()],
            parameters=self.parameters,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(container_attribute: ContainerAttribute, **kwargs) -> 'ContainerAttributeYamlObject':
        '''
        Creates a ContainerAttributeYamlObject from a ContainerAttribute model.

        :param container_attribute: The container attribute model.
        :type container_attribute: ContainerAttribute
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerAttributeYamlObject.
        :rtype: ContainerAttributeYamlObject
        '''

        # Create a new ContainerAttributeYamlObject from the model, converting
        # the dependencies list into a dictionary keyed by flag.
        return TransferObject.from_model(
            ContainerAttributeYamlObject,
            container_attribute,
            dependencies={
                dep.flag: TransferObject.from_model(FlaggedDependencyYamlObject, dep)
                for dep in container_attribute.dependencies
            },
            **kwargs,
        )

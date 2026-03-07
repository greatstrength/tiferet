"""Tiferet DI Mappers"""

# *** imports

# ** core
from typing import Dict, Any

# ** app
from ..domain import (
    FlaggedDependency,
    ServiceConfiguration,
    DomainObject,
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
            'to_data.json': TransferObject.deny('flag'),
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

# ** mapper: service_configuration_aggregate
class ServiceConfigurationAggregate(ServiceConfiguration, Aggregate):
    '''
    An aggregate representation of a service configuration.
    '''

    # * method: new
    @staticmethod
    def new(
        service_configuration_data: Dict[str, Any],
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'ServiceConfigurationAggregate':
        '''
        Initializes a new service configuration aggregate.

        :param service_configuration_data: The data to create the service configuration aggregate from.
        :type service_configuration_data: dict
        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode for the aggregate object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new service configuration aggregate.
        :rtype: ServiceConfigurationAggregate
        '''

        # Create a new service configuration aggregate from the provided data.
        return Aggregate.new(
            ServiceConfigurationAggregate,
            validate=validate,
            strict=strict,
            **service_configuration_data,
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
        Update the default type and parameters for this service configuration.

        :param module_path: New module path (or None to clear).
        :type module_path: str | None
        :param class_name: New class name (or None to clear).
        :type class_name: str | None
        :param parameters: New parameters dict (or None to clear all).
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # If both type fields are None, clear default type entirely.
        if module_path is None and class_name is None:
            self.module_path = None
            self.class_name = None
            self.parameters = {}

        # Otherwise, set them to whatever is provided.
        else:
            self.module_path = module_path
            self.class_name = class_name

        # Update parameters: if parameters is None, clear all; otherwise replace with filtered dict.
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
        Sets or updates a flagged dependency.

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

                # Inline set_parameters semantics — works on any FlaggedDependency instance.
                merged = dict(dep.parameters or {})
                merged.update(parameters)
                dep.parameters = {k: v for k, v in merged.items() if v is not None}
                return

        # Create a new dependency if none exists with this flag.
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
        Remove a flagged dependency by its flag.

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


# ** mapper: service_configuration_yaml_object
class ServiceConfigurationYamlObject(ServiceConfiguration, TransferObject):
    '''
    A YAML data representation of a service configuration object.
    '''

    class Options:
        '''
        The options for the service configuration data.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('dependencies', 'parameters'),
            'to_data.yaml': TransferObject.deny('id'),
            'to_data.json': TransferObject.deny('id'),
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
            description='The default parameters for the service configuration.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> ServiceConfigurationAggregate:
        '''
        Maps the service configuration data to a service configuration aggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new service configuration aggregate.
        :rtype: ServiceConfigurationAggregate
        '''

        # Map the service configuration data to a service configuration aggregate.
        return super().map(
            ServiceConfigurationAggregate,
            dependencies=[dep.map(flag=flag) for flag, dep in self.dependencies.items()],
            parameters=self.parameters,
            **self.to_primitive('to_model'),
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(service_configuration: ServiceConfiguration, **kwargs) -> 'ServiceConfigurationYamlObject':
        '''
        Creates a ServiceConfigurationYamlObject from a ServiceConfiguration model.

        :param service_configuration: The service configuration model.
        :type service_configuration: ServiceConfiguration
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ServiceConfigurationYamlObject.
        :rtype: ServiceConfigurationYamlObject
        '''

        # Create a new ServiceConfigurationYamlObject from the model, converting
        # the dependencies list into a dictionary keyed by flag.
        return TransferObject.from_model(
            ServiceConfigurationYamlObject,
            service_configuration,
            dependencies={
                dep.flag: TransferObject.from_model(FlaggedDependencyYamlObject, dep)
                for dep in service_configuration.dependencies
            },
            **kwargs,
        )

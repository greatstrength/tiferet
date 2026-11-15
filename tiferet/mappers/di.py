"""Tiferet DI Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from pydantic import AliasChoices, Field

# ** app
from ..domain import (
    INVALID_MODEL_VALUE_ID,
    FlaggedDependency,
    ModelError,
    ServiceRegistration,
)
from .core import Aggregate, TransferObject

# *** mappers

# ** mapper: flagged_dependency_aggregate
class FlaggedDependencyAggregate(FlaggedDependency, Aggregate):
    '''
    An aggregate representation of a flagged dependency.
    '''

    # * method: set_parameters
    def set_parameters(self, parameters: Dict[str, Any] | None = None) -> None:
        '''
        Overlay new parameters onto the existing parameters for this flagged dependency.

        A new value wins, a None value removes that key, an empty overlay
        preserves existing entries, and a None argument leaves the mapping
        unchanged.

        :param parameters: The parameter overlay, or None for a no-op.
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Leave the parameters unchanged when None is provided.
        if parameters is None:
            return

        # Merge existing parameters with new ones (new values win), then drop
        # keys whose value is None. Reassign so validate_assignment fires.
        merged = dict(self.parameters or {})
        merged.update(parameters)
        self.parameters = {k: v for k, v in merged.items() if v is not None}

# ** mapper: flagged_dependency_config_object
class FlaggedDependencyConfigObject(FlaggedDependency, TransferObject):
    '''
    A configuration data representation of a flagged dependency object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True, 'exclude': {'flag'}},
    }

    # * attribute: flag
    flag: str | None = Field(
        default=None,
        description=(
            'The flag for the dependency. Optional in YAML data because the '
            'flag is typically the dict key in the parent ServiceRegistration.'
        ),
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='params',
        validation_alias=AliasChoices('params', 'parameters'),
        description='The parameters for the dependency.',
    )

    # * method: map
    def map(self, flag: str | None = None, **overrides) -> FlaggedDependency:
        '''
        Maps the flagged dependency data to a runtime FlaggedDependency.

        :param flag: Optional flag override (used when keyed in parent dict).
        :type flag: str | None
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FlaggedDependency instance.
        :rtype: FlaggedDependency
        '''

        # Pass an explicit flag override only when one was supplied so we do
        # not accidentally clear the YAML's own flag value.
        if flag is not None:
            overrides.setdefault('flag', flag)

        # Delegate to the base mapper, targeting FlaggedDependency.
        return super().map(FlaggedDependency, **overrides)

    # * method: from_model
    @classmethod
    def from_model(cls, flagged_dependency: FlaggedDependency, **overrides) -> 'FlaggedDependencyConfigObject':
        '''
        Creates a FlaggedDependencyConfigObject from a FlaggedDependency model.

        :param flagged_dependency: The flagged dependency model to copy from.
        :type flagged_dependency: FlaggedDependency
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new FlaggedDependencyConfigObject instance.
        :rtype: FlaggedDependencyConfigObject
        '''

        # Delegate to the base mapper.
        return super().from_model(flagged_dependency, **overrides)

# ** mapper: service_registration_aggregate
class ServiceRegistrationAggregate(ServiceRegistration, Aggregate):
    '''
    An aggregate representation of a service registration.
    '''

    # * method: set_default_type
    def set_default_type(
        self,
        module_path: str | None = None,
        class_name: str | None = None,
        parameters: Dict[str, Any] | None = None,
    ) -> None:
        '''
        Update the default type and overlay the parameters for this service
        registration.

        The type fields are assigned as supplied. The parameters are overlaid
        onto the existing mapping: a new value wins, a ``None`` value removes
        that key, and a ``None`` argument leaves the parameters unchanged.

        :param module_path: New module path.
        :type module_path: str | None
        :param class_name: New class name.
        :type class_name: str | None
        :param parameters: Optional parameter overlay.
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Set the type fields to whatever is provided.
        self.module_path = module_path
        self.class_name = class_name

        # Leave the parameters unchanged when no overlay is supplied.
        if parameters is None:
            return

        # Overlay the new parameters onto a copy of the existing ones, then
        # remove entries whose value is None.
        merged = dict(self.parameters or {})
        merged.update(parameters)
        self.parameters = {k: v for k, v in merged.items() if v is not None}

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

        The first dependency with a matching flag is updated in place and keeps
        its list position: its type fields are assigned, even when None, and
        its parameters are overlaid so a new value wins, a None value removes
        that key, and a None or empty overlay preserves existing entries. For
        an absent flag, a new dependency is appended whose parameters omit None
        values; a None argument creates an empty parameters mapping.

        :param flag: The flag that identifies the dependency.
        :type flag: str
        :param module_path: The module path for the dependency.
        :type module_path: str | None
        :param class_name: The class name for the dependency.
        :type class_name: str | None
        :param parameters: The parameter overlay for the dependency, or None for an empty overlay.
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Normalize absent parameters to an empty overlay.
        parameters = parameters or {}

        # Update the first dependency with the same flag in place.
        for dep in self.dependencies:
            if dep.flag == flag:
                dep.module_path = module_path
                dep.class_name = class_name
                merged = dict(dep.parameters or {})
                merged.update(parameters)
                dep.parameters = {k: v for k, v in merged.items() if v is not None}
                return

        # Otherwise create a new dependency omitting None-valued parameters and append it.
        dependency = FlaggedDependency(
            module_path=module_path,
            class_name=class_name,
            flag=flag,
            parameters={k: v for k, v in parameters.items() if v is not None},
        )
        self.dependencies = list(self.dependencies) + [dependency]

    # * method: remove_dependency
    def remove_dependency(self, flag: str) -> None:
        '''
        Remove a flagged dependency by its flag.

        :param flag: The flag identifying the dependency to remove.
        :type flag: str
        :return: None
        :rtype: None
        '''

        # Reassign so validate_assignment=True triggers field validation.
        self.dependencies = [
            dependency
            for dependency in self.dependencies
            if dependency.flag != flag
        ]

# ** mapper: service_registration_config_object
class ServiceRegistrationConfigObject(ServiceRegistration, TransferObject):
    '''
    A configuration data representation of a service registration object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'dependencies', 'parameters'}},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: dependencies
    dependencies: Dict[str, FlaggedDependencyConfigObject] = Field(
        default_factory=dict,
        serialization_alias='deps',
        validation_alias=AliasChoices('deps', 'dependencies', 'flags'),
        description='The dependencies as key-value pairs, keyed by flags.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='params',
        validation_alias=AliasChoices('params', 'parameters'),
        description='The default parameters for the service registration.',
    )

    # * method: map
    def map(self, **overrides) -> ServiceRegistrationAggregate:
        '''
        Maps the service registration data to a service registration aggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new ServiceRegistrationAggregate instance.
        :rtype: ServiceRegistrationAggregate
        '''

        # Convert dict-keyed YAML deps into a flag-tagged list of FlaggedDependency.
        return super().map(
            ServiceRegistrationAggregate,
            dependencies=[dep.map(flag=flag) for flag, dep in self.dependencies.items()],
            parameters=self.parameters,
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, service_registration: ServiceRegistration, **overrides) -> 'ServiceRegistrationConfigObject':
        '''
        Creates a ServiceRegistrationConfigObject from a ServiceRegistration model.

        The dependencies list is keyed by flag in list order. A repeated flag
        is rejected before conversion, and the model is not mutated.

        :param service_registration: The service registration model to copy from.
        :type service_registration: ServiceRegistration
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: A new ServiceRegistrationConfigObject instance.
        :rtype: ServiceRegistrationConfigObject
        '''

        # Reject the first repeated flag before keyed conversion.
        seen = set()
        for dep in service_registration.dependencies:
            if dep.flag in seen:
                ModelError.raise_error(
                    INVALID_MODEL_VALUE_ID,
                    message=f'Flagged dependency {dep.flag!r} is repeated in service registration {service_registration.id!r}.',
                    model=service_registration,
                    attribute='dependencies',
                    flag=dep.flag,
                )
            seen.add(dep.flag)

        # Convert the dependencies list into a dictionary keyed by flag.
        return super().from_model(
            service_registration,
            dependencies={
                dep.flag: FlaggedDependencyConfigObject.from_model(dep)
                for dep in service_registration.dependencies
            },
            **overrides,
        )

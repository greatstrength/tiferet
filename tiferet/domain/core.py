"""Tiferet Core Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Dict

# ** infra
from pydantic import BaseModel, ConfigDict, Field

# *** classes

# ** class: domain_object
class DomainObject(BaseModel):
    '''
    The base domain model object for Tiferet, backed by Pydantic v2.

    Subclasses declare fields with idiomatic ``name: T = Field(...)`` annotations.
    Domain objects are intended to be read-only at the base level; mutation logic
    lives on Aggregate subclasses in :mod:`tiferet.mappers`.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
    )

# *** models

# ** model: service_dependency
class ServiceDependency(DomainObject):
    '''
    A core service dependency that defines the module, class, and parameters
    for a service implementation.
    '''

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path for the service dependency.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name for the service dependency.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='The parameters for the service dependency.',
    )

    # * method: get_service_type
    def get_service_type(self) -> type:
        '''
        Import and return the service class identified by this dependency.

        :return: The service class type.
        :rtype: type
        '''

        # Import the module and return the named class.
        return getattr(import_module(self.module_path), self.class_name)

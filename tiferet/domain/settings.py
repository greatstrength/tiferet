"""Tiferet Domain Settings"""

# *** imports

# ** infra
from pydantic import BaseModel, ConfigDict

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

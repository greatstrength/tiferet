"""Tiferet Test Module Domain Models"""

# *** imports

# ** infra
from pydantic import ConfigDict, Field

# ** app
from .core import DomainObject

# *** models

# ** model: test_module_address
class TestModuleAddress(DomainObject):
    '''
    The address of one tiferet_tests YAML document.

    It names the stem and the resolved file. It does not read the file,
    edit the document, or know what a phase contains.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        frozen=True,
    )

    # * attribute: rel
    rel: str = Field(
        ...,
        description='The relative test-module stem, without an extension.',
    )

    # * attribute: base_dir
    base_dir: str = Field(
        ...,
        description='The directory whose tiferet_tests child holds the module.',
    )

    # * attribute: path
    path: str = Field(
        ...,
        description='The resolved tiferet_tests YAML path.',
    )

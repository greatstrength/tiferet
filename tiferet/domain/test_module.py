"""Tiferet Test Module Domain Models"""

# *** imports

# ** core
from typing import Any

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

# ** model: test_module_document
class TestModuleDocument(DomainObject):
    '''
    The YAML document at one test-module address.

    It is the noun the writer reads and writes. It is not a test, not a
    tester, and not only the address. The address is a field. The text is
    the loaded revision. The body is the composed root, not a fixture dict.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        frozen=True,
    )

    # * attribute: address
    address: TestModuleAddress = Field(
        ...,
        description='The read-only address of this document.',
    )

    # * attribute: text
    text: str | None = Field(
        None,
        description='The loaded YAML revision, or None when the file is absent.',
    )

    # * attribute: body
    body: Any = Field(
        None,
        description='The composed root, unset when the file is absent.',
    )

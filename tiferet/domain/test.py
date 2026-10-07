"""Tiferet Test Domain Models"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** infra
from pydantic import Field

# ** app
from .feature import Feature

# *** models

# ** model: test
class Test(Feature):
    '''
    A test is a feature in purpose and a test in name — the same workflow
    noun, spoken as the three phases ``conditions``, ``execute``, and
    ``asserts``, so a YAML test module can name what a feature step list
    cannot say on its own.

    The YAML phase key is ``assert``. Mapping that key onto ``asserts``
    belongs on the transfer object, which this model does not carry.
    '''

    # * attribute: conditions
    conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description='The conditions phase. What must be true before the test runs.',
    )

    # * attribute: execute
    execute: List[Dict[str, Any]] = Field(
        default_factory=list,
        description='The execute phase. The ordered steps the test performs.',
    )

    # * attribute: asserts
    asserts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description='The asserts phase. The ordered checks the test evaluates.',
    )

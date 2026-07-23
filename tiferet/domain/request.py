"""Tiferet Request Domain Models"""

# *** imports

# ** core
from typing import Any, Dict
from uuid import uuid4

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject

# *** models

# ** model: request
class Request(DomainObject):
    '''
    A request value object carrying the session, feature, headers, and data for
    a single feature execution. Runtime output (``result``) is intentionally not
    modeled here; it is owned by the operational request context.
    '''

    # * attribute: session_id
    session_id: str = Field(
        ...,
        description='The unique session identifier for the request.',
    )

    # * attribute: feature_id
    feature_id: str | None = Field(
        default=None,
        description='The identifier of the feature being executed.',
    )

    # * attribute: headers
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description='The request headers.',
    )

    # * attribute: data
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description='The request data payload.',
    )

    # * method: derive_session_id (validator)
    @model_validator(mode='before')
    @classmethod
    def derive_session_id(cls, data: Any) -> Any:
        '''
        Generate a ``uuid4`` ``session_id`` when one is not supplied, mirroring
        the derivation validators on other domain objects.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The (possibly augmented) input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs; pass other shapes through unchanged.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Generate a session id when missing or None.
        if not data.get('session_id'):
            data['session_id'] = str(uuid4())

        # Return the (possibly augmented) input data.
        return data

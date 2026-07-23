"""Tiferet Error Domain Models"""

# *** imports

# ** core
from typing import Any, List

# ** infra
from pydantic import Field, model_validator

# ** app
from .core import DomainObject

# *** models

# ** model: error_message
class ErrorMessage(DomainObject):
    '''
    An error message object.
    '''

    # * attribute: lang
    lang: str = Field(..., description='The language of the error message text.')

    # * attribute: text
    text: str = Field(..., description='The error message text.')

    # * method: format
    def format(self, **kwargs) -> str:
        '''
        Formats the error message text.

        :param kwargs: The format keyword arguments for the error message text.
        :type kwargs: dict
        :return: The formatted error message text.
        :rtype: str
        '''

        # If there are no arguments, return the error message text.
        if not kwargs:
            return self.text

        # Format the error message text and return it.
        return self.text.format(**kwargs)

# ** model: error
class Error(DomainObject):
    '''
    An error object.
    '''

    # * attribute: id
    id: str = Field(..., description='The unique identifier of the error.')

    # * attribute: name
    name: str = Field(..., description='The name of the error.')

    # * attribute: description
    description: str | None = Field(default=None, description='The description of the error.')

    # * attribute: error_code
    error_code: str | None = Field(default=None, description='The unique code of the error.')

    # * attribute: message
    message: List[ErrorMessage] = Field(default_factory=list, description='The error message translations for the error.')

    # * method: _derive_error_code (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_error_code(cls, data: Any) -> Any:
        '''
        Derive ``error_code`` from ``id`` when not explicitly provided.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The (possibly augmented) input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs; pass other shapes through unchanged.
        if isinstance(data, dict) and not data.get('error_code') and data.get('id'):
            data = dict(data)
            data['error_code'] = str(data['id']).upper().replace(' ', '_')

        # Return the (possibly augmented) input data.
        return data

    # * method: format_message
    def format_message(self, lang: str = 'en_US', **kwargs) -> str:
        '''
        Formats the error message text for the specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param kwargs: Additional format arguments for the error message text.
        :type kwargs: dict
        :return: The formatted error message text.
        :rtype: str
        '''

        # Iterate through the error messages.
        for msg in self.message:

            # Skip if the language does not match.
            if msg.lang != lang:
                continue

            # Format the error message text.
            return msg.format(**kwargs)

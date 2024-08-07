from typing import List, Dict, Any

from ..objects.error import Error
from ..objects.error import ErrorMessage

def create_error(message: List[str], **kwargs) -> Error:

    # Create a list of error messages.
    error_messages = []

    # Convert incoming message list to dictionary by splitting on '='.
    for text in message:
        lang, text = text.split('=')
        error_messages.append(ErrorMessage(dict(
            lang=lang,
            text=text
        )))
        

    # Create the error.
    _error = Error.new(
        message=error_messages,
        **kwargs
    )

    # Return the error.
    return _error

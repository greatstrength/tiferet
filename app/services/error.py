from typing import List, Dict, Any

from ..objects.error import Error

def create_error(name: str, message: List[str], **kwargs) -> Error:

    # Upper snake case the name.
    name = name.upper()

    # Convert incoming message list to dictionary by splitting on '='.
    message = {item.split('=')[0]: item.split('=')[1] for item in message}

    # Create the error.
    _error = Error(dict(
        name=name,
        message=message,
        **kwargs
    ))

    # Validate the error.
    _error.validate()

    # Return the error.
    return _error

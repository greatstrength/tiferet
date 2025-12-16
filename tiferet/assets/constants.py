"""Tiferet Connstants (Assets)"""

# *** imports

# *** constants

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: default_errors
DEFAULT_ERRORS = {

    # * error: ERROR_NOT_FOUND
    ERROR_NOT_FOUND_ID: {
        'id': ERROR_NOT_FOUND_ID,
        'name': 'Error Not Found',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Error not found: {id}.'
            }
        ]
    }
}
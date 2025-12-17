"""Tiferet Connstants (Assets)"""

# *** imports

# *** constants

# ** constant: error_not_found_id
ERROR_NOT_FOUND_ID = 'ERROR_NOT_FOUND'

# ** constant: parameter_parsing_failed_id
PARAMETER_PARSING_FAILED_ID = 'PARAMETER_PARSING_FAILED'

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
    },

    # * error: PARAMETER_PARSING_FAILED
    PARAMETER_PARSING_FAILED_ID: {
        'id': PARAMETER_PARSING_FAILED_ID,
        'name': 'Parameter Parsing Failed',
        'message': [
            {
                'lang': 'en_US',
                'text': 'Failed to parse parameter: {parameter}. Error: {exception}.'
            }
        ]
    }
}
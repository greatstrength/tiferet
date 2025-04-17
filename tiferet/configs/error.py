# *** constants

# ** constant: errors
ERRORS = dict(

    # */ ERROR_LOADING_FAILED
    ERROR_LOADING_FAILED = dict(
        id='ERROR_LOADING_FAILED',
        name='Error loading failed',
        error_code='ERROR_LOADING_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Failed to load errors: {}.'
            )
        ]
    ),

    # */ ERROR_NOT_FOUND
    ERROR_NOT_FOUND = dict(
        id='ERROR_NOT_FOUND',
        name='Error not found',
        error_code='ERROR_NOT_FOUND',
        message=[
            dict(
                lang='en_US',
                text='Error not found: {}.'
            )
        ]
    ),

    # */ CREATE_INJECTOR_FAILED
    CREATE_INJECTOR_FAILED = dict(
        id='CREATE_INJECTOR_FAILED',
        name='Create injector failed',
        error_code='CREATE_INJECTOR_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Failed to create injector: {}.'
            )
        ]
    ),

    # */ IMPORT_DEPENDENCY_FAILED
    IMPORT_DEPENDENCY_FAILED = dict(
        id='IMPORT_DEPENDENCY_FAILED',
        name='Import dependency failed',
        error_code='IMPORT_DEPENDENCY_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Error importing dependency: {}.'
            )
        ]
    ),

    # */ CONTAINER_ATTRIBUTE_LOADING_FAILED
    CONTAINER_ATTRIBUTE_LOADING_FAILED = dict(
        id='CONTAINER_ATTRIBUTE_LOADING_FAILED',
        name='Container attribute loading failed',
        error_code='CONTAINER_ATTRIBUTE_LOADING_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Error loading container attributes: {}.'
            )
        ]
    ),

    # */ DEPENDENCY_NOT_FOUND
    DEPENDENCY_NOT_FOUND = dict(
        id='DEPENDENCY_NOT_FOUND',
        name='Dependency not found',
        error_code='DEPENDENCY_NOT_FOUND',
        message=[
            dict(
                lang='en_US',
                text='Dependency not found: {} ({}).'
            )
        ]
    ),

    # */ PARAMETER_PARSING_FAILED
    PARAMETER_PARSING_FAILED = dict(
        id='PARAMETER_PARSING_FAILED',
        name='Parameter parsing failed',
        error_code='PARAMETER_PARSING_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Error parsing parameter: {} - {}.'
            )
        ]
    ),

    # /* FEATURE_LOADING_FAILED
    FEATURE_LOADING_FAILED = dict(
        id='FEATURE_LOADING_FAILED',
        name='Feature loading failed',
        error_code='FEATURE_LOADING_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Failed loading features: {}.'
            )
        ]
    ),

    # */ FEATURE_NOT_FOUND
    FEATURE_NOT_FOUND = dict(
        id='FEATURE_NOT_FOUND',
        name='Feature not found',
        error_code='FEATURE_NOT_FOUND',
        message=[
            dict(
                lang='en_US',
                text='Feature not found: {}.'
            )
        ]
    ),

    # */ APP_REPOSITORY_IMPORT_FAILED
    APP_REPOSITORY_IMPORT_FAILED = dict(
        id='APP_REPOSITORY_IMPORT_FAILED',
        name='App repository import failed',
        error_code='APP_REPOSITORY_IMPORT_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Failed to import app repository: {}.'
            )
        ]
    ),

    # */ APP_INTERFACE_LOADING_FAILED
    APP_INTERFACE_LOADING_FAILED = dict(
        id='APP_INTERFACE_LOADING_FAILED',
        name='App interface loading failed',
        error_code='APP_INTERFACE_LOADING_FAILED',
        message=[
            dict(
                lang='en_US',
                text='Failed to load app interfaces: {}.'
            )
        ]
    ),

    # */ APP_INTERFACE_NOT_FOUND
    APP_INTERFACE_NOT_FOUND = dict(
        id='APP_INTERFACE_NOT_FOUND',
        name='App interface not found',
        error_code='APP_INTERFACE_NOT_FOUND',
        message=[
            dict(
                lang='en_US',
                text='App interface not found: {}.'
            )
        ]
    ),

    # */ APP_INTERFACE_INVALID
    APP_INTERFACE_INVALID = dict(
        id='APP_INTERFACE_INVALID',
        name='App interface invalid',
        error_code='APP_INTERFACE_INVALID',
        message=[
            dict(
                lang='en_US',
                text='Invalid app interface: {}.'
            )
        ]
    ),

    # */ REQUEST_DATA_INVALID
    REQUEST_DATA_INVALID = dict(
        id='REQUEST_DATA_INVALID',
        name='Request data invalid',
        error_code='REQUEST_DATA_INVALID',
        message=[
            dict(
                lang='en_US',
                text='Invalid request data: {}.'
            )
        ]
    ),
)

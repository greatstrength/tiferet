from ...objects import *
from ...constants import *
from ...services import *
from ...errors import *
from ...repositories import *

from schematics.exceptions import DataError


feature_cache: FeatureCache = None

def handle(request: ExecuteFeature, app_context, headers=Header, **kwargs):
    from ...error import ErrorManager
    from importlib import import_module
    from time import time
    
    class MessageContext():

        def __init__(self):
            self.headers = {}
            self.data = None
            self.services = None
            self.result = {}
            self.errors = ErrorManager()

    # Get feature from cache.
    feature: Feature = feature_cache.get(request.feature_id)
            
    # Create message context.
    context: MessageContext = MessageContext()

    # Add headers to the context.
    context.headers = headers

    for handler in feature.handlers:

        if request.debug:
            print('Executing function: "function": "{}"'.format(
                function.to_primitive()))

        headers.request_start = int(time())

        # Set data mapping and service container for feature function

        # Retrieve configured data mapping.
        data_mapping = feature_service.get_data_mapping(feature, handler)

        try:
            if data_mapping and data_mapping != 'default':
                if request.debug: print('Perform data mapping: "mapping": "{}"'.format(data_mapping))
                data_mapping_func = getattr(
                    import_module(DEFAULT_DATA_MAPPER_PATH.format(app_context.interface)),
                    data_mapping)
                if request.debug: print('Performing data mapping for following request: "mapping": "{}", "request": "{}", params: "{}"'.format(data_mapping, request, handler.params))
                context.data = data_mapping_func(context, request, app_context, **handler.params, **kwargs)
            else: 
                context.data = feature_service.map_feature_data(handler, request.data)
            if request.debug: print('Data mapping complete: "mapping": "{}", "data": "{}"'.format(data_mapping, context.data.to_primitive()))
            # Request model state validation
            try:
                context.data.validate()
            except AttributeError: # In the case where there is no configured data mapping
                pass
            except DataError as ex:
                raise InvalidRequestData(ex.messages)
        except TypeError as ex:
            print(ex)
            raise ex

        context.services = app_context.container

        # Format function module path.
        module_path = 'app.features.handlers.{}'.format(handler.function_path)

        # Import function module.
        if request.debug:
            print('Importing function: {}'.format(module_path))
        func = import_module(module_path)

        # Execute function handler.
        if request.debug:
            print('Executing function: {}'.format(module_path))
        try:
            result = func.handle(context)
        except AppError as ex:
            raise ex
        # For those who do now wish to assign the results to the context in the handler
        if result:
            context.result = result

        # Log activity
        if handler.log_activity:
            if request.debug:
                print('Logging activity for function: {}'.format(module_path))
            activity = import_module(DEFAULT_ACTIVITY_HANDLER_PATH)
            activity.handle(context)

        if request.debug:
            print('Finishing function: {}'.format(module_path))

    headers.request_end = int(time())

    return context



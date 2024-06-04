from ...objects import *
from ...constants import *
from ...services import *
from ...errors import *

from schematics.exceptions import DataError


feature_cache = None
error_cache = None

def handle(feature_id: str, request, app_context, debug: bool = False, **kwargs):
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

    # Load feature cache.
    feature_cache = app_context.container.feature_cache()

    # Get feature from cache.
    feature: Feature = feature_cache.get(feature_id)
            
    # Create message context.
    context: MessageContext = MessageContext()

    # Add errors first.  It's easier this way...
    context.errors = app_context.errors

    # Begin header mapping process.
    if debug:
        print('Perform header mapping: "mapping": "{}"'.format(
            feature.header_mapping))

    # Import header mappings module.
    header_module = import_module(
        DEFAULT_HEADER_MAPPER_PATH.format(app_context.interface))

    try:
        # Retrieve header mapping function.
        header_mapping_func = getattr(
            header_module, feature.header_mapping)
    except TypeError:
        # Retrieve default header mapping function if none is specified.
        header_mapping_func = getattr(header_module, 'default')

    # Get header data and add to message context.
    context.headers = header_mapping_func(request, app_context, **kwargs)

    for handler in feature.handlers:

        if debug:
            print('Executing function: "function": "{}"'.format(
                function.to_primitive()))

        context.headers['request_start'] = int(time())

        # Set data mapping and service container for feature function
        try:
            data_mapping = feature_service.get_data_mapping(feature, handler)
            if debug: print('Perform data mapping: "mapping": "{}"'.format(data_mapping))
            data_mapping_func = getattr(
                import_module(DEFAULT_DATA_MAPPER_PATH.format(app_context.interface)),
                data_mapping)
            if debug: print('Performing data mapping for following request: "mapping": "{}", "request": "{}", params: "{}"'.format(data_mapping, request, handler.params))
            context.data = data_mapping_func(context, request, app_context, **handler.params, **kwargs)
            if debug: print('Data mapping complete: "mapping": "{}", "data": "{}"'.format(data_mapping, context.data.to_primitive()))
            # Request model state validation
            try:
                context.data.validate()
            except AttributeError: # In the case where there is no configured data mapping
                pass
        except TypeError as ex:
            print(ex)
        except DataError as ex:
            raise AppError(
                app_context.errors.INVALID_REQUEST_DATA.format_message(ex.messages))

        context.services = app_context.container

        # Format function module path.
        module_path = 'app.features.{}'.format(handler.function_path)

        # Import function module.
        if debug:
            print('Importing function: {}'.format(module_path))
        func = import_module(module_path)

        # This is a crazy test.
        if handler.function_path == 'care_recipients.assign_device':
            setattr(func, 'care_recipient_repo', context.services.care_recipient_repo())
            setattr(func, 'device_repo', context.services.device_repo())

        # Execute function handler.
        if debug:
            print('Executing function: {}'.format(module_path))
        result = func.handle(context)
        # For those who do now wish to assign the results to the context in the handler
        if result:
            context.result = result

        # Log activity
        if handler.log_activity:
            if debug:
                print('Logging activity for function: {}'.format(module_path))
            activity = import_module(DEFAULT_ACTIVITY_HANDLER_PATH)
            activity.handle(context)

        if debug:
            print('Finishing function: {}'.format(module_path))

    context.headers['request_end'] = int(time())

    # Return result
    # Handle list scenario
    if type(context.result) == list:
        result = []
        for item in context.result:
            if isinstance(item, Model):
                if feature.use_role:
                    result.append(item.to_primitive(
                        role=feature.use_role))
                else:
                    result.append(item.to_primitive())
            else:
                result.append(item)
        return result
    if not context.result:
        return {}
    # Convert schematics models to primitive dicts.
    if isinstance(context.result, Model):
        if feature.use_role:
            return context.result.to_primitive(role=feature.use_role)
        else:
            return context.result.to_primitive()
    return context.result

# *** imports

# ** core
from typing import Dict, Any
from uuid import uuid4
import json

# ** app
from .settings import *
from ..models.feature import Request, ModelObject


# *** commands

# ** command: parse_request
class ParseRequest(Command):
    '''
    Parse a request for a feature.
    '''

    # * method: execute
    def execute(self,
        feature_id: str,
        data: Dict[str, Any] = {},
        headers: Dict[str, str] = {},
        debug: bool = False,
        **kwargs) -> Request:
        '''
        Parse the incoming request.

        :param feature_id: The feature ID.
        :type feature_id: str
        :param data: The data.
        :type data: dict
        :param headers: The headers.
        :type headers: dict
        :param debug: Debug flag.
        :type debug: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The request context.
        :rtype: Request
        '''

        # Parse the incoming data type value.
        for key, value in data.items():

            # If if the value is a string, integer, float, or boolean, continue to the next iteration.
            if isinstance(value, (str, int, float, bool)):
                continue

            # If the value is a list, dictionary, convert it to a JSON string.
            elif isinstance(value, (list, dict)):
                data[key] = json.dumps(value)

            # If the value is a model object, convert it to a primitive dictionary and then to a JSON string.
            elif isinstance(value, ModelObject):
                data[key] = json.dumps(value.to_primitive())

            # If the value is not a string, integer, float, boolean, list, dictionary, or model, raise an error.
            else:
                self.raise_error(
                    'REQUEST_DATA_INVALID',
                    key,
                    str(value)
                )
            
        # Add app interface id and name to the headers.
        headers.update(dict(
            feature_id=feature_id,
            session_id=str(uuid4()),
            app_name=self.name
        ))

        # Parse request.
        return ModelObject.new(
            Request,
            data=data,
            headers=headers,
            debug=debug
        )
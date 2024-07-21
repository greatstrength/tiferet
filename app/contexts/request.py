from typing import Dict, Any

from . import app


class RequestContext(object):

    feature_id: str = None
    headers: Dict[str, str] = None
    data: Dict[str, Any] = None
    context: app.AppContext = None
    result: Any = None

    def __init__(self, feature_id: str, headers: Dict[str, str], data: Dict[str, Any], context: app.AppContext, **kwargs):
        self.feature_id = feature_id
        self.headers = headers
        self.data = data
        self.context = context

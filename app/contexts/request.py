from typing import Dict, Any


class RequestContext(object):

    feature_id: str = None
    headers: Dict[str, str] = None
    data: Dict[str, Any] = None
    result: Any = None

    def __init__(self, feature_id: str, headers: Dict[str, str], data: Dict[str, Any], **kwargs):
        self.feature_id = feature_id
        self.headers = headers
        self.data = data

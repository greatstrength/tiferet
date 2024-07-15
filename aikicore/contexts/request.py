from typing import Dict, Any

class RequestContext(object):

    headers: Dict[str, str] = None
    data: Dict[str, Any] = None

    def __init__(self, headers: Dict[str, str], data: Dict[str, Any]):
        self.headers = headers
        self.data = data
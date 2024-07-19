from typing import Any

from ..contexts.request import RequestContext

def create_request(self, request: Any, **kwargs) -> RequestContext:
    return RequestContext(request)
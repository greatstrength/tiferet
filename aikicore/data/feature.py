from ..objects import *


class FeatureHandlerData(FeatureHandler, DataObject):
    
    class Options(DefaultOptions):
        pass

    def map(self, role: str = 'to_object', **kwargs):
        return super().map(FeatureHandler, role, **kwargs)
from ..objects import *


class FeatureHandlerData(FeatureHandler, DataObject):
    
    class Options(DefaultOptions):
        pass

    def map(self, role: str = 'to_object', **kwargs):
        return super().map(FeatureHandler, role, **kwargs)
    

class FeatureData(Feature, DataObject):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('handlers', 'group'),
            'to_data.yaml': blacklist('group')
        }

    handlers = t.ListType(t.ModelType(FeatureHandlerData), deserialize_from=['handlers', 'functions'])

    def map(self, role: str = 'to_object.yaml', **kwargs):
        return super().map(Feature, role, **kwargs)
    

class FeatureGroupData(FeatureGroup, DataObject):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('features'),
            'to_data.yaml': wholelist()
        }

    features = t.DictType(t.ModelType(FeatureData), default={})

    def map(self, role: str = 'to_object.yaml', **kwargs):
        return super().map(FeatureGroupData, role, **kwargs)
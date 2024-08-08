from typing import List, Dict, Any
from schematics import types as t
from schematics.types.serializable import serializable
from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.feature import Feature
from ..objects.feature import FeatureHandler
from ..objects.data import ModelData
from ..objects.data import DefaultOptions



class FeatureHandlerData(FeatureHandler, ModelData):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': wholelist(),
            'to_data.yaml': wholelist()
        }

    def map(self, role: str = 'to_object', **kwargs):
        return super().map(FeatureHandler, role, **kwargs)


class FeatureData(Feature, ModelData):

    class Options(DefaultOptions):
        roles = {
            'to_object.yaml': blacklist('feature_key'),
            'to_data.yaml': blacklist('feature_key', 'group_id')
        }

    handlers = t.ListType(t.ModelType(FeatureHandlerData),
                          deserialize_from=['handlers', 'functions'])
    
    @serializable
    def feature_key(self):
        return self.id.split('.')[-1]

    def map(self, role: str = 'to_object.yaml', **kwargs):
        return super().map(Feature, role, **kwargs)

    @staticmethod
    def new(**kwargs) -> 'FeatureData':

        # Create a new FeatureData object.
        _data = FeatureData(dict(**kwargs), strict=False)

        # Validate the new FeatureData object.
        _data.validate()

        # Return the new FeatureData object.
        return _data

    @staticmethod
    def from_yaml_data(id: str, group_id: str, **kwargs) -> 'FeatureData':

        # Create a new FeatureData object.
        _data = FeatureData(dict(
            id=id,
            group_id=group_id,
            **kwargs
        ), strict=False)

        # Validate the new FeatureData object.
        _data.validate()

        # Return the new FeatureData object.
        return _data

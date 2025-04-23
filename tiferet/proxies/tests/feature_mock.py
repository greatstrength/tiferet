# *** imports

# ** app
from ...contracts.feature import *


# *** mocks

# ** mock: mock_feature_proxy
class MockFeatureProxy(FeatureRepository):

    # * method: init
    def __init__(self, features: List[Feature] = []):
        self.features = features

    # * method: list
    def list(self) -> List[Feature]:
        return self.features
    
    # * method: get
    def get(self, feature_id: str) -> Feature:
        return next((feature for feature in self.features if feature.id == feature_id), None)
    
    # * method: exists
    def exists(self, feature_id: str) -> bool:
        return self.get(feature_id) is not None
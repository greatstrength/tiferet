# *** imports

# ** core
from abc import ABC, abstractmethod

# ** app
from ..domain.core import ModelObject


# *** contracts

# ** contract: model_contract
class ModelContract(ModelObject):
    '''
    A base contract for model objects.
    '''

    pass


# ** contract: repository
class Repository(ABC):
    '''
    A base contract for repository interfaces.
    '''

    pass


# ** contract: service
class Service(ABC):
    '''
    A base contract for service interfaces.
    '''

    pass
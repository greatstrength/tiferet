# *** imports

# ** infra
from schematics import Model
from schematics import types as t


# *** types

# ** type: string_type
class StringType(t.StringType):
    '''
    A string type.
    '''

    pass


# ** type: integer_type
class IntegerType(t.IntType):
    '''
    An integer type.
    '''

    pass


# ** type: float_type
class FloatType(t.FloatType):
    '''
    A float type.
    '''

    pass


# ** type: boolean_type
class BooleanType(t.BooleanType):
    '''
    A boolean type.
    '''

    pass


# ** type: list_type
class ListType(t.ListType):
    '''
    A list type.
    '''

    pass


# ** type: dict_type
class DictType(t.DictType):
    '''
    A dictionary type.
    '''

    pass


# ** type: model_type
class ModelType(t.ModelType):
    '''
    A model type.
    '''

    pass

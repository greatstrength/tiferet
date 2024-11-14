# *** imports

# ** infra
from schematics import types as t


# *** config

# ** config (class): string_type
class StringType(t.StringType):
    '''
    A string type.
    '''

    pass


# ** config (class): integer_type
class IntegerType(t.IntType):
    '''
    An integer type.
    '''

    pass


# ** config (class): float_type
class FloatType(t.FloatType):
    '''
    A float type.
    '''

    pass


# ** config (class): boolean_type
class BooleanType(t.BooleanType):
    '''
    A boolean type.
    '''

    pass


# ** config (class): list_type
class ListType(t.ListType):
    '''
    A list type.
    '''

    pass


# ** config (class): dict_type
class DictType(t.DictType):
    '''
    A dictionary type.
    '''

    pass


# ** config (class): model_type
class ModelType(t.ModelType):
    '''
    A model type.
    '''

    pass

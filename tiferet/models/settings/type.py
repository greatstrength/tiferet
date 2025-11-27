"""Model Settings Type Classes"""

# *** imports

# ** infra
from schematics import types as t

# *** classes

# ** class: string_type
class StringType(t.StringType):
    '''
    A string type.
    '''

    pass

# ** class: integer_type
class IntegerType(t.IntType):
    '''
    An integer type.
    '''

    pass

# ** class: float_type
class FloatType(t.FloatType):
    '''
    A float type.
    '''

    pass

# ** class: boolean_type
class BooleanType(t.BooleanType):
    '''
    A boolean type.
    '''

    pass

# ** class: list_type
class ListType(t.ListType):
    '''
    A list type.
    '''

    pass

# ** class: dict_type
class DictType(t.DictType):
    '''
    A dictionary type.
    '''

    pass

# ** class: model_type
class ModelType(t.ModelType):
    '''
    A model type.
    '''

    pass
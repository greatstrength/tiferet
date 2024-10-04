#** imp

import typing

from schematics import Model
from schematics import types as t

from ..objects.object import Entity
from ..objects.object import ValueObject


#** con

CONSTANT_DATA_TYPE_DEFAULT = 'str' #/
CONSTANT_DATA_TYPE_CHOICES = [
    'str',
    'list',
    'dict'
] #/
CONSTANT_TYPE_CHOICES = [
    'model',
    'service'
]


#** cls

class Constant(ValueObject):
    '''
    A constant value for the state of the object.
    '''

    #** atr

    name = t.StringType(
        required=True,
        metadata=dict(
            description='Name of the constant.',
        ),
    )

    data_type = t.StringType(
        required=True,
        default=CONSTANT_DATA_TYPE_DEFAULT,
        choices=CONSTANT_DATA_TYPE_CHOICES,
        metadata=dict(
            description='The data type of the constant.',
        ),
    )

    type = t.StringType(
        required=True,
        choices=CONSTANT_TYPE_CHOICES,
        metadata=dict(
            description='The type of the constant.',
        ),
    )

    group_id = t.StringType(
        required=True,
        metadata=dict(
            description='The context group ID of the constant.',
        ),
    )

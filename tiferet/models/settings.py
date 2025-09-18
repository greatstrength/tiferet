# *** imports

# ** infra
from schematics import Model, types as t


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


# ** class: model_object
class ModelObject(Model):
    '''
    A domain model object.
    '''

    # ** attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the object.'
        )
    )

    # ** attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the object.'
        )
    )

    # * method: new
    @staticmethod
    def new(
        model_type: type,
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'ModelObject':
        '''
        Initializes a new model object.

        :param model_type: The type of model object to create.
        :type model_type: type
        :param validate: True to validate the model object.
        :type validate: bool
        :param strict: True to enforce strict mode for the model object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new model object.
        :rclass: ModelObject
        '''

        # Create a new model object.
        _object: ModelObject = model_type(dict(
            **kwargs
        ), strict=strict)

        # Validate if specified.
        if validate:
            _object.validate()

        # Return the new model object.
        return _object


# ** model: value_object
class ValueObject(ModelObject):
    '''
    A domain model value object.
    '''
    pass


# ** class: entity
class Entity(ModelObject):
    '''
    A domain model entity.
    '''

    # ** attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The entity unique identifier.'
        )
    )
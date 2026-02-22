"""Tiferet Domain Settings"""

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

# ** class: domain_object
class DomainObject(Model):
    '''
    A domain model object.
    '''

    # * method: new
    @staticmethod
    def new(
        model_type: type,
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'DomainObject':
        '''
        Initializes a new domain object.

        :param model_type: The type of domain object to create.
        :type model_type: type
        :param validate: True to validate the domain object.
        :type validate: bool
        :param strict: True to enforce strict mode for the domain object.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new domain object.
        :rclass: DomainObject
        '''

        # Create a new domain object.
        domain_object: DomainObject = model_type(dict(
            **kwargs
        ), strict=strict)

        # Validate if specified.
        if validate:
            domain_object.validate()

        # Return the new domain object.
        return domain_object
    
    # * method: validate
    def validate(self, **kwargs):

        # Override to disable strict mode by default.
        return super().validate(False, True, None, **kwargs)

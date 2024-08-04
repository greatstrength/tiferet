from schematics import Model, types as t


OBJECT_TYPE_ENTITY = 'entity'
OBJECT_TYPE_VALUE_OBJECT = 'value_object'
OBJECT_TYPES = [
    'entity',
    'value_object'
]
OBJECT_TYPE_DEFAULT = OBJECT_TYPE_ENTITY


class Entity(Model):
    id = t.StringType(required=True)


class ValueObject(Model):
    pass


class ModelObject(Entity):
    '''
    A domain model component defined as a class object.
    '''

    name = t.StringType(required=True)
    group_id = t.StringType(required=True)
    type = t.StringType(choices=OBJECT_TYPES, default=OBJECT_TYPE_DEFAULT)
    class_name = t.StringType(required=True)
    description = t.StringType(required=True)
    base_type_id = t.StringType()

    @staticmethod
    def new(name: str, id: str = None, class_name: str = None, **kwargs):
        '''
        Initializes a new ModelObject object.

        :param name: The name of the model object.
        :type name: str
        :param id: The unique identifier for the model object.
        :type id: str
        :param class_name: The printed class name for the model object.
        :type class_name: str
        :return: A new ModelObject object.
        '''

        # Set the class name as the Pascal case of the name if not provided.
        if not class_name:
            class_name = name.title().replace(' ', '')

        # Set the unique identifier as the snake case of the class name if not provided.
        if not id:
            id = name.lower().replace(' ', '_')

        # Create a new ModelObject object.
        obj = ModelObject(dict(
            id=id,
            name=name,
            class_name=class_name,
            **kwargs
        ), strict=False)

        # Validate the new ModelObject object.
        obj.validate()

        # Return the new ModelObject object.
        return obj
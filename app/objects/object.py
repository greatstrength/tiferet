from schematics import Model, types as t


OBJECT_TYPE_ENTITY = 'entity'
OBJECT_TYPE_VALUE_OBJECT = 'value_object'
OBJECT_TYPES = [
    'entity',
    'value_object',
    'model',
]
OBJECT_TYPE_DEFAULT = OBJECT_TYPE_ENTITY
ATTRIBUTE_TYPES = [
    'str',
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'list',
    'dict',
    'model',
    'poly'
]
ATTRIBUTE_INNER_TYPES = [
    'str',
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'model'
]
DATE_TIME_SETTINGS_TZD_TYPES = [
    'require',
    'allow',
    'utc',
    'reject'
]
METHOD_TYPES = [
    'factory',
    'state',
]
METHOD_RETURN_TYPES = [
    'str',
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'list',
    'dict',
    'model',
]
METHOD_RETURN_INNER_TYPES = [
    'str',
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'model'
]
METHOD_PARAMETER_TYPES = [
    'str',
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'list',
    'dict',
    'model',
    'type',
    'args',
    'kwargs'
]
METHOD_PARAMETER_INNER_TYPES = [
    'str',
    'int',
    'float',
    'bool',
    'date',
    'datetime',
    'model'
]
METHOD_CODE_BLOCK_PYTHON = 'python'
METHOD_CODE_BLOCK_TYPES = [
    METHOD_CODE_BLOCK_PYTHON
]
METHOD_CODE_BLOCK_DEFAULT = METHOD_CODE_BLOCK_PYTHON


class Entity(Model):
    '''
    A domain model entity.
    '''

    id = t.StringType(
        required=True,
        metadata=dict(
            description='The entity unique identifier.'
        )
    )


class ValueObject(Model):
    '''
    A domain model value object.
    '''

    pass


class ObjectTypeSettings(ValueObject):
    '''
    Type-specific settings for an object attribute.
    '''

    pass


class StringSettings(ObjectTypeSettings):
    '''
    Type-specific settings for a string object attribute.
    '''

    regex = t.StringType(
        metadata=dict(
            description='The regular expression required for the string object attribute value.'
        )
    )

    min_length = t.IntType(
        metadata=dict(
            description='The minimum length for the string object attribute value.'
        )
    )

    max_length = t.IntType(
        metadata=dict(
            description='The maximum length for the string object attribute value.'
        )
    )

    @staticmethod
    def new(min_length: int = None, max_length: int = None, **kwargs) -> 'StringSettings':
        '''
        Initializes a new StringSettings object.
        
        :param min_length: The minimum length for the string object attribute.
        :type min_length: int
        :param max_length: The maximum length for the string object attribute.
        :type max_length: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new StringSettings object.
        '''

        # Set the min and max length as integers if provided.
        min_length = int(min_length) if min_length else None
        max_length = int(max_length) if max_length else None

        # Create a new StringSettings object.
        obj = StringSettings(dict(
            min_length=min_length,
            max_length=max_length,
            **kwargs
        ), strict=False)

        # Valdiate and return the new StringSettings object.
        obj.validate()
        return obj


class DateSettings(ObjectTypeSettings):
    '''
    Type-specific settings for a date object attribute.
    '''

    formats = t.StringType(
        metadata=dict(
            description='The formats for a date object attribute value.'
        )
    )

    @staticmethod
    def new(**kwargs) -> 'DateSettings':
        '''
        Initializes a new DateSettings object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new DateSettings object.
        '''

        # Create a new DateSettings object.
        obj = DateSettings(dict(
            **kwargs
        ), strict=False)

        # Validate and return the new DateSettings object.
        obj.validate()
        return obj


class DateTimeSettings(ObjectTypeSettings):
    '''
    Type-specific settings for a datetime object attribute.
    '''

    formats = t.StringType(
        metadata=dict(
            description='The formats for a datetime object attribute value.'
        )
    )

    serialized_format = t.StringType(
        metadata=dict(
            description='The output format for a datetime object attribute value.'
        )
    )

    tzd = t.StringType(
        choices=DATE_TIME_SETTINGS_TZD_TYPES,
        metadata=dict(
            description='The timezone policy for a datetime object attribute value.'
        )
    )

    convert_tz = t.BooleanType(
        metadata=dict(
            description='Whether to convert the timezone to UTC for the datetime object attribute value.'
        )
    )

    drop_tzinfo = t.BooleanType(
        metadata=dict(
            description='Whether to drop the timezone info for the datetime object attribute value.'
        )
    )

    @staticmethod
    def new(convert_tz: bool = None, drop_tzinfo: bool = None, **kwargs) -> 'DateTimeSettings':
        '''
        Initializes a new DateTimeSettings object.

        :param convert_tz: Whether to convert the timezone to UTC for the datetime object attribute value.
        :type convert_tz: bool
        :param drop_tzinfo: Whether to drop the timezone info for the datetime object attribute value.
        :type drop_tzinfo: bool
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new DateTimeSettings object.
        '''

        # Set Drop TZInfo to True if Convert TZ is True.
        if convert_tz and not drop_tzinfo:
            drop_tzinfo = True

        # Create a new DateTimeSettings object.
        obj = DateTimeSettings(dict(
            convert_tz=convert_tz,
            drop_tzinfo=drop_tzinfo,
            **kwargs
        ), strict=False)

        # Validate and return the new DateTimeSettings object.
        obj.validate()
        return obj


class ListSettings(ObjectTypeSettings):
    '''
    Type-specific settings for a list object attribute.
    '''

    min_size = t.IntType(
        metadata=dict(
            description='The minimum size for a list object attribute value.'
        )
    )

    max_size = t.IntType(
        metadata=dict(
            description='The maximum size for a list object attribute value.'
        )
    )

    @staticmethod
    def new(min_size: int = None, max_size: int = None, **kwargs) -> 'ListSettings':
        '''
        Initializes a new ListSettings object.

        :param min_size: The minimum size for a list object attribute value.
        :type min_size: int
        :param max_size: The maximum size for a list object attribute value.
        :type max_size: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ListSettings object.
        '''

        # Set the min and max size as integers if provided.
        min_size = int(min_size) if min_size else None
        max_size = int(max_size) if max_size else None

        # Create a new ListSettings object.
        obj = ListSettings(dict(
            min_size=min_size,
            max_size=max_size,
            **kwargs
        ), strict=False)

        # Validate and return the new ListSettings object.
        obj.validate()
        return obj


class DictSettings(ObjectTypeSettings):
    '''
    Type-specific settings for a dict object attribute.
    '''

    coerce_key = t.StringType()

    @staticmethod
    def new(**kwargs) -> 'DictSettings':
        '''
        Initializes a new DictSettings object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new DictSettings object.
        '''

        # Create a new DictSettings object.
        obj = DictSettings(dict(
            **kwargs
        ), strict=False)

        # Validate and return the new DictSettings object.
        obj.validate()
        return obj


class ObjectAttribute(ValueObject):
    '''
    A model object attribute.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The object attribute name.'
        )
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The object attribute description for inline documentation.'
        )
    )

    type = t.StringType(
        required=True,
        choices=ATTRIBUTE_TYPES,
        metadata=dict(
            description='The object attribute data type.'
        )
    )

    inner_type = t.StringType(
        choices=ATTRIBUTE_INNER_TYPES,
        metadata=dict(
            description='The object attribute inner data type if the base type is a list or dict.'
        )
    )

    type_object_id = t.StringType(
        metadata=dict(
            description='The object identifier for the attribute type for object attributes with a model type or inner type.'
        )
    )

    poly_type_object_ids = t.ListType(
        t.StringType(),
        default=[],
        metadata=dict(
            description='The object identifiers for an object attribute with a poly type.'
        )
    )

    required = t.BooleanType(
        metadata=dict(
            description='True if a value for the object attribute is required.'
        )
    )

    default = t.StringType(
        metadata=dict(
            description='The object attribute default value.'
        )
    )

    choices = t.ListType(
        t.StringType(),
        default=[],
        metadata=dict(
            description='The set of valid object attribute values.'
        )
    )

    type_settings = t.PolyModelType(
        [StringSettings, DateSettings, DateTimeSettings, ListSettings, DictSettings],
        metadata=dict(
            description='The type-specific settings for the object attribute.'
        )
    )

    @staticmethod
    def new(name: str, **kwargs) -> 'ObjectAttribute':
        '''
        Initializes a new ObjectAttribute object.

        :param name: The name of the object attribute.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ObjectAttribute object.
        '''

        # Set the name as the snake case of the name by default.
        name = name.lower().replace(' ', '_')

        # Create a new ModelAttribute object.
        obj = ObjectAttribute(dict(
            name=name,
            **kwargs
        ), strict=False)

        # Validate and return the new ModelAttribute object.
        obj.validate()
        return obj


class ObjectMethodParameter(ValueObject):
    '''
    A model object method parameter.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the object method parameter.'
        )
    )

    type = t.StringType(
        required=True,
        choices=METHOD_PARAMETER_TYPES,
        metadata=dict(
            description='The data type of the object method parameter.'
        )
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The description of the object method parameter for inline documentation.'
        )
    )

    inner_type = t.StringType(
        choices=METHOD_PARAMETER_INNER_TYPES,
        metadata=dict(
            description='The inner data type for object method parameters that are lists or dicts.'
        )
    )

    type_object_id = t.StringType(
        metadata=dict(
            description='The object identifier for the parameter type for object method parameters with a model type or inner type.'
        )
    )

    required = t.BooleanType(
        metadata=dict(
            description='True if the object method parameter is required.'
        )
    )

    default = t.StringType(
        metadata=dict(
            description='The default value for the object method parameter.'
        )
    )

    @staticmethod
    def new(name: str, **kwargs) -> 'ObjectMethodParameter':
        '''
        Initializes a new ObjectMethodParameter object.

        :param name: The name of the object method parameter.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ObjectMethodParameter object.
        :rtype: ObjectMethodParameter
        '''

        # Convert name to snake case.
        name = name.lower().replace(' ', '_')

        # Create a new ObjectMethodParameter object.
        obj = ObjectMethodParameter(dict(
            name=name,
            **kwargs
        ), strict=False)

        # Validate and return the new ObjectMethodParameter object.
        obj.validate()
        return obj
    

class ObjectMethodCodeBlock(ValueObject):
    '''
    A model object method code block.
    '''

    type = t.StringType(
        required=True,
        default=METHOD_CODE_BLOCK_DEFAULT,
        choices=METHOD_CODE_BLOCK_TYPES,
        metadata=dict(
            description='The code block type.'
        )
    )

    comments = t.ListType(
        t.StringType(),
        default=[],
        metadata=dict(
            description='The comments for the code block.'
        )
    )

    lines = t.ListType(
        t.StringType(),
        default=[],
        metadata=dict(
            description='The lines of code for the code block.'
        )
    )

    indent = t.IntType(
        metadata=dict(
            description='The number of tabs to indent the code block.'
        )
    )


class ObjectMethod(ValueObject):
    '''
    A model object method.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the object method.'
        )
    )

    type = t.StringType(
        required=True,
        choices=METHOD_TYPES,
        metadata=dict(
            description='The type of the object method.'
        )
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The description of the object method for inline documentation.'
        )
    )

    return_type = t.StringType(
        choices=METHOD_RETURN_TYPES,
        metadata=dict(
            description='The return type of the object method.'
        )
    )

    return_inner_type = t.StringType(
        choices=METHOD_RETURN_INNER_TYPES,
        metadata=dict(
            description='The inner return type for object methods that return a list or dict.'
        )
    )

    return_type_object_id = t.StringType(
        metadata=dict(
            description='The object identifier for the return type for object methods with a model return type or inner return type.'
        )
    )

    parameters = t.ListType(
        t.ModelType(ObjectMethodParameter),
        default=[],
        metadata=dict(
            description='The parameters for the object method.'
        )
    )

    code_block = t.ListType(
        t.ModelType(ObjectMethodCodeBlock),
        default=[],
        metadata=dict(
            description='The code blocks for the object method.'
        )
    )

    @staticmethod
    def new(name: str, **kwargs) -> 'ObjectMethod':
        '''
        Initializes a new ObjectMethod object.
        
        :param name: The name of the object method.
        :type name: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ObjectMethod object.
        :rtype: ObjectMethod
        '''

        # Convert name to snake case.
        name = name.lower().replace(' ', '_')

        # Create a new ObjectMethod object.
        obj = ObjectMethod(dict(
            name=name,
            **kwargs
        ), strict=False)

        # Validate and return the new ObjectMethod object.
        obj.validate()
        return obj

    def has_parameter(self, name: str) -> bool:
        '''
        Returns True if the parameter exists in the object method.

        :param name: The name of the parameter.
        :type name: str
        :return: True if the parameter exists in the object method.
        :rtype: bool
        '''

        # Format the parameter name.
        parameter_name = name.lower().replace(' ', '_')

        # Return True if the parameter exists in the object method.
        return any([parameter.name == parameter_name for parameter in self.parameters])

    def add_parameter(self, parameter: 'ObjectMethodParameter'):
        '''
        Adds a parameter to the object method.

        :param parameter: The parameter to add to the object method.
        :type parameter: ObjectMethodParameter
        '''

        # Add the parameter to the object method.
        self.parameters.append(parameter)


class ModelObject(Entity):
    '''
    A domain model component defined as a class object.
    '''

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The model object name.'
        )
    )

    group_id = t.StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the model object.'
        )
    )

    type = t.StringType(
        choices=OBJECT_TYPES,
        default=OBJECT_TYPE_DEFAULT,
        metadata=dict(
            description='The model object type.'
        )
    )

    class_name = t.StringType(
        required=True,
        metadata=dict(
            description='The model object class name.'
        )
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The model object description.'
        )
    )

    base_type_id = t.StringType(
        metadata=dict(
            description='The base model object identifier.'
        )
    )
    attributes = t.ListType(
        t.ModelType(ObjectAttribute),
        default=[],
        metadata=dict(
            description='The model object attributes.'
        )
    )

    methods = t.ListType(
        t.ModelType(ObjectMethod),
        default=[],
        metadata=dict(
            description='The model object methods.'
        )
    )

    @staticmethod
    def new(name: str, id: str = None, class_name: str = None, **kwargs) -> 'ModelObject':
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

        # Validate and return the new ModelObject object.
        obj.validate()
        return obj

    def has_attribute(self, name: str) -> bool:
        '''
        Returns True if the attribute exists in the model object.

        :param name: The name of the attribute.
        :type name: str
        :return: True if the attribute exists in the model object.
        :rtype: bool
        '''

        # Format the attribute name.
        attribute_name = name.lower().replace(' ', '_')

        # Return True if the attribute exists in the model object.
        return any([attribute.name == attribute_name for attribute in self.attributes])

    def add_attribute(self, attribute: 'ObjectAttribute'):
        '''
        Adds an attribute to the model object.

        :param attribute: The attribute to add to the model object.
        :type attribute: ObjectAttribute
        '''

        # Add the attribute to the model object.
        self.attributes.append(attribute)

    def has_method(self, name: str) -> bool:
        '''
        Returns True if the method exists in the model object.

        :param name: The name of the method.
        :type name: str
        :return: True if the method exists in the model object.
        :rtype: bool
        '''

        # Return True if the method exists in the model object.
        return self.get_method(name) is not None
    
    def get_method(self, name: str) -> 'ObjectMethod':
        '''
        Returns the method with the specified name.

        :param name: The name of the method.
        :type name: str
        :return: The method with the specified name.
        :rtype: ObjectMethod
        '''

        # Format the method name.
        method_name = name.lower().replace(' ', '_')

        # Return the method with the specified name.
        return next((method for method in self.methods if method.name == method_name), None)

    def add_method(self, method: 'ObjectMethod'):
        '''
        Adds a method to the model object.

        :param method: The method to add to the model object.
        :type method: ObjectMethod
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Add the method to the model object.
        self.methods.append(method)

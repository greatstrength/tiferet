#** imp

import typing

from schematics import Model
from schematics import types as t

from .object import Entity
from .object import ValueObject


#** con

ATTRIBUTE_TYPES = [
    'model',
    'data',
    'context',
    'serializable'
]
IMPORT_TYPE_CORE = 'core'
IMPORT_TYPE_INFRA = 'infra'
IMPORT_TYPE_APP = 'app'
IMPORT_TYPES = [
    IMPORT_TYPE_CORE,
    IMPORT_TYPE_INFRA,
    IMPORT_TYPE_APP,
]
MODULE_TYPE_OBJECTS = 'objects'
MODULE_TYPES = [
    MODULE_TYPE_OBJECTS,
]
TAB = '    '


#** cls

class Import(ValueObject):
    '''
    A code import object.
    '''

    #** atr

    type = t.StringType(
        required=True,
        choices=IMPORT_TYPES,
        metadata=dict(
            description='The type of the import.'
        ),
    )

    from_module = t.StringType(
        metadata=dict(
            description='The module to import from.'
        ),
    )

    import_module = t.StringType(
        required=True,
        metadata=dict(
            description='The module to import.'
        ),
    )

    alias = t.StringType(
        metadata=dict(
            description='The alias for the import.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'Import':
        '''
        Initializes a new Import object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new Import object.
        :rtype: Import
        '''

        # Create and return the import.
        return super(Import, Import).new(Import, **kwargs)


class Variable(ValueObject):
    '''
    A code variable object.
    '''

    #** atr

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the variable.'
        ),
    )

    type = t.StringType(
        metadata=dict(
            description='The type of the variable.'
        ),
    )

    value = t.StringType(
        metadata=dict(
            description='The value of the variable.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'Variable':
        '''
        Initializes a new Variable object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new Variable object.
        :rtype: Variable
        '''

        # Create and return the variable.
        return super(Variable, Variable).new(Variable, **kwargs)


class Parameter(ValueObject):
    '''
    A code parameter object.
    '''

    #** atr

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the parameter.'
        ),
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The description of the parameter.'
        ),
    )

    type = t.StringType(
        metadata=dict(
            description='The type of the parameter.'
        ),
    )

    is_kwargs = t.BooleanType(
        metadata=dict(
            description='Whether the parameter is a keyword arguments parameter.'
        ),
    )

    default = t.StringType(
        metadata=dict(
            description='The default value of the parameter.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'Parameter':
        '''
        Initializes a new Parameter object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new Parameter object.
        :rtype: Parameter
        '''

        # Create and return the parameter.
        return super(Parameter, Parameter).new(Parameter, **kwargs)


class CodeBlock(ValueObject):

    #** atr

    lines = t.ListType(
        t.StringType,
        required=True,
        metadata=dict(
            description='The lines of code in the block.'
        ),
    )

    comments = t.ListType(
        t.StringType,
        metadata=dict(
            description='The comments for the code block.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'CodeBlock':
        '''
        Initializes a new CodeBlock object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new CodeBlock object.
        :rtype: CodeBlock
        '''

        # Create and return the code block.
        return super(CodeBlock, CodeBlock).new(CodeBlock, **kwargs)


class Function(ValueObject):
    '''
    A code function object.
    '''

    #** atr

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the function.'
        ),
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The description of the function.'
        ),
    )

    parameters = t.ListType(
        t.ModelType(Parameter),
        default=[],
        metadata=dict(
            description='The parameters of the function.'
        ),
    )

    return_type = t.StringType(
        metadata=dict(
            description='The return type of the function.'
        ),
    )

    return_description = t.StringType(
        metadata=dict(
            description='The description of the return value.'
        ),
    )

    is_class_method = t.BooleanType(
        metadata=dict(
            description='Whether the function is a class method.'
        ),
    )

    is_static_method = t.BooleanType(
        metadata=dict(
            description='Whether the function is a static method.'
        ),
    )

    code_block = t.ListType(
        t.ModelType(CodeBlock),
        default=[],
        metadata=dict(
            description='The code block for the function.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'Function':
        '''
        Initializes a new Function object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new Function object.
        :rtype: Function
        '''

        # Create and return the function.
        return super(Function, Function).new(Function, **kwargs)


class Class(ValueObject):
    '''
    A code class object.
    '''

    #** atr

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the class.'
        ),
    )

    description = t.StringType(
        required=True,
        metadata=dict(
            description='The description of the class.'
        ),
    )

    base_classes = t.ListType(
        t.StringType,
        metadata=dict(
            description='The base class names for the class.'
        ),
    )

    attributes = t.ListType(
        t.ModelType(Variable),
        default=[],
        metadata=dict(
            description='The attributes of the class.'
        ),
    )

    methods = t.ListType(
        t.ModelType(Function),
        default=[],
        metadata=dict(
            description='The methods of the class.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'Class':
        '''
        Initializes a new Class object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new Class object.
        :rtype: Class
        '''

        # Create and return the class.
        return super(Class, Class).new(Class, **kwargs)


class Module(Entity):
    '''
    A module file represented as an object.
    '''

    #** atr

    type = t.StringType(
        required=True,
        choices=MODULE_TYPES,
        metadata=dict(
            description='The module type.'
        )
    )

    imports = t.ListType(
        t.ModelType(Import),
        default=[],
        metadata=dict(
            description='The imports for the module.'
        ),
    )

    constants = t.ListType(
        t.ModelType(Variable),
        default=[],
        metadata=dict(
            description='The constants for the module.'
        ),
    )

    functions = t.ListType(
        t.ModelType(Function),
        default=[],
        metadata=dict(
            description='The functions for the module.'
        ),
    )

    classes = t.ListType(
        t.ModelType(Class),
        default=[],
        metadata=dict(
            description='The classes for the module.'
        ),
    )

    #** met

    @staticmethod
    def new(**kwargs) -> 'Module':
        '''
        Initializes a new Module object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: The new Module object.
        :rtype: Module
        '''

        # Create and return the module.
        return super(Module, Module).new(Module, **kwargs)
    
    def get_class(self, class_name: str) -> Class:
        '''
        Gets a class by name.

        :param class_name: The class name.
        :type class_name: str
        :return: The class.
        :rtype: Class
        '''

        # Get the class by name.
        return next((c for c in self.classes if c.name == class_name), None)

    def set_component(self, component: typing.Any):
        '''
        Sets a component for the module.

        :param component: The component to set.
        :type component: Any
        '''

        # Get the components based on the component type.
        components = None
        if isinstance(component, Variable):
            components = self.constants
        elif isinstance(component, Function):
            components = self.functions
        elif isinstance(component, Class):
            components = self.classes
        
        # If the component matches none of the types, exit.
        else:
            return

        # If the components are set...
        # Replace the component if it already exists.
        # Otherwise, add the component.
        if components:
            for i, comp in enumerate(components):
                if comp.name == component.name:
                    components[i] = component
                    return
        components.append(component)

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

        :param kwargs: The keyword arguments.
        :type kwargs: Dict[str, Any]
        :return: The new Import object.
        :rtype: Import
        '''

        # Create the import.
        _import = Import(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the import.
        _import.validate()
        return _import


class CodeComponent(ValueObject):
    '''
    A code component object.
    '''

    #** atr

    name = t.StringType(
        required=True,
        metadata=dict(
            description='The name of the component.'
        ),
    )


class Variable(CodeComponent):
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

        :param kwargs: The keyword arguments.
        :type kwargs: Dict[str, Any]
        :return: The new Variable object.
        :rtype: Variable
        '''

        # Create the variable.
        _variable = Variable(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the variable.
        _variable.validate()
        return _variable


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

        :param kwargs: The keyword arguments.
        :type kwargs: Dict[str, Any]
        :return: The new Parameter object.
        :rtype: Parameter
        '''

        # Create the parameter.
        _parameter = Parameter(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the parameter.
        _parameter.validate()
        return _parameter


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

        :param kwargs: The keyword arguments.
        :type kwargs: Dict[str, Any]
        :return: The new CodeBlock object.
        :rtype: CodeBlock
        '''

        # Create the code block.
        _code_block = CodeBlock(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the code block.
        _code_block.validate()
        return _code_block


class Function(CodeComponent):
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

        :param kwargs: The keyword arguments.
        :type kwargs: Dict[str, Any]
        :return: The new Function object.
        :rtype: Function
        '''

        # Create the function.
        _function = Function(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the function.
        _function.validate()
        return _function


class Class(CodeComponent):
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

        :return: The new Class object.
        :rtype: Class
        '''

        # Create the class.
        _class = Class(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the class.
        _class.validate()
        return _class


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

        :return: The new Module object.
        :rtype: Module
        '''

        # Create the module.
        _module = Module(
            dict(**kwargs),
            strict=False
        )

        # Validate and return the module.
        _module.validate()
        return _module

    def set_component(self, component: CodeComponent):
        '''
        Sets a component for the module.

        :param component: The component to set.
        :type component: CodeComponent
        '''

        # Get the components based on the component type.
        components = None
        if isinstance(component, Variable):
            components = self.constants
        elif isinstance(component, Function):
            components = self.functions
        elif isinstance(component, Class):
            components = self.classes

        # If the components are set...
        # Replace the component if it already exists.
        # Otherwise, add the component.
        if components:
            for i, comp in enumerate(components):
                if comp.name == component.name:
                    components[i] = component
                    return
        components.append(component)

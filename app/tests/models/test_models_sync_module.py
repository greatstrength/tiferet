from ...objects.sync import Module
from ...objects.sync import Import
from ...objects.sync import Class
from ...objects.sync import Variable
from ...objects.sync import Function

def test_module_new():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
        imports=[
            Import.new(
                type='core',
                import_module='json',
            ),
        ]
    )

    # Assert the module is correct.
    assert module.id == 'object'
    assert module.type == 'objects'
    assert len(module.imports) == 1
    assert module.imports[0].type == 'core'
    assert module.imports[0].import_module == 'json'


def test_module_get_class():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
        classes=[
            Class.new(
                name='Object',
                base_classes=['object'],
                description='An object.',
            ),
        ]
    )

    # Get the class.
    _class = module.get_class('Object')

    # Assert the class is correct.
    assert _class.name == 'Object'
    assert _class.base_classes == ['object']
    assert _class.description == 'An object.'


def test_module_get_class_returns_none():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
        classes=[
            Class.new(
                name='Object',
                base_classes=['object'],
                description='An object.',
            ),
        ]
    )

    # Get the class.
    _class = module.get_class('NotObject')

    # Assert the class is None.
    assert _class is None


def test_module_set_component_constant():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
    )

    # Create the constant variable.
    constant = Variable.new(
        name='name',
        type='str',
        value='None',
    )

    # Set the variable as a constant.
    module.set_component(constant)

    # Assert the constant is correct.
    assert module.constants[0].name == 'name'
    assert module.constants[0].type == 'str'
    assert module.constants[0].value == 'None'


def test_module_set_component_function():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
    )

    # Create the function.
    function = Function.new(
        name='create_object',
        return_type='object',
        description='Creates an object.',
        return_description='The object.',
    )

    # Set the function.
    module.set_component(function)

    # Assert the function is correct.
    assert module.functions[0].name == 'create_object'
    assert module.functions[0].return_type == 'object'
    assert module.functions[0].description == 'Creates an object.'
    assert module.functions[0].return_description == 'The object.'


def test_module_set_component_class():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
    )

    # Create the class.
    _class = Class.new(
        name='Object',
        base_classes=['object'],
        description='An object.',
    )

    # Set the class.
    module.set_component(_class)

    # Assert the class is correct.
    assert module.classes[0].name == 'Object'
    assert module.classes[0].base_classes == ['object']
    assert module.classes[0].description == 'An object.'


def test_module_set_component_invalid():

    # Create the module.
    module = Module.new(
        id='object',
        type='objects',
    )

    # Set the invalid component.
    module.set_component('invalid')

    # Assert the module has no components.
    assert len(module.constants) == 0
    assert len(module.functions) == 0
    assert len(module.classes) == 0
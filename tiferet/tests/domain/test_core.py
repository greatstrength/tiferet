from ...domain import *

def test_model_object_new():
    
    # Create a new model object.
    class TestModelObject(ModelObject):
        
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )

    model_object = ModelObject.new(TestModelObject, attribute='test')

    # Assert the model object is valid.
    assert isinstance(model_object, TestModelObject)
    assert model_object.attribute == 'test'


def test_entity_new():
    
    # Create a new entity.
    class TestEntity(Entity):
        
        id = StringType(
            required=True,
            metadata=dict(
                description='The entity unique identifier.'
            ),
        )

    entity = Entity.new(TestEntity, id='test')

    # Assert the entity is valid.
    assert isinstance(entity, TestEntity)
    assert entity.id == 'test'


def test_value_object_new():

    # Create a new value object.
    class TestValueObject(ValueObject):
        
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )

    value_object = ValueObject.new(TestValueObject, attribute='test')

    # Assert the value object is valid.
    assert isinstance(value_object, TestValueObject)
    assert value_object.attribute == 'test'


def test_data_object_from_model():

    # Create a new model object.
    class TestModelObject(ModelObject):
        pass

    # Create a new data object from the model object.
    model_object = TestModelObject.new(TestModelObject)
    data_object = DataObject.from_model(TestModelObject, **model_object.to_primitive())

    # Assert the data object is valid.
    assert isinstance(data_object, DataObject)


def test_data_object_from_data():

    # Create a new data object.
    class TestDataObject(DataObject):
        
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )

    data_object = DataObject.from_data(TestDataObject, attribute='test')

    # Assert the data object is valid.
    assert isinstance(data_object, TestDataObject)
    assert data_object.attribute == 'test'


def test_data_object_allow():

    # Create a new allow role.
    role = DataObject.allow('test')

    # Assert the role is valid.
    assert role.fields == {'test'}


def test_data_object_deny():

    # Create a new deny role.
    role = DataObject.deny('test')

    # Assert the role is valid.
    assert role.fields == {'test'}


def test_module_dependency_new():

    # Create a new module dependency.
    module_dependency = ModuleDependency.new(
        ModuleDependency,
        module_path='tests.repos.test',
        class_name='YamlProxy',
    )

    # Assert the module dependency is valid.
    assert isinstance(module_dependency, ModuleDependency)
    assert module_dependency.module_path == 'tests.repos.test'
    assert module_dependency.class_name == 'YamlProxy'
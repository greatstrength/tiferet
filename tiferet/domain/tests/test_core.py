# *** imports

# ** infra
import pytest

# ** app
from . import *


# *** fixtures

# ** fixture: test_model_object
@pytest.fixture
def test_model_object():
    class TestModelObject(ModelObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )
    return TestModelObject


# ** fixture: test_entity
@pytest.fixture
def test_entity():
    class TestEntity(Entity):
        id = StringType(
            required=True,
            metadata=dict(
                description='The entity unique identifier.'
            ),
        )
    return TestEntity


# ** fixture: test_value_object
@pytest.fixture
def test_value_object():
    class TestValueObject(ValueObject):
        attribute = StringType(
            required=True,
            metadata=dict(
                description='The attribute.'
            ),
        )
    return TestValueObject


# ** fixture: module_dependency
@pytest.fixture
def module_dependency():
    return ModuleDependency.new(
        ModuleDependency,
        module_path='tests.repos.test',
        class_name='YamlProxy',
    )


# *** tests

# ** domain: test_model_object_new
def test_model_object_new(test_model_object):
    
    # Create a new model object using the fixture.
    model_object = ModelObject.new(test_model_object, attribute='test')

    # Assert the model object is valid.
    assert isinstance(model_object, test_model_object)
    assert model_object.attribute == 'test'


# ** domain: test_entity_new
def test_entity_new(test_entity):

    # Create a new entity using the fixture.
    entity = Entity.new(test_entity, id='test')

    # Assert the entity is valid.
    assert isinstance(entity, test_entity)
    assert entity.id == 'test'


# ** domain: test_value_object_new
def test_value_object_new(test_value_object):

    # Create a new value object using the fixture.
    value_object = ValueObject.new(test_value_object, attribute='test')

    # Assert the value object is valid.
    assert isinstance(value_object, test_value_object)
    assert value_object.attribute == 'test'


# ** domain: test_module_dependency_new
def test_module_dependency_new(module_dependency):

    # Assert the module dependency is valid using the fixture.
    assert isinstance(module_dependency, ModuleDependency)
    assert module_dependency.module_path == 'tests.repos.test'
    assert module_dependency.class_name == 'YamlProxy'
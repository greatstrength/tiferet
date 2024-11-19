def test_container_dependency_new():

    # Import test data.
    from ..configs.container import test_container_dependency as container_dependency

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tests.repos.test'
    assert container_dependency.class_name == 'YamlProxy'
    assert container_dependency.flag == 'test'
    assert container_dependency.parameters == {'config_file': 'test.yml'}


def test_container_attribute_new():

    # Import test data.
    from ..configs.container import test_container_attribute as container_attribute

    # Assert the container attribute is valid.
    assert container_attribute.id == 'test_repo'
    assert container_attribute.type == 'data'
    assert len(container_attribute.dependencies) == 1
    assert container_attribute.dependencies[0].module_path == 'tests.repos.test'
    assert container_attribute.dependencies[0].class_name == 'YamlProxy'
    assert container_attribute.dependencies[0].flag == 'test'
    assert container_attribute.dependencies[0].parameters == {
        'config_file': 'test.yml'}


def test_container_attribute_get_dependency():

    # Import test data.
    from ..configs.container import test_container_attribute as container_attribute

    # Get the container dependency.
    container_dependency = container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tests.repos.test'
    assert container_dependency.class_name == 'YamlProxy'
    assert container_dependency.flag == 'test'
    assert container_dependency.parameters == {'config_file': 'test.yml'}


def test_container_attribute_get_dependency_invalid():

    # Import test data.
    from ..configs.container import test_container_attribute as container_attribute

    # Assert the container dependency is invalid.
    assert container_attribute.get_dependency('invalid') is None


def test_container_attribute_set_dependency():

    # Import test data.
    from ..configs.container import test_container_attribute_no_dependencies as container_attribute
    from ..configs.container import test_container_dependency as container_dependency

    # Assert that the container attribute has no dependencies.
    assert len(container_attribute.dependencies) == 0

    # Set the container dependency.
    container_attribute.set_dependency(container_dependency)

    # Assert the container dependency is valid.
    assert len(container_attribute.dependencies) == 1
    assert container_attribute.dependencies[0].module_path == 'tests.repos.test'
    assert container_attribute.dependencies[0].class_name == 'YamlProxy'
    assert container_attribute.dependencies[0].flag == 'test'


def test_container_attribute_set_dependency_exists():

    # Import test data.
    from ..configs.container import test_container_attribute as container_attribute
    from ..configs.container import test_container_dependency as container_dependency

    # Modify the container dependency.
    container_dependency.module_path = 'tests.repos.super_test'
    container_dependency.class_name = 'SuperYamlProxy'

    # Set the container dependency.
    container_attribute.set_dependency(container_dependency)

    # Get the container dependency.
    container_dependency = container_attribute.get_dependency('test')

    # Assert the container dependency is valid.
    assert container_dependency.module_path == 'tests.repos.super_test'
    assert container_dependency.class_name == 'SuperYamlProxy'
    assert container_dependency.flag == 'test'
    assert container_dependency.parameters == {'config_file': 'test.yml'}

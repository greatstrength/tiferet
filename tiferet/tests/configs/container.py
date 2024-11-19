from ...domain import ContainerDependency, ContainerAttribute

# ** domain: test_container_dependency
test_container_dependency = ContainerDependency.new(
    module_path='tests.repos.test',
    class_name='YamlProxy',
    flag='test',
    parameters={'config_file': 'test.yml'}
)

# ** domain: test_container_attribute
test_container_attribute = ContainerAttribute.new(
    id='test_repo',
    type='data',
    dependencies=[
        test_container_dependency,
    ],
)

# ** domain: test_container_attribute_no_dependencies
test_container_attribute_no_dependencies = ContainerAttribute.new(
    id='test_repo',
    type='data',
    dependencies=[],
)

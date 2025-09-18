# *** imports

# ** app
from . import *


# *** fixtures

# ** fixture: test_yaml_file
@pytest.fixture
def test_yaml_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as temp:
        temp.write(yaml.dump({'test': {'key': 'value'}}))
        temp.close()
        yield temp.name
    os.unlink(temp.name)


# *** tests

# ** test: yaml_client_load
def test_yaml_client_load(test_yaml_file):

    # Load the yaml file.
    data = yaml_client.load(test_yaml_file)

    # Ensure the data was loaded correctly.
    assert data == {'test': {'key': 'value'}}


# ** test: load_yaml_file_with_custom_create_data
def test_load_yaml_file_with_custom_start_node(test_yaml_file):
    
    # Load the yaml file with a custom start node.
    data = yaml_client.load(test_yaml_file, start_node=lambda data: data.get('test'))
    
    # Ensure the data was loaded correctly.
    assert data == {'key': 'value'}


# ** test: yaml_client_save
def test_yaml_client_save(test_yaml_file):
    
    # Save the data to the yaml file.
    yaml_client.save(test_yaml_file, {'key2': 'value2'}, 'test')
    
    # Load the yaml file.
    with open(test_yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    # Ensure the data was saved correctly.
    assert data == {'test': {'key2': 'value2'}}

# ** test: yaml_client_save_new_data
def test_yaml_client_save_new_data(test_yaml_file):
    
    # Save the data to the yaml file.
    yaml_client.save(test_yaml_file, {'key2': 'value2'}, 'test/test2')
    
    # Load the yaml file.
    with open(test_yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    # Ensure the data was saved correctly.
    assert data.get('test').get('test2') == {'key2': 'value2'}


def test_yaml_client_save_new_data_to_new_node(test_yaml_file):
    
    # Save the data to the yaml file.
    yaml_client.save(test_yaml_file, {'key2': 'value2'}, 'test2/test/whatever')
    
    # Load the yaml file.
    with open(test_yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    # Ensure the data was saved correctly.
    assert data.get('test2').get('test').get('whatever') == {'key2': 'value2'}


# ** test_yaml_client_save_new_data_to_existing_node
def test_yaml_client_save_new_data_to_existing_node(test_yaml_file):
    
    # Save the data to the yaml file.
    yaml_client.save(test_yaml_file, {'key2': 'value2'}, 'test/test2')
    
    # Load the yaml file.
    with open(test_yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    # Ensure the data was saved correctly.
    assert data.get('test').get('test2') == {'key2': 'value2'}
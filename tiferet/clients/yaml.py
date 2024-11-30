# *** imports

# ** infra
import yaml


# *** functions

# ** function: load
def load(path: str, create_data = lambda data: data, start_node = lambda data: data, **kwargs):
    '''
    Load the data from the yaml file.

    :param path: The path to the yaml file.
    :type path: str
    :param create_data: The function to create the data.
    :type create_data: function
    :param start_node: The function to start the node.
    :type start_node: function
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: The data.
    :rtype: dict
    '''

    # Load the data from the yaml file.
    with open(path, 'r') as file:
        data = yaml.safe_load(file)

    # Find the start node.
    try:
        data = start_node(data)
    except AttributeError:
        return None
    
    # Return the data if it is None.
    if data == None:
        return None
    
    # Create and return the data.
    return create_data(data, **kwargs)


# ** function: save
def save(yaml_file: str, data: dict, data_save_path: str = None):
    '''
    Save the data to the yaml file.

    :param yaml_file: The path to the yaml file.
    :type yaml_file: str
    :param data: The data to save.
    :type data: dict
    :param data_save_path: The path to save the data to.
    :type data_save_path: str
    '''

    # Save the data to the yaml file and exit if no save path is provided.
    if not data_save_path:
        with open(yaml_file, 'w') as file:
            yaml.safe_dump(data, file)
        return

    # Load the yaml data.
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)

    # Get the data save path list.
    save_path_list = data_save_path.split('/')

    # Update the yaml data.
    new_yaml_data = None
    for fragment in save_path_list[:-1]:

        # If the new yaml data exists, update it.
        try:
            new_yaml_data = new_yaml_data[fragment]

        # If the new yaml data does not exist, create it from the yaml data.
        except TypeError:
            try:
                new_yaml_data = yaml_data[fragment]
                continue  
        
            # If the fragment does not exist, create it.
            except KeyError:
                new_yaml_data = yaml_data[fragment] = {}

        # If the fragment does not exist, create it.
        except KeyError: 
            new_yaml_data[fragment] = {}
            new_yaml_data = new_yaml_data[fragment]

    # Update the yaml data.
    try:
        new_yaml_data[save_path_list[-1]] = data
    # if there is a type error because the new yaml data is None, update the yaml data directly.
    except TypeError:
        yaml_data[save_path_list[-1]] = data

    # Save the updated yaml data.
    with open(yaml_file, 'w') as file:
        yaml.safe_dump(yaml_data, file)

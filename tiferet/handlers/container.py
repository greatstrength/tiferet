# *** imports

# ** app
from ..commands import *
from ..contracts.container import *


# *** handlers

# ** handler: container_handler
class ContainerHandler(ContainerService):

    '''
    A container handler is a class that is used to create a container object.
    '''

    # * attribute: container_repo
    container_repo: ContainerRepository

    # * method: __init__
    def __init__(self, container_repo: ContainerRepository):
        '''
        Initialize the container handler.

        :param name: The name of the container.
        :type name: str
        :param dependencies: The dependencies.
        :type dependencies: dict
        '''
        
        # Assign the container repository.
        self.container_repo = container_repo
    
    # * method: list_all
    def list_all(self) -> Tuple[List[ContainerAttribute], Dict[str, str]]:
        '''
        List all container attributes and constants.

        :return: A tuple containing a list of container attributes and a dictionary of constants.
        :rtype: Tuple[List[ContainerAttribute], Dict[str, str]]
        '''

        # Retrieve all container attributes and constants from the repository.
        attributes, constants = self.container_repo.list_all()

        # Return the attributes and constants.
        return attributes, constants
    
    # * method: load_constants
    def load_constants(self, attributes: List[ContainerAttribute], constants: Dict[str, str] = {}, flags: List[str] = []) -> Dict[str, str]:
        '''
        Load constants from the container attributes.

        :param attributes: The list of container attributes.
        :type attributes: List[ContainerAttribute]
        :param constants: The dictionary of constants.
        :type constants: Dict[str, str]
        :return: A dictionary of constants.
        :rtype: Dict[str, str]
        '''

        # Raise an error if there are no attributes provided.
        if not attributes:
            raise_error.execute(
                'CONTAINER_ATTRIBUTES_NOT_FOUND',
                'No container attributes provided to load the container.',
            )

        # If constants are provided, clean the parameters using the parse_parameter command.
        constants = {k: parse_parameter.execute(v) for k, v in constants.items()}

        # Iterate through each attribute to clean parameter dictionaries.
        # For each attribute, parse its parameters and add them to the constants dictionary.
        # For each dependency, parse its parameters and add them to the constants dictionary.
        for attr in attributes:
            constants.update({k: parse_parameter.execute(v) for k, v in attr.parameters.items()})
            dependency = attr.get_dependency(flags)
            if dependency:
                constants.update({k: parse_parameter.execute(v) for k, v in dependency.parameters.items()})

        # Return the updated constants dictionary.
        return constants
    
    # * method: get_dependency_type
    def get_dependency_type(self, attribute: ContainerAttribute, flags: List[str] = []) -> type:
        '''
        Get the type of a container attribute.

        :param attribute: The container attribute.
        :type attribute: ContainerAttribute
        :return: The type of the container attribute.
        :rtype: type
        '''

        # Check the flagged dependencies for the type first.
        for dep in attribute.dependencies:
            if dep.flag in flags:
                return import_dependency.execute(
                    dep.module_path,
                    dep.class_name
                ) 
        
        # Otherwise defer to an available default type.
        if attribute.module_path and attribute.class_name:
            return import_dependency.execute(
                attribute.module_path,
                attribute.class_name
            )
            
        # If no type is found, raise an error.
        raise_error.execute(
            'DEPENDENCY_TYPE_NOT_FOUND',
            f'No dependency type found for attribute {attribute.id} with flags {flags}.',
            attribute.id,
            flags
        )
# *** imports

# ** app
from ..configs import *
from ..models import ModelObject
from ..contexts import import_dependency


# *** commands

# ** command: service_command
class ServiceCommand(object):
    '''
    A service command class.
    '''

    # * method: execute
    def execute(self, **kwargs) -> Any:
        '''
        Execute the service command.

        :param kwargs: The command arguments.
        :type kwargs: dict
        :return: The command result.
        :rtype: Any
        '''

        # Not implemented.
        raise NotImplementedError()
    

    # * method: verify
    def verify(self, expression: bool, error_code: str, *args):
        '''
        Verify an expression and raise an error if it is false.

        :param expression: The expression to verify.
        :type expression: bool
        :param error_code: The error code.
        :type error_code: str
        :param args: Additional error arguments.
        :type args: tuple
        '''

        # Verify the expression.
        try:
            assert expression
        except AssertionError:
            raise TiferetError(
                error_code,
                *args
            )
        

# ** command: create_model_object
class CreateModelObject(ServiceCommand):
    '''
    A command to create a model object.
    '''

    # * method: execute
    def execute(self, module_path: str, class_name: str, **kwargs) -> Any:
        '''
        Execute the create model object command.

        :param module_path: The module path.
        :type module_path: str
        :param class_name: The class name.
        :type class_name: str
        :param data: The data to pass to the model object.
        :type data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of the command.
        :rtype: Any
        '''

        # Import the class type.
        model_type = import_dependency(
            module_path=module_path,
            class_name=class_name
        )

        # Create the model object.
        return ModelObject.new(
            model_type,
            **kwargs
        )
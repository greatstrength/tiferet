# *** imports

# ** core
from typing import List, Dict, Any
from abc import abstractmethod

# ** app
from .settings import *


# *** contracts

# ** contract: error_message
class ErrorMessage(ModelContract):
    '''
    Contract for an error message translation.
    '''

    # * attribute: lang
    lang: str

    # * attribute: text
    text: str

    # * method: format
    @abstractmethod
    def format(self, *args) -> str:
        '''
        Format the error message text with provided arguments.

        :param args: The arguments to format the error message text.
        :type args: tuple
        :return: The formatted error message text.
        :rtype: str
        '''
        raise NotImplementedError('The format method must be implemented by the error message.')


# ** contract: error
class Error(ModelContract):
    '''
    Contract for an error object with multilingual messages.
    '''

    # * attribute: id
    id: str

    # * attribute: name
    name: str

    # * attribute: error_code
    error_code: str

    # * attribute: message
    message: List[ErrorMessage]

    # * method: format_message
    @abstractmethod
    def format_message(self, lang: str = 'en_US', *args) -> str:
        '''
        Format the error message for a specified language.

        :param lang: The language of the error message text (default: en_US).
        :type lang: str
        :param args: The format arguments for the error message text.
        :type args: tuple
        :return: The formatted error message text.
        :rtype: str
        '''
        raise NotImplementedError('The format_message method must be implemented by the error.')

    # * method: format_response
    @abstractmethod
    def format_response(self, lang: str = 'en_US', *args, **kwargs) -> Dict[str, Any]:
        '''
        Generate a formatted error response for a specified language.

        :param lang: The language of the error message text (default: en_US).
        :type lang: str
        :param args: The format arguments for the error message text.
        :type args: tuple
        :param kwargs: Additional keyword arguments for the response.
        :type kwargs: dict
        :return: The formatted error response.
        :rtype: Dict[str, Any]
        '''
        raise NotImplementedError('The format_response method must be implemented by the error.')

    # * method: set_message
    @abstractmethod
    def set_message(self, lang: str, text: str) -> None:
        '''
        Set or update the error message text for a specified language.

        :param lang: The language of the error message text.
        :type lang: str
        :param text: The error message text.
        :type text: str
        '''
        raise NotImplementedError('The set_message method must be implemented by the error.')


# ** contract: error_repository
class ErrorRepository(Repository):
    '''
    Contract for an error repository to manage error objects.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str, **kwargs) -> bool:
        '''
        Check if the error exists.

        :param id: The error id.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Whether the error exists.
        :rtype: bool
        '''
        raise NotImplementedError('The exists method must be implemented by the error repository.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> Error:
        '''
        Get an error object by its ID.

        :param id: The error id.
        :type id: str
        :return: The error object.
        :rtype: Error
        '''
        raise NotImplementedError('The get method must be implemented by the error repository.')

    # * method: list
    @abstractmethod
    def list(self) -> List[Error]:
        '''
        List all error objects.

        :return: The list of error objects.
        :rtype: List[Error]
        '''
        raise NotImplementedError('The list method must be implemented by the error repository.')

    # * method: save
    @abstractmethod
    def save(self, error: Error) -> None:
        '''
        Save the error.

        :param error: The error.
        :type error: Error
        '''
        raise NotImplementedError('The save method must be implemented by the error repository.')
    

# ** contract: error_service
class ErrorService(Service):
    '''
    Contract for an error service to handle error operations.
    '''

    # * method: load_errors
    @abstractmethod
    def load_errors(self, configured_errors: List[Error] = []) -> List[Error]:
        '''
        Load errors by their codes.

        :param configured_errors: The list of hard-coded errors to load.
        :type configured_errors: List[Error]
        :return: The list of loaded errors.
        :rtype: List[Error]
        '''
        raise NotImplementedError('The load_errors method must be implemented by the error service.')

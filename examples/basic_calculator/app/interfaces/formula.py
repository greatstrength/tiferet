# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** app
from tiferet.interfaces import Service
from ..mappers.formula import FormulaAggregate

# *** interfaces

# ** interface: formula_service
class FormulaService(Service):
    '''
    Service interface for managing saved formulas.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, id: str) -> bool:
        '''
        Check if a formula exists by ID.

        :param id: The formula identifier.
        :type id: str
        :return: True if the formula exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for FormulaService.')

    # * method: get
    @abstractmethod
    def get(self, id: str) -> FormulaAggregate | None:
        '''
        Retrieve a formula by ID.

        :param id: The formula identifier.
        :type id: str
        :return: The formula aggregate or None if not found.
        :rtype: FormulaAggregate | None
        '''
        raise NotImplementedError('get method is required for FormulaService.')

    # * method: list
    @abstractmethod
    def list(self) -> List[FormulaAggregate]:
        '''
        List all formulas.

        :return: A list of formula aggregates.
        :rtype: List[FormulaAggregate]
        '''
        raise NotImplementedError('list method is required for FormulaService.')

    # * method: save
    @abstractmethod
    def save(self, formula: FormulaAggregate) -> None:
        '''
        Save or update a formula.

        :param formula: The formula aggregate to save.
        :type formula: FormulaAggregate
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for FormulaService.')

    # * method: delete
    @abstractmethod
    def delete(self, id: str) -> None:
        '''
        Delete a formula by ID. This operation should be idempotent.

        :param id: The formula identifier.
        :type id: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for FormulaService.')

# *** imports

# ** core
from pathlib import Path
from typing import List

# ** app
from tiferet.repos.settings import ConfigurationRepository
from ..interfaces.formula import FormulaService
from ..mappers.formula import FormulaAggregate, FormulaConfigObject

# *** repos

# ** repo: formula_config_repository
class FormulaConfigRepository(FormulaService, ConfigurationRepository):
    '''
    The formula configuration repository, persisting formulas to a YAML/JSON
    configuration file under the ``formulas`` root node.
    '''

    # * init
    def __init__(self, formula_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the formula configuration repository.

        :param formula_config: The configuration file path.
        :type formula_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=formula_config, encoding=encoding)

    # * method: _load_full
    def _load_full(self) -> dict:
        '''
        Load the full configuration mapping, tolerating a missing file.

        :return: The full configuration data, or an empty dict.
        :rtype: dict
        '''

        # Return an empty mapping when the configuration file does not exist yet.
        if not Path(self.config_file).exists():
            return {}

        # Load and return the full configuration data.
        return self._load() or {}

    # * method: _load_formulas
    def _load_formulas(self) -> dict:
        '''
        Load the ``formulas`` mapping, tolerating a missing file or node.

        :return: The formulas mapping keyed by formula id.
        :rtype: dict
        '''

        # Return the formulas node, defaulting to an empty mapping.
        return (self._load_full().get('formulas') or {})

    # * method: exists
    def exists(self, id: str) -> bool:
        '''
        Check if a formula exists by ID.

        :param id: The formula identifier.
        :type id: str
        :return: True if the formula exists, otherwise False.
        :rtype: bool
        '''

        # Return whether the formula id exists in the mapping.
        return id in self._load_formulas()

    # * method: get
    def get(self, id: str) -> FormulaAggregate | None:
        '''
        Retrieve a formula by ID.

        :param id: The formula identifier.
        :type id: str
        :return: The formula aggregate or None if not found.
        :rtype: FormulaAggregate | None
        '''

        # Load the specific formula data from the configuration file.
        formula_data = self._load_formulas().get(id)

        # If no data is found, return None.
        if not formula_data:
            return None

        # Map the data to a FormulaAggregate and return it.
        return FormulaConfigObject.model_validate(
            {**formula_data, 'id': id}
        ).map()

    # * method: list
    def list(self) -> List[FormulaAggregate]:
        '''
        List all formulas.

        :return: A list of formula aggregates.
        :rtype: List[FormulaAggregate]
        '''

        # Map each formula entry to a FormulaAggregate.
        return [
            FormulaConfigObject.model_validate(
                {**formula_data, 'id': formula_id}
            ).map()
            for formula_id, formula_data in self._load_formulas().items()
        ]

    # * method: save
    def save(self, formula: FormulaAggregate) -> None:
        '''
        Save or update a formula.

        :param formula: The formula aggregate to save.
        :type formula: FormulaAggregate
        :return: None
        :rtype: None
        '''

        # Convert the formula model to configuration data.
        formula_data = FormulaConfigObject.from_model(formula)

        # Load the full configuration file.
        full_data = self._load_full()

        # Update or insert the formula entry.
        full_data.setdefault('formulas', {})[formula.id] = formula_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(data=full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''
        Delete a formula by ID. This operation is idempotent.

        :param id: The formula identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = self._load_full()

        # Remove the formula entry if it exists (idempotent).
        full_data.get('formulas', {}).pop(id, None)

        # Persist the updated configuration file.
        self._save(data=full_data)

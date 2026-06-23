# *** imports

# ** core
import re
from typing import Any, List

# ** infra
from pydantic import Field, model_validator

# ** app
from tiferet import DomainObject

# *** models

# ** model: formula
class Formula(DomainObject):
    '''
    A saved, variablized calculator formula (e.g. ``width * height``).
    '''

    # * attribute: id
    id: str = Field(..., description='The unique identifier of the formula.')

    # * attribute: name
    name: str = Field(..., description='The human-readable name of the formula.')

    # * attribute: expression
    expression: str = Field(..., description='The arithmetic expression using named variables.')

    # * attribute: variables
    variables: List[str] = Field(default_factory=list, description='The named variables the expression depends on.')

    # * attribute: description
    description: str | None = Field(default=None, description='An optional description of the formula.')

    # * method: _derive_fields (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_fields(cls, data: Any) -> Any:
        '''
        Derive ``id`` from ``name`` and infer ``variables`` from the
        ``expression`` identifiers when they are not explicitly provided.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The (possibly augmented) input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs; pass other shapes through unchanged.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Derive a snake_case id from the name when id is missing.
        if not data.get('id') and data.get('name'):
            data['id'] = str(data['name']).strip().lower().replace(' ', '_')

        # Infer variables from the expression identifiers when none are given.
        if not data.get('variables') and data.get('expression'):
            identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', str(data['expression']))
            data['variables'] = list(dict.fromkeys(identifiers))

        # Return the (possibly augmented) input data.
        return data

    # * method: display
    def display(self) -> str:
        '''
        Render a friendly, human-readable summary of the formula.

        :return: A single-line description of the formula.
        :rtype: str
        '''

        # Build the base "name: expression" summary.
        summary = f'{self.name}: {self.expression}'

        # Append the variable list when present.
        if self.variables:
            summary += f" (variables: {', '.join(self.variables)})"

        # Return the rendered summary.
        return summary

    # * method: __str__
    def __str__(self) -> str:
        '''
        Return the friendly display string for the formula.

        :return: The human-readable formula summary.
        :rtype: str
        '''

        # Delegate to the display method.
        return self.display()

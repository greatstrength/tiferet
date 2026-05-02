"""Tiferet Feature Domain Models"""

# *** imports

# ** core
from typing import Any, Dict, List, Literal

# ** infra
from pydantic import Field, model_validator

# ** app
from .settings import DomainObject

# *** models

# ** model: feature_step
class FeatureStep(DomainObject):
    '''
    A base step in a feature workflow.
    '''

    # * attribute: type
    type: Literal['event'] = Field(
        default='event',
        description='The type of the feature step.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the feature step.',
    )

# ** model: feature_event
class FeatureEvent(FeatureStep):
    '''
    A feature event step that executes a domain event from the container.
    '''

    # * attribute: service_id
    service_id: str = Field(
        ...,
        description='The service configuration ID for the feature event.',
    )

    # * attribute: flags
    flags: List[str] = Field(
        default_factory=list,
        description='List of feature flags that activate this event.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='The custom parameters for the feature event.',
    )

    # * attribute: return_to_data (obsolete)
    return_to_data: bool = Field(
        default=False,
        description='Whether to return the feature event result to the feature data context.',
    )

    # * attribute: data_key
    data_key: str | None = Field(
        default=None,
        description='The data key to store the feature event result in if Return to Data is True.',
    )

    # * attribute: pass_on_error
    pass_on_error: bool = Field(
        default=False,
        description='Whether to pass on the error if the feature event fails.',
    )

# ** model: feature
class Feature(DomainObject):
    '''
    A feature object.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier of the feature.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the feature.',
    )

    # * attribute: flags
    flags: List[str] = Field(
        default_factory=list,
        description='List of feature flags that activate this entire feature.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='The description of the feature.',
    )

    # * attribute: group_id
    group_id: str = Field(
        ...,
        description='The context group identifier for the feature.',
    )

    # * attribute: feature_key
    feature_key: str = Field(
        ...,
        description='The key of the feature.',
    )

    # * attribute: steps
    steps: List[FeatureEvent] = Field(
        default_factory=list,
        description='The step workflow for the feature.',
    )

    # * attribute: log_params
    log_params: Dict[str, str] = Field(
        default_factory=dict,
        description='The parameters to log for the feature.',
    )

    # * method: _derive_keys (validator)
    @model_validator(mode='before')
    @classmethod
    def _derive_keys(cls, data: Any) -> Any:
        '''
        Derive ``id``, ``group_id``, ``feature_key``, and ``description`` from
        whichever inputs are provided so callers may supply any consistent subset.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The (possibly augmented) input data.
        :rtype: Any
        '''

        # Only mutate dict-shaped inputs; pass other shapes through unchanged.
        if not isinstance(data, dict):
            return data
        data = dict(data)

        # Derive group_id and feature_key from id when id is dotted.
        if (
            data.get('id')
            and '.' in str(data['id'])
            and (not data.get('group_id') or not data.get('feature_key'))
        ):
            group_id, feature_key = str(data['id']).split('.', 1)
            data.setdefault('group_id', group_id)
            data.setdefault('feature_key', feature_key)

        # Derive feature_key from name (snake-case) when missing.
        if data.get('name') and not data.get('feature_key'):
            data['feature_key'] = str(data['name']).lower().replace(' ', '_')

        # Derive id from group_id and feature_key when missing.
        if not data.get('id') and data.get('group_id') and data.get('feature_key'):
            data['id'] = f"{data['group_id']}.{data['feature_key']}"

        # Default description to name when missing.
        if data.get('name') and not data.get('description'):
            data['description'] = data['name']

        # Return the (possibly augmented) input data.
        return data

    # * method: get_step
    def get_step(self, position: int) -> FeatureStep | None:
        '''
        Get the feature step at the given position, or None if the
        index is out of range or invalid.

        :param position: The index of the step to retrieve.
        :type position: int
        :return: The FeatureStep at the position, or None.
        :rtype: FeatureStep | None
        '''

        # Attempt to retrieve the step at the specified index, returning
        # None if the index is out of range or invalid.
        try:
            return self.steps[position]
        except (IndexError, TypeError):
            return None

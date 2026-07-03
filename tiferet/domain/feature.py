"""Tiferet Feature Domain Models"""

# *** imports

# ** core
from typing import Any, Dict, List, Literal, Optional, Tuple, Type

# ** infra
from pydantic import ConfigDict, Field, ValidationError, create_model, model_validator

# ** app
from .settings import DomainObject
from .. import assets as a
from ..assets import TiferetError

# *** models

# ** model: feature_step
class FeatureStep(DomainObject):
    '''
    A base step in a feature workflow.
    '''

    # * attribute: type
    type: Literal['event'] = Field(default='event', description='The type of the feature step.')

    # * attribute: name
    name: str = Field(..., description='The name of the feature step.')

# ** model: event_feature_step
class EventFeatureStep(FeatureStep):
    '''
    An event feature step that executes a domain event from the container.
    '''

    # * attribute: service_id
    service_id: str = Field(..., description='The service registration ID for the event feature step.')

    # * attribute: flags
    flags: List[str] = Field(default_factory=list, description='List of feature flags that activate this event feature step.')

    # * attribute: parameters
    parameters: Dict[str, str] = Field(default_factory=dict, description='The custom parameters for the event feature step.')

    # * attribute: return_to_data (obsolete)
    return_to_data: bool = Field(default=False, description='Whether to return the event feature step result to the feature data context.')

    # * attribute: data_key
    data_key: str | None = Field(default=None, description='The data key to store the event feature step result in if Return to Data is True.')

    # * attribute: pass_on_error
    pass_on_error: bool = Field(default=False, description='Whether to pass on the error if the event feature step fails.')

    # * attribute: condition
    condition: str | None = Field(
        default=None,
        description='Optional boolean expression evaluated against request data. Step executes only when the expression resolves to True. When None, the step always executes.',
    )

    # * attribute: middleware
    middleware: List[str] = Field(
        default_factory=list,
        description='Ordered list of middleware service IDs applied to this step. Outermost wrapper first.',
    )

# ** model: parameter_specification
class ParameterSpecification(DomainObject):
    '''
    A value object describing one expected request parameter, including its
    declared type, requiredness, default, and validation constraints.
    '''

    # * attribute: name
    name: str = Field(..., description='The name of the request parameter.')

    # * attribute: type
    type: Literal['str', 'int', 'float', 'bool', 'list', 'dict'] = Field(
        default='str',
        description='The declared type of the parameter.',
    )

    # * attribute: required
    required: bool = Field(default=True, description='Whether the parameter is required.')

    # * attribute: default
    default: Any | None = Field(default=None, description='The default value applied when the parameter is absent.')

    # * attribute: description
    description: str | None = Field(default=None, description='A human-readable description of the parameter.')

    # * attribute: minimum
    minimum: float | None = Field(default=None, description='Inclusive lower bound for numeric values (maps to ge).')

    # * attribute: maximum
    maximum: float | None = Field(default=None, description='Inclusive upper bound for numeric values (maps to le).')

    # * attribute: min_length
    min_length: int | None = Field(default=None, description='Minimum length for string or list values.')

    # * attribute: max_length
    max_length: int | None = Field(default=None, description='Maximum length for string or list values.')

    # * attribute: pattern
    pattern: str | None = Field(default=None, description='Regex pattern the value must match.')

    # * attribute: choices
    choices: List[Any] | None = Field(default=None, description='Enumerated set of valid values.')

    # * method: get_type
    def get_type(self) -> Type:
        '''
        Map the declared type string to a Python type.

        :return: The corresponding Python type.
        :rtype: type
        '''

        # Map the supported type strings to Python types.
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
        }

        # Return the mapped type, defaulting to str.
        return type_map.get(self.type, str)

    # * method: field_definition
    def field_definition(self) -> Tuple[Any, Any]:
        '''
        Build the ``(annotation, default)`` pair consumed by
        ``pydantic.create_model``, applying constraints via ``Field`` and using
        ``Literal`` when ``choices`` is present.

        :return: The annotation and field-default pair.
        :rtype: Tuple[Any, Any]
        '''

        # Resolve the base annotation, preferring a Literal of the choices.
        annotation = Literal[tuple(self.choices)] if self.choices else self.get_type()

        # A parameter is effectively required only when flagged required with no default.
        effective_required = self.required and self.default is None

        # Optional parameters must also accept None.
        if not effective_required:
            annotation = Optional[annotation]

        # Translate friendly constraint keys into pydantic Field keywords.
        constraints: Dict[str, Any] = {}
        if self.minimum is not None:
            constraints['ge'] = self.minimum
        if self.maximum is not None:
            constraints['le'] = self.maximum
        if self.min_length is not None:
            constraints['min_length'] = self.min_length
        if self.max_length is not None:
            constraints['max_length'] = self.max_length
        if self.pattern is not None:
            constraints['pattern'] = self.pattern
        if self.description is not None:
            constraints['description'] = self.description

        # Required fields use Ellipsis; optional fields use the configured default.
        default = ... if effective_required else self.default

        # Return the annotation/field pair for dynamic model construction.
        return (annotation, Field(default, **constraints))

# ** model: request_specification
class RequestSpecification(DomainObject):
    '''
    A feature-level Specification object that dynamically reconstitutes the
    request configuration as a Pydantic model to validate and coerce request
    data, failing fast with a single aggregated error.
    '''

    # * attribute: parameters
    parameters: List[ParameterSpecification] = Field(
        default_factory=list,
        description='The expected request parameters.',
    )

    # * method: normalize_parameters (validator)
    @model_validator(mode='before')
    @classmethod
    def normalize_parameters(cls, data: Any) -> Any:
        '''
        Normalize ergonomic config forms into the canonical ``parameters`` list.

        Accepts the canonical ``{'parameters': [...]}`` form, the shorthand
        keyed form ``{'a': 'int'}``, and the expanded keyed form
        ``{'b': {'type': 'float', 'required': False}}``.

        :param data: The raw input data passed to the model.
        :type data: Any
        :return: The canonicalized input data.
        :rtype: Any
        '''

        # Only normalize dict-shaped inputs; pass other shapes through unchanged.
        if not isinstance(data, dict):
            return data

        # Treat a list-valued ``parameters`` key as already canonical. The keyed
        # form only ever maps a name to a type string or a spec dict, so a list
        # here unambiguously indicates the canonical ``{'parameters': [...]}``
        # shape. This lets a feature declare a request parameter literally named
        # ``parameters`` (e.g. service.add) without colliding with canonical form.
        if isinstance(data.get('parameters'), list):
            return data

        # Expand each keyed entry into a parameter specification dict.
        parameters: List[Dict[str, Any]] = []
        for name, spec in data.items():
            if isinstance(spec, str):
                parameters.append({'name': name, 'type': spec, 'required': True})
            elif isinstance(spec, dict):
                parameters.append({'name': name, **spec})

        # Return the canonical parameters mapping.
        return {'parameters': parameters}

    # * method: build_model
    def build_model(self, model_name: str = 'RequestModel') -> type:
        '''
        Dynamically create a standalone Pydantic model from the parameter
        specifications.

        The model is a plain ``pydantic.BaseModel`` (not a ``DomainObject``) so
        ``coerce_numbers_to_str`` does not corrupt numeric coercion.

        :param model_name: The name for the generated model.
        :type model_name: str
        :return: The dynamically built Pydantic model class.
        :rtype: type
        '''

        # Build the field definitions from each parameter specification.
        field_definitions = {
            param.name: param.field_definition()
            for param in self.parameters
        }

        # Create a standalone model that ignores unspecified extra keys.
        return create_model(
            model_name,
            __config__=ConfigDict(extra='ignore'),
            **field_definitions,
        )

    # * method: validate
    def validate(self, data: Dict[str, Any], feature_id: str = None) -> Dict[str, Any]:
        '''
        Validate and coerce ``data`` against the schema, returning the original
        request data merged with coerced schema-covered fields and defaults.
        Unspecified extra request keys are preserved.

        :param data: The request data to validate.
        :type data: Dict[str, Any]
        :param feature_id: The feature id used for error context.
        :type feature_id: str
        :return: The merged, coerced request data.
        :rtype: Dict[str, Any]
        '''

        # Build the dynamic validation model.
        model_cls = self.build_model()

        # Validate and coerce the request data, aggregating all field errors.
        try:
            validated = model_cls(**(data or {}))

        # Convert Pydantic validation errors into a single structured error.
        except ValidationError as error:
            violations = [
                {
                    'field': '.'.join(str(loc) for loc in err.get('loc', ())),
                    'type': err.get('type'),
                    'message': err.get('msg'),
                }
                for err in error.errors()
            ]
            raise TiferetError(
                a.const.REQUEST_VALIDATION_FAILED_ID,
                f'Request validation failed for feature {feature_id}: {violations}.',
                feature_id=feature_id,
                violations=violations,
            )

        # Merge coerced schema fields and defaults over the original data.
        return {**(data or {}), **validated.model_dump()}

    # * method: is_satisfied_by
    def is_satisfied_by(self, data: Dict[str, Any]) -> bool:
        '''
        Report whether ``data`` satisfies the specification.

        :param data: The request data to test.
        :type data: Dict[str, Any]
        :return: True when the data validates, otherwise False.
        :rtype: bool
        '''

        # Attempt validation, treating a validation error as not satisfied.
        try:
            self.validate(data)
            return True
        except TiferetError:
            return False

# ** model: feature
class Feature(DomainObject):
    '''
    A feature object.
    '''

    # * attribute: id
    id: str = Field(..., description='The unique identifier of the feature.')

    # * attribute: name
    name: str = Field(..., description='The name of the feature.')

    # * attribute: flags
    flags: List[str] = Field(default_factory=list, description='List of feature flags that activate this entire feature.')

    # * attribute: description
    description: str | None = Field(default=None, description='The description of the feature.')

    # * attribute: group_id
    group_id: str = Field(..., description='The context group identifier for the feature.')

    # * attribute: feature_key
    feature_key: str = Field(..., description='The key of the feature.')

    # * attribute: steps
    steps: List[EventFeatureStep] = Field(default_factory=list, description='The step workflow for the feature.')

    # * attribute: middleware
    middleware: List[str] = Field(
        default_factory=list,
        description='Ordered list of middleware service IDs applied to every step in this feature. Outermost wrapper first.',
    )

    # * attribute: is_async
    is_async: bool = Field(
        default=False,
        description='Whether the feature executes its steps asynchronously. Selects the AsyncFeatureContext when True.',
    )

    # * attribute: log_params
    log_params: Dict[str, str] = Field(default_factory=dict, description='The parameters to log for the feature.')

    # * attribute: params_schema
    params_schema: RequestSpecification | None = Field(
        default=None,
        description='Optional feature-level request validation schema applied to request data before step execution.',
    )

    # * method: derive_keys (validator)
    @model_validator(mode='before')
    @classmethod
    def derive_keys(cls, data: Any) -> Any:
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

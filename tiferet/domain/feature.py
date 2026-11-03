"""Tiferet Feature Domain Models"""

# *** imports

# ** core
from collections.abc import Mapping
from typing import Any, Dict, List, Literal, Optional, Tuple

# ** infra
from pydantic import ConfigDict, Field, ValidationError, create_model, model_validator

# ** app
from .core import (
    INVALID_MODEL_VALUE_ID,
    DomainObject,
    ModelError,
)

# *** models

# ** model: feature_step
# >> see: @guides/domain/feature.md#featurestep
class FeatureStep(DomainObject):
    '''
    The base shape every step in a feature workflow shares, carrying a
    ``type`` discriminator so the workflow can grow new step kinds (e.g. a
    loop or branch) without breaking existing ones.
    '''

    # * attribute: type
    type: Literal['event'] = Field(default='event', description='The type of the feature step.')

    # * attribute: name
    name: str = Field(..., description='The name of the feature step.')

# ** model: event_feature_step
# >> see: @guides/domain/feature.md#eventfeaturestep
class EventFeatureStep(FeatureStep):
    '''
    A single unit of work in a feature workflow — a resolvable domain event
    plus the flags, parameters, result routing, and error-handling
    configuration needed to execute it as one step of a larger pipeline.
    '''

    # * attribute: service_id
    service_id: str = Field(..., description='The service registration ID for the event feature step.')

    # * attribute: flags
    flags: List[str] = Field(default_factory=list, description='List of feature flags that activate this event feature step.')

    # * attribute: parameters
    parameters: Dict[str, str] = Field(default_factory=dict, description='The custom parameters for the event feature step.')

    # * attribute: data_key
    data_key: str | None = Field(default=None, description='The key under which to store the step result in the request data. When None, the step result is set as the top-level response.')

    # * attribute: pass_on_error
    pass_on_error: bool = Field(default=False, description='Whether to pass on the error if the event feature step fails.')

    # * attribute: is_async
    is_async: bool = Field(
        default=False,
        description='Whether this step executes asynchronously. Only evaluated when the parent Feature.is_async is False; when the feature is async the entire step loop runs via run_coroutine(_execute_async) regardless of this flag.',
    )

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
# >> see: @guides/domain/feature.md#parameterspecification
class ParameterSpecification(DomainObject):
    '''
    A value object describing one expected request parameter, including its
    declared type, requiredness, default, and validation constraints.

    The noun owns the three faces of one declared parameter: the config map
    entry (shorthand ``a: int`` or an expanded mapping keyed by name), the
    ordered runtime list keyed by ``name``, and the ``(annotation, Field)``
    field definition consumed by ``pydantic.create_model``.
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
    # >> see: @guides/domain/feature.md#parameterspecification-get-type
    def get_type(self) -> type:
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
    # >> see: @guides/domain/feature.md#parameterspecification-field-definition
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

    # * method: from_config_entry (classmethod)
    # >> see: @guides/domain/feature.md#parameterspecification-from-config-entry
    @classmethod
    def from_config_entry(cls, name: str, value: Any) -> 'ParameterSpecification':
        '''
        Read one config-map entry as a parameter specification.

        A type string is shorthand: that name, that type, ``required=True``,
        and every other field at its default. A mapping is the expanded face,
        keyed by ``name``; an inner ``name`` equal to the key is dropped. An
        unknown type string fails as a Pydantic ``ValidationError``.

        :param name: The config-map key, which is the parameter name.
        :type name: str
        :param value: The config-map value: a type string or a mapping.
        :type value: Any
        :return: The parameter specification.
        :rtype: ParameterSpecification
        '''

        # A type string is shorthand for a required parameter of that type.
        if isinstance(value, str):
            return cls(name=name, type=value, required=True)

        # Any other non-mapping value is not a config entry.
        if not isinstance(value, Mapping):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Parameter {name!r} config value must be a type string or a mapping, not {type(value).__name__}.',
            )

        # The map key is the name; an inner name must agree with it.
        fields = dict(value)
        if 'name' in fields:
            inner_name = fields.pop('name')
            if inner_name != name:
                ModelError.raise_error(
                    INVALID_MODEL_VALUE_ID,
                    message=f'Parameter {name!r} config value names a different parameter: {inner_name!r}.',
                )

        # Build the expanded parameter specification.
        return cls(name=name, **fields)

    # * method: to_config_value
    # >> see: @guides/domain/feature.md#parameterspecification-to-config-value
    def to_config_value(self) -> str | Dict[str, Any]:
        '''
        Write this parameter as its config-map value, without ``name``.

        The type string is emitted only when the parameter is required, has no
        default, and has no description or constraint. Otherwise a mapping is
        emitted: ``type`` first, then only the fields that differ, in field
        order. Absence is ``is not None``, so a default of ``0`` or ``False``
        is written.

        :return: The type string, or the expanded mapping.
        :rtype: str | Dict[str, Any]
        '''

        # Collect the fields that differ from the shorthand defaults, in order.
        extras: Dict[str, Any] = {}
        if self.default is not None:
            extras['default'] = self.default
        if not self.required:
            extras['required'] = self.required
        for key in ('description', 'minimum', 'maximum', 'min_length', 'max_length', 'pattern', 'choices'):
            item = getattr(self, key)
            if item is not None:
                extras[key] = item

        # Emit shorthand when only the type is meaningful.
        if not extras:
            return self.type

        # Emit the expanded mapping with the type first.
        return {'type': self.type, **extras}

    # * method: from_config_map (classmethod)
    # >> see: @guides/domain/feature.md#parameterspecification-from-config-map
    @classmethod
    def from_config_map(cls, config: Any) -> List['ParameterSpecification']:
        '''
        Read a name-keyed config map as the ordered runtime list.

        Entries are read in insertion order. A key named ``parameters`` is a
        parameter name like any other.

        :param config: The name-keyed config map.
        :type config: Any
        :return: The parameter specifications, in map order.
        :rtype: List[ParameterSpecification]
        '''

        # Only a mapping is a config map.
        if not isinstance(config, Mapping):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Parameter config map must be a mapping, not {type(config).__name__}.',
            )

        # Read each entry, then key the list by name.
        return cls.keyed_by_name([
            cls.from_config_entry(name, value)
            for name, value in config.items()
        ])

    # * method: to_config_map (classmethod)
    # >> see: @guides/domain/feature.md#parameterspecification-to-config-map
    @classmethod
    def to_config_map(cls, parameters: Any) -> Dict[str, Any]:
        '''
        Write the runtime list as a name-keyed config map, in list order.

        An empty list writes an empty mapping.

        :param parameters: The parameter specifications or canonical dicts.
        :type parameters: Any
        :return: The name-keyed config map.
        :rtype: Dict[str, Any]
        '''

        # Key the list by name, then write each config value.
        return {
            param.name: param.to_config_value()
            for param in cls.keyed_by_name(parameters)
        }

    # * method: keyed_by_name (classmethod)
    # >> see: @guides/domain/feature.md#parameterspecification-keyed-by-name
    @classmethod
    def keyed_by_name(cls, parameters: Any) -> List['ParameterSpecification']:
        '''
        Return the runtime list as parameter specifications keyed by ``name``,
        in input order.

        Accepts parameter specifications or canonical dicts that include
        ``name``. It does not read shorthand or a config map. A repeated name
        is a model error, not a last-wins write.

        :param parameters: The parameter specifications or canonical dicts.
        :type parameters: Any
        :return: The parameter specifications, in input order.
        :rtype: List[ParameterSpecification]
        '''

        # A mapping is a config map, not the runtime list; do not iterate keys.
        if isinstance(parameters, Mapping) or not isinstance(parameters, (list, tuple)):
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Parameter runtime list must be a list, not {type(parameters).__name__}.',
            )

        # Build each specification, rejecting a repeated name.
        result: List[ParameterSpecification] = []
        names: set = set()
        for item in parameters:
            if isinstance(item, cls):
                param = item
            elif isinstance(item, Mapping):
                param = cls(**item)
            else:
                ModelError.raise_error(
                    INVALID_MODEL_VALUE_ID,
                    message=f'Parameter runtime list item must be a parameter specification or a mapping, not {type(item).__name__}.',
                )
            if param.name in names:
                ModelError.raise_error(
                    INVALID_MODEL_VALUE_ID,
                    message=f'Parameter {param.name!r} is declared more than once.',
                )
            names.add(param.name)
            result.append(param)

        # Return the ordered runtime list.
        return result

# ** model: request_specification
# >> see: @guides/domain/feature.md#requestspecification
class RequestSpecification(DomainObject):
    '''
    A feature's declared request contract — dynamically reconstituting its
    parameter specifications into a Pydantic model lets a feature validate
    and coerce its request data fail-fast, with a single aggregated error,
    before any step runs.
    '''

    # * attribute: parameters
    parameters: List[ParameterSpecification] = Field(
        default_factory=list,
        description='The expected request parameters.',
    )

    # * method: normalize_parameters (validator)
    # >> see: @guides/domain/feature.md#requestspecification-normalize-parameters
    @model_validator(mode='before')
    @classmethod
    def normalize_parameters(cls, data: Any) -> Any:
        '''
        Normalize ergonomic config forms into the canonical ``parameters`` list.

        Distinguishes the canonical ``{'parameters': [...]}`` form from a
        name-keyed config map (shorthand ``{'a': 'int'}`` or expanded
        ``{'b': {'type': 'float', 'required': False}}``) and delegates each to
        ``ParameterSpecification``, which owns the shorthand rule.

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
        # Other keys are kept so ``extra='forbid'`` still rejects them.
        if isinstance(data.get('parameters'), list):
            return {
                **data,
                'parameters': ParameterSpecification.keyed_by_name(data['parameters']),
            }

        # Every other dict is a name-keyed config map.
        return {'parameters': ParameterSpecification.from_config_map(data)}

    # * method: build_model
    # >> see: @guides/domain/feature.md#requestspecification-build-model
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

    # * method: coerce
    # >> see: @guides/domain/feature.md#requestspecification-coerce
    def coerce(self, data: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Validate and coerce ``data`` against the schema, returning the original
        request data merged with coerced schema-covered fields and defaults.
        Unspecified extra request keys are preserved.

        Pydantic's ``ValidationError`` propagates untouched: naming the failure
        is the orchestration layer's concern, so the domain carries no framework
        error vocabulary.

        :param data: The request data to coerce.
        :type data: Dict[str, Any]
        :return: The merged, coerced request data.
        :rtype: Dict[str, Any]
        '''

        # Build the dynamic validation model.
        model_cls = self.build_model()

        # Validate and coerce the request data, aggregating all field errors.
        validated = model_cls(**(data or {}))

        # Merge coerced schema fields and defaults over the original data.
        return {**(data or {}), **validated.model_dump()}

    # * method: is_satisfied_by
    # >> see: @guides/domain/feature.md#requestspecification-is-satisfied-by
    def is_satisfied_by(self, data: Dict[str, Any]) -> bool:
        '''
        Report whether ``data`` satisfies the specification.

        :param data: The request data to test.
        :type data: Dict[str, Any]
        :return: True when the data validates, otherwise False.
        :rtype: bool
        '''

        # Attempt coercion, treating a validation error as not satisfied.
        try:
            self.coerce(data)
            return True
        except ValidationError:
            return False

# ** model: feature
# >> see: @guides/domain/feature.md#feature
class Feature(DomainObject):
    '''
    A complete, named workflow definition — the orchestration unit that binds
    an ordered pipeline of domain-event steps (and an optional request
    schema) to a single resolvable id so a CLI command, API route, or
    scheduled job can execute it as one call.
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
    # ++ todo: when additional step types emerge (e.g. LoopStep, BranchStep), broaden to a discriminated union:
    # ++       List[Annotated[Union[EventFeatureStep, ...], Field(discriminator='type')]]
    #          Changing to List[FeatureStep] now would break Pydantic validation (extra='forbid' on DomainObject
    #          rejects EventFeatureStep-specific fields when validating dicts against the base type).
    steps: List[EventFeatureStep] = Field(default_factory=list, description='The step workflow for the feature.')

    # * attribute: middleware
    middleware: List[str] = Field(
        default_factory=list,
        description='Ordered list of middleware service IDs applied to every step in this feature. Outermost wrapper first.',
    )

    # * attribute: is_async
    is_async: bool = Field(
        default=False,
        description='Whether the feature executes its steps asynchronously. When True, execute_feature drives the full step loop via run_coroutine(_execute_async). Step-level is_async is only evaluated when this flag is False.',
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
    # >> see: @guides/domain/feature.md#feature-get-step
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

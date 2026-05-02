"""Tiferet Mapper Settings"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from pydantic import BaseModel, ConfigDict

# ** app
from ..domain.settings import DomainObject
from ..events import RaiseError, a

# *** constants

# ** constant: default_module_path
DEFAULT_MODULE_PATH = 'tiferet.contexts.app'

# ** constant: default_class_name
DEFAULT_CLASS_NAME = 'AppInterfaceContext'

# *** classes

# ** class: aggregate
class Aggregate(DomainObject):
    '''
    A mutable, validated representation of a domain aggregate.

    Aggregates inherit the strict ``extra='forbid'`` and ``validate_assignment=True``
    config from :class:`DomainObject`. Mutation goes through :meth:`set_attribute`
    for an explicit existence check, but any direct ``setattr`` will still trigger
    Pydantic field validation.
    '''

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Update an attribute on the aggregate, raising an error if it is unknown.

        :param attribute: The attribute name to update.
        :type attribute: str
        :param value: The new value to assign.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Reject unknown attribute names by raising a structured error.
        if attribute not in type(self).model_fields:
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                attribute=attribute,
            )

        # Apply the update; validate_assignment=True triggers field validation.
        setattr(self, attribute, value)

# ** class: transfer_object
class TransferObject(DomainObject):
    '''
    A representation used to serialize, deserialize, or otherwise map domain data
    to and from external formats (YAML, JSON, SQL rows, HTTP payloads, etc.).

    Transfer objects are deliberately lenient: ``extra='ignore'`` lets unknown
    incoming keys flow through without raising, and ``validate_assignment=False``
    keeps piecewise data shaping cheap. Subclasses declare a class-level
    ``_ROLES`` constant whose values are keyword-argument dictionaries forwarded
    to :meth:`pydantic.BaseModel.model_dump`, and resolve them via
    :meth:`to_primitive`. ``'to_model'`` is the canonical role used by
    :meth:`map` to produce an Aggregate; format-specific roles such as
    ``'to_data.yaml'``, ``'to_data.json'``, or ``'to_data.sql'`` are conventions
    consumers can adopt as needed.
    '''

    # * attribute: model_config
    model_config = ConfigDict(
        extra='ignore',
        populate_by_name=True,
        validate_assignment=False,
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
    )

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {}

    # * method: to_primitive
    def to_primitive(self,
            role: str | None = None,
            **overrides,
        ) -> Dict[str, Any]:
        '''
        Serialize the transfer object via ``model_dump`` using role-specific kwargs.

        :param role: Optional role key indexing into ``_ROLES``.
        :type role: str | None
        :param overrides: Additional ``model_dump`` keyword overrides.
        :type overrides: dict
        :return: The serialized primitive dictionary.
        :rtype: Dict[str, Any]
        '''

        # Default to canonical-name dumps; YAML/JSON roles opt-in to by_alias=True.
        kwargs: Dict[str, Any] = {'exclude_none': True}

        # Apply role-specific kwargs if a role is specified.
        if role and role in type(self)._ROLES:
            kwargs.update(type(self)._ROLES[role])

        # Apply caller overrides last so they win.
        kwargs.update(overrides)

        # Delegate to Pydantic's model_dump.
        return self.model_dump(**kwargs)

    # * method: map
    def map(self,
            target: type,
            **overrides,
        ) -> Aggregate:
        '''
        Map this transfer object to an aggregate type.

        :param target: The aggregate class to construct.
        :type target: type
        :param overrides: Field overrides applied after ``to_primitive('to_model')``.
        :type overrides: dict
        :return: A new aggregate instance.
        :rtype: Aggregate
        '''

        # Serialize via the to_model role and apply overrides.
        data = self.to_primitive(role='to_model')
        data.update(overrides)

        # Construct and return the aggregate.
        return target(**data)

    # * method: from_model
    @classmethod
    def from_model(cls,
            model: BaseModel,
            **overrides,
        ) -> 'TransferObject':
        '''
        Build a transfer object from an aggregate or domain object.

        :param model: The source model to copy data from.
        :type model: BaseModel
        :param overrides: Field overrides applied after the source dump.
        :type overrides: dict
        :return: A new transfer object instance.
        :rtype: TransferObject
        '''

        # Dump the source model using its canonical field names.
        data = model.model_dump(by_alias=False)

        # Apply caller overrides last so they win.
        data.update(overrides)

        # Validate and construct the transfer object.
        return cls.model_validate(data)

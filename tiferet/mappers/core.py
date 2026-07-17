"""Tiferet Mapper Settings"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from pydantic import BaseModel, ConfigDict

# ** app
from ..domain import DomainObject
from ..events import RaiseError, a

# *** constants

# ** constant: default_module_path
DEFAULT_MODULE_PATH = 'tiferet.contexts.app'

# ** constant: default_class_name
DEFAULT_CLASS_NAME = 'AppSessionContext'

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
                error_code=a.error.INVALID_MODEL_ATTRIBUTE_ID,
                attribute=attribute,
            )

        # Apply the update; validate_assignment=True triggers field validation.
        setattr(self, attribute, value)

    # * method: to_dict
    def to_dict(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize the aggregate to a dictionary, optionally applying role-specific kwargs.

        Mirrors :meth:`TransferObject.to_primitive` for consistent serialization
        across both aggregates and transfer objects.

        :param role: Optional serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to ``model_dump``.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Start with the default kwargs.
        kwargs: Dict[str, Any] = {'exclude_none': True}

        # Apply caller overrides.
        kwargs.update(overrides)

        # Delegate to Pydantic model_dump.
        return self.model_dump(**kwargs)

# ** class: transfer_object
class TransferObject(DomainObject):
    '''
    A serialization and mapping layer for domain data.

    TransferObjects use a lenient config (``extra='ignore'``, ``validate_assignment=False``)
    so that unknown or extra fields in external data sources (e.g. YAML) are silently
    dropped rather than raising validation errors.

    Subclasses declare a ``_ROLES`` ClassVar mapping role names to ``model_dump`` kwargs
    for role-based serialization via :meth:`to_primitive`.
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
    def to_primitive(self, role: str = None, **overrides) -> Dict[str, Any]:
        '''
        Serialize the transfer object to a dictionary, optionally applying role-specific kwargs.

        :param role: The serialization role to apply.
        :type role: str
        :param overrides: Additional keyword arguments passed to ``model_dump``.
        :type overrides: dict
        :return: The serialized dictionary.
        :rtype: Dict[str, Any]
        '''

        # Start with the default kwargs.
        kwargs: Dict[str, Any] = {'exclude_none': True}

        # Merge role-specific kwargs if the role is known.
        if role and role in type(self)._ROLES:
            kwargs.update(type(self)._ROLES[role])

        # Apply caller overrides last so they always win.
        kwargs.update(overrides)

        # Delegate to Pydantic model_dump.
        return self.model_dump(**kwargs)

    # * method: map
    def map(self, target: type, **overrides) -> 'Aggregate':
        '''
        Map the transfer object to an aggregate instance.

        :param target: The aggregate class to construct.
        :type target: type
        :param overrides: Additional keyword arguments merged into the data.
        :type overrides: dict
        :return: A new aggregate instance.
        :rtype: Aggregate
        '''

        # Serialize via the to_model role and merge overrides.
        data = self.to_primitive(role='to_model')
        data.update(overrides)

        # Construct the target aggregate.
        return target(**data)

    # * method: from_model
    @classmethod
    def from_model(cls, model: BaseModel, **overrides) -> 'TransferObject':
        '''
        Create a transfer object from a domain model or aggregate.

        :param model: The source model instance.
        :type model: BaseModel
        :param overrides: Additional keyword arguments that take priority.
        :type overrides: dict
        :return: A new transfer object.
        :rtype: TransferObject
        '''

        # Dump the model to a dict using canonical field names.
        data = model.model_dump(by_alias=False)

        # Apply overrides so they take priority.
        data.update(overrides)

        # Construct and return the transfer object.
        return cls.model_validate(data)

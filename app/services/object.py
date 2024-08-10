from typing import List, Dict, Any

from ..objects.object import ObjectAttribute
from ..objects.object import ObjectTypeSettings
from ..objects.object import StringSettings
from ..objects.object import DateSettings
from ..objects.object import DateTimeSettings
from ..objects.object import ListSettings
from ..objects.object import DictSettings
from ..repositories.object import ObjectRepository


def create_type_settings(type_settings: Dict[str, Any], type: str, **kwargs) -> ObjectTypeSettings:
    '''
    Create type settings for an object attribute.

    :param type_settings: The type settings.
    :type type_settings: dict
    :param type: The attribute type.
    :type type: str
    :return: The type settings.
    :rtype: ObjectTypeSettings
    '''

    # Exit if there are no type settings.
    if not type_settings:
        return type_settings

    # Set the type settings based on the attribute type.
    if type == 'str':
        type_settings = StringSettings(type_settings, strict=False)
    elif type == 'date':
        type_settings = DateSettings(type_settings, strict=False)
    elif type == 'datetime':
        type_settings = DateTimeSettings(type_settings, strict=False)
    elif type == 'list':
        type_settings = ListSettings(type_settings, strict=False)
    elif type == 'dict':
        type_settings = DictSettings(type_settings, strict=False)

    # Return none if no type settings were created.
    else:
        return None

    # Return the type settings.
    return type_settings


def create_attribute(object_id: str, type: str, type_settings: Dict[str, Any], **kwargs) -> ObjectAttribute:
    '''
    Create a new object attribute.

    :param object_id: The object ID.
    :type object_id: str
    :param type: The attribute type.
    :type type: str
    :param type_settings: The type settings.
    :type type_settings: dict
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: The new object attribute.
    :rtype: ObjectAttribute
    '''

    # Create type settings for the object attribute.
    type_settings = create_type_settings(type_settings, type)

    # Create a new object attribute.
    attribute = ObjectAttribute.new(
        object_id=object_id,
        type_settings=type_settings,
        **kwargs
    )

    # Return the new object attribute.
    return attribute


def validate_attribute(object_repo: ObjectRepository, attribute: ObjectAttribute, **kwargs):
    '''
    Validate an object attribute.

    :param object_repo: The object repository.
    :type object_repo: ObjectRepository
    :param attribute: The object attribute.
    :type attribute: ObjectAttribute
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: The validated object attribute.
    :rtype: ObjectAttribute
    '''

    # If the attribute has an type object id,
    if attribute.type_object_id:

        # Assert that the object exists or return an Object Not Found error.
        assert object_repo.exists(
            attribute.type_object_id), f'OBJECT_NOT_FOUND: {attribute.type_object_id}'

    # If the attribute has poly model object ids,
    if attribute.poly_type_object_ids:

        # For each poly model object id,
        for object_id in attribute.poly_type_object_ids:

            # Assert that the object exists or return an Object Not Found error.
            assert object_repo.exists(
                object_id), f'OBJECT_NOT_FOUND: {object_id}'

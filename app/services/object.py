from ..objects.object import ObjectAttribute
from ..repositories.object import ObjectRepository

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
        assert object_repo.exists(attribute.type_object_id), f'OBJECT_NOT_FOUND: {attribute.type_object_id}'
    
    # If the attribute has poly model object ids,
    if attribute.poly_type_object_ids:

        # For each poly model object id,
        for object_id in attribute.poly_type_object_ids:

            # Assert that the object exists or return an Object Not Found error.
            assert object_repo.exists(object_id), f'OBJECT_NOT_FOUND: {object_id}'

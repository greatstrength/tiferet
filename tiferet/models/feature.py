"""Tiferet Feature Models"""

# *** imports

# ** app
from .settings import (
    ModelObject,
    StringType,
    BooleanType,
    DictType,
    ListType,
    ModelType,
)

# *** models

# ** model: feature_command
class FeatureCommand(ModelObject):
    '''
    A command object for a feature command.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the feature handler.'
        )
    )

    # * attribute: attribute_id
    attribute_id = StringType(
        required=True,
        metadata=dict(
            description='The container attribute ID for the feature command.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType(),
        default={},
        metadata=dict(
            description='The custom parameters for the feature handler.'
        )
    )

    # * attribute: return_to_data (obsolete)
    return_to_data = BooleanType(
        default=False,
        metadata=dict(
            description='Whether to return the feature command result to the feature data context.'
        )
    )

    # * attribute: data_key
    data_key = StringType(
        metadata=dict(
            description='The data key to store the feature command result in if Return to Data is True.'
        )
    )

    # * attribute: pass_on_error
    pass_on_error = BooleanType(
        metadata=dict(
            description='Whether to pass on the error if the feature handler fails.'
        )
    )

# ** model: feature
class Feature(ModelObject):
    '''
    A feature object.
    '''

    # attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the feature.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the feature.'
        )
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the feature.'
        )
    )

    # * attribute: group_id
    group_id = StringType(
        required=True,
        metadata=dict(
            description='The context group identifier for the feature.'
        )
    )

    feature_key = StringType(
        required=True,
        metadata=dict(
            description='The key of the feature.'
        )
    )

    # * attribute: commands
    commands = ListType(
        ModelType(FeatureCommand),
        default=[],
        metadata=dict(
            description='The command handler workflow for the feature.'
        )
    )

    # * attribute: log_params
    log_params = DictType(
        StringType(),
        default={},
        metadata=dict(
            description='The parameters to log for the feature.'
        )
    )

    # * method: new
    @staticmethod
    def new(name: str, group_id: str, feature_key: str = None, id: str = None, description: str = None, **kwargs) -> 'Feature':
        '''Initializes a new Feature object.

        :param name: The name of the feature.
        :type name: str
        :param group_id: The context group identifier of the feature.
        :type group_id: str
        :param feature_key: The key of the feature.
        :type feature_key: str
        :param id: The identifier of the feature.
        :type id: str
        :param description: The description of the feature.
        :type description: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new Feature object.
        '''

        # Set the feature key as the snake case of the name if not provided.
        if not feature_key:
            feature_key = name.lower().replace(' ', '_')

        # Feature ID is the group ID and feature key separated by a period.
        if not id:
            id = f'{group_id}.{feature_key}'

        # Set the description as the name if not provided.
        if not description:
            description = name

        # Create and return a new Feature object.
        return ModelObject.new(
            Feature,
            id=id,
            name=name,
            group_id=group_id,
            feature_key=feature_key,
            description=description,
            **kwargs
        )

    # * method: add_command
    def add_command(
        self,
        name: str,
        attribute_id: str,
        parameters: dict | None = None,
        data_key: str | None = None,
        pass_on_error: bool = False,
        position: int | None = None,
    ) -> FeatureCommand:
        '''
        Add a feature command using raw attributes.

        :param name: Command name.
        :type name: str
        :param attribute_id: Container attribute ID.
        :type attribute_id: str
        :param parameters: Optional parameters dictionary.
        :type parameters: dict | None
        :param data_key: Optional result data key.
        :type data_key: str | None
        :param pass_on_error: Whether to pass on errors from this command.
        :type pass_on_error: bool
        :param position: Insertion position (None to append).
        :type position: int | None
        :return: Created FeatureCommand instance.
        :rtype: FeatureCommand
        '''

        # Create the feature command from raw attributes.
        command = ModelObject.new(
            FeatureCommand,
            name=name,
            attribute_id=attribute_id,
            parameters=parameters or {},
            data_key=data_key,
            pass_on_error=pass_on_error,
        )

        # Add the feature command to the feature.
        if position is not None:
            self.commands.insert(position, command)
        else:
            self.commands.append(command)

        return command

    # * method: rename
    def rename(self, name: str) -> None:
        '''
        Update the display name of the feature.

        :param name: The new name.
        :type name: str
        '''

        self.name = name

    # * method: set_description
    def set_description(self, description: str | None) -> None:
        '''
        Update or clear the feature description.

        :param description: The new description, or None to clear.
        :type description: str | None
        '''

        self.description = description

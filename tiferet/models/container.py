"""Tiferet Container Models"""

# *** imports

# ** app
from .settings import (
    ModelObject,
    StringType,
    DictType,
    ListType,
    ModelType,
)
from ..commands import ImportDependency

# *** models

# ** model: flagged_dependency
class FlaggedDependency(ModelObject):
    '''
    A flagged container dependency object.
    '''

     # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path.'
        )
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name.'
        )
    )

    # * attribute: flag
    flag = StringType(
        required=True,
        metadata=dict(
            description='The flag for the container dependency.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The container dependency parameters.'
        )
    )

    # * method: set_parameters
    def set_parameters(self, parameters=None):
        '''
        Update the parameters dictionary for this flagged dependency.

        :param parameters: New parameters, or None to clear all.
                           Keys with None values are removed.
        :type parameters: Dict[str, Any] | None
        '''

        # If parameters is None, clear all.
        if parameters is None:
            self.parameters = {}
        else:
            # Merge existing parameters with new ones (new values win).
            merged = dict(self.parameters or {})
            merged.update(parameters)

            # Filter out keys where the value is None.
            self.parameters = {
                k: v for k, v in merged.items() if v is not None
            }

# ** model: container_attribute
class ContainerAttribute(ModelObject):
    '''
    An attribute that defines container injectior behavior.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier for the container attribute.'
        )
    )

    # * attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the container attribute.'
        )
    )

    # * attribute: module_path
    module_path = StringType(
        metadata=dict(
            description='The non-flagged module path for the container attribute.'
        )
    )

    # * attribute: class_name
    class_name = StringType(
        metadata=dict(
            description='The non-flagged class name for the container attribute.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The container attribute parameters.'
        )
    )

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(FlaggedDependency),
        default=[],
        metadata=dict(
            description='The container attribute dependencies.'
        )
    )

    # * method: set_default_type
    def set_default_type(
        self,
        module_path=None,
        class_name=None,
        parameters=None,
    ):
        '''
        Update the default type and parameters for this container attribute.

        :param module_path: New module path (or None to clear).
        :type module_path: Optional[str]
        :param class_name: New class name (or None to clear).
        :type class_name: Optional[str]
        :param parameters: New parameters dict (or None to clear all).
        :type parameters: Optional[Dict[str, Any]]
        '''

        # If both type fields are None, clear default type.
        if module_path is None and class_name is None:
            self.module_path = None
            self.class_name = None
            self.parameters = {}
            
        # Otherwise, set them to whatever is provided.
        else:
            self.module_path = module_path
            self.class_name = class_name

        # Update parameters: if parameters is None, clear all; otherwise replace.
        if parameters is None:
            self.parameters = {}
        else:
            self.parameters = {k: v for k, v in parameters.items() if v != None}

    # * method: get_dependency
    def get_dependency(self, *flags) -> FlaggedDependency:
        '''
        Gets a flagged container dependency by flag.

        :param flags: The flags for the flagged container dependency.
        :type flags: Tuple[str, ...]
        :return: The flagged container dependency that matches the first provided flag.
        :rtype: FlaggedDependency
        '''

        # Return the first dependency that matches any of the provided flags.
        # Input flags are assumed ordinal in priority, so the first match is returned.
        for flag in flags:
            match = next(
                (dependency for dependency in self.dependencies if dependency.flag == flag),
                None
            )
            if match:
                return match

        # Return None if no dependency matches the flags.
        return None

    # * method: get_type
    def get_type(self, *flags) -> type:
        '''
        Gets the type of the container attribute based on the provided flags.

        :param flags: The flags for the flagged container dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the container attribute.
        :rtype: type
        '''

        # Check the flagged dependencies for the type first.
        for flag in flags:
            dependency = self.get_dependency(flag)
            if dependency:
                return ImportDependency.execute(
                    dependency.module_path,
                    dependency.class_name
                ) 
        
        # Otherwise defer to an available default type.
        if self.module_path and self.class_name:
            return ImportDependency.execute(
                self.module_path,
                self.class_name
            )
        
        # Return None if no type is found.
        return None

    # * method: remove_dependency
    def remove_dependency(self, flag):
        '''
        Remove a flagged container dependency by its flag.

        :param flag: The flag identifying the dependency to remove.
        :type flag: str
        '''

        # Filter out any dependency whose flag matches the provided flag.
        self.dependencies = [
            dependency
            for dependency in self.dependencies
            if dependency.flag != flag
        ]

    # * method: set_dependency
    def set_dependency(
        self,
        flag,
        module_path=None,
        class_name=None,
        parameters=None,
    ):
        '''
        Sets or updates a flagged container dependency.

        :param flag: The flag that identifies the dependency.
        :type flag: str
        :param module_path: The module path for the dependency.
        :type module_path: Optional[str]
        :param class_name: The class name for the dependency.
        :type class_name: Optional[str]
        :param parameters: The parameters for the dependency (empty dict by default).
        :type parameters: Dict[str, Any] | None
        '''

        # Normalize parameters to a dict; None is treated as an empty mapping here
        # and the final cleaning is delegated to FlaggedDependency.set_parameters.
        parameters = parameters or {}

        # Replace the value of the dependency if a dependency with the same flag exists.
        for dep in self.dependencies:
            if dep.flag == flag:
                dep.module_path = module_path
                dep.class_name = class_name
                dep.set_parameters(parameters)
                return

        # Create a new dependency if none exists with this flag.
        dependency = ModelObject.new(
            FlaggedDependency,
            module_path=module_path,
            class_name=class_name,
            flag=flag,
            parameters=parameters,
        )

        self.dependencies.append(dependency)

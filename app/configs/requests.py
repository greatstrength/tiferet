from schematics import types as t
from schematics import Model

from ..objects.cli import CliArgument
from ..objects.object import ModelObject
from ..objects.object import ObjectAttribute
from ..objects.object import ObjectMethod
from ..objects.object import ObjectMethodParameter
from ..objects.object import ObjectMethodCodeBlock
from ..objects.container import ContainerAttribute
from ..objects.error import ErrorMessage
from ..objects.feature import FeatureHandler


class AddCliCommand(Model):

    interface_id = t.StringType(required=True)
    group_id = t.StringType(required=True)
    command_key = t.StringType(required=True)
    name = t.StringType(required=True)
    help = t.StringType(required=True, deserialize_from=[
                        'help', 'description'])
    feature_key = t.StringType()


class AddCliArgument(CliArgument):

    name = t.StringType(required=True)
    interface_id = t.StringType(required=True)
    help = t.StringType(required=True, deserialize_from=[
                        'help', 'description'])
    arg_type = t.StringType(default='command', choices=['command', 'parent_argument'])
    feature_id = t.StringType()
    positional = t.BooleanType()
    flags = t.ListType(t.StringType(), default=[])
    name_or_flags = t.ListType(t.StringType(), default=[])


class AddContainerAttribute(ContainerAttribute):

    group_id = t.StringType(required=True)
    flag = t.StringType(required=True)
    data = t.ListType(t.StringType(), default=[])


class AddNewError(Model):

    name = t.StringType(required=True)
    message = t.ListType(t.ModelType(ErrorMessage), default=[])


class AddNewFeature(Model):

    name = t.StringType(required=True)
    group_id = t.StringType(required=True)
    feature_key = t.StringType(required=True)
    handlers = t.ListType(t.ModelType(FeatureHandler),
                          default=[], deserialize_from=['handler', 'handlers'])
    request_type_path = t.StringType()
    description = t.StringType()


class AddFeatureHandler(FeatureHandler):
    
    feature_id = t.StringType(required=True)
    position = t.IntType()


class AddNewObject(ModelObject):

    id = t.StringType()
    class_name = t.StringType()


class AddObjectAttribute(ObjectAttribute):

    object_id = t.StringType(required=True)
    type_properties = t.DictType(t.StringType(), default={})


class AddObjectMethod(ObjectMethod):

    object_id = t.StringType(required=True)
    parameters = t.ListType(t.ModelType(ObjectMethodParameter), default=[], deserialize_from=['param'])


class AddObjectMethodParameters(Model):

    object_id = t.StringType(required=True)
    method_name = t.StringType(required=True)
    params_data = t.ListType(t.ModelType(ObjectMethodParameter), required=True, deserialize_from=['param'])


class AddObjectMethodCode(Model):

    object_id = t.StringType(required=True)
    method_name = t.StringType(required=True)
    code_block = t.ListType(t.ModelType(ObjectMethodCodeBlock), required=True, deserialize_from=['code'])

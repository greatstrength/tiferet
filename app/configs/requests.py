from schematics import types as t
from schematics import Model

class AddCliCommand(Model):
    
    group_id = t.StringType(required=True)
    command_key = t.StringType(required=True)
    name = t.StringType(required=True)
    help = t.StringType(required=True, deserialize_from=['help', 'description'])
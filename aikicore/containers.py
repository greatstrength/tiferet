from schematics import types as t, Model

# Container configuration


class ContainerConfiguration(Model):

    app_project_filepath = t.StringType(required=False, default=None)


# Default container
class Container():

    # Custom fields below
    # ...

    def __init__(self, config: ContainerConfiguration):
        # Default init
        self.config = config

        # Custom init below
        # ...


# Default dynamic container
class DynamicContainer():

    def add_service(self, service_name, factory_func):
        setattr(self, service_name, factory_func)

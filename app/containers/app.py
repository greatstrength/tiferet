from typing import List

from dependencies import Injector

from ..objects.container import ContainerAttribute


class AppContainer(object):

    container: Injector = None

    def __init__(self, attributes: List[ContainerAttribute]):
        pass

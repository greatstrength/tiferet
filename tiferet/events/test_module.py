"""Tiferet Test Module Events"""

# *** imports

# ** core
from typing import Any

# ** infra
from yaml.nodes import MappingNode

# ** app
from ..assets.tester import (
    TEST_ANCHOR_CONFLICT_ID,
    TEST_MODULE_LOAD_FAILED_ID,
)
from ..domain.test_module import TestModuleAddress, TestModuleDocument
from ..interfaces.core import ServiceError
from ..utils.yaml import YamlLoader
from .core import DomainEvent

# *** events

# ** event: read_test_module_document
class ReadTestModuleDocument(DomainEvent):
    '''
    Read one test-module document from an address and a YAML revision.

    The event composes through the anchored loader when text is present.
    It does not open a file, and it does not take a service.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['address'])
    def execute(self,
            address: TestModuleAddress,
            text: str = None,
            anchors: Any = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Compose a revision into one document, or leave the body unset.

        :param address: The document address.
        :type address: TestModuleAddress
        :param text: The YAML revision. None means the file is absent.
        :type text: str
        :param anchors: An existing anchor table, used when composing a fragment.
        :type anchors: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The document. Body stays unset when text is None.
        :rtype: TestModuleDocument
        '''

        # An absent file is not composed and is not created.
        if text is None:
            return TestModuleDocument(address=address, text=None)

        # Compose through the anchored loader. Do not safe_load.
        try:
            body = YamlLoader.compose_anchored(text, anchors=anchors)
        except ServiceError as error:
            self._raise_compose_error(error)

        # Attach the composed root so the event returns one value.
        return TestModuleDocument(address=address, text=text, body=body)

    # * method: raise_compose_error
    def _raise_compose_error(self, error: ServiceError) -> None:
        '''Map a loader failure onto the two ids the writer already uses.'''

        # Anchor conflicts stay distinct from a compose failure.
        failure = error.kwargs.get('failure')
        problem = error.message or str(error)
        if failure == 'anchor' or 'undefined alias' in problem or 'duplicate anchor' in problem:
            self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)

        # Do not add an eighth id.
        self.raise_error(TEST_MODULE_LOAD_FAILED_ID, problem, detail=problem)

# ** event: write_test_module_document
class WriteTestModuleDocument(DomainEvent):
    '''
    Write one test-module document from a working graph.

    The event serializes through the anchored extension and returns a new
    document. It does not save, dump, or replace a file, and it does not
    take a service.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['document', 'working'])
    def execute(self,
            document: TestModuleDocument,
            working: Any,
            already: Any = None,
            **kwargs,
        ) -> TestModuleDocument:
        '''
        Serialize the working graph and return a new document.

        :param document: The document whose address is kept.
        :type document: TestModuleDocument
        :param working: The composed graph to emit.
        :type working: Any
        :param already: Nodes the serializer should treat as already visited.
        :type already: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new document with the same address and the emitted text.
        :rtype: TestModuleDocument
        '''

        # An empty document root is a newline, not an empty mapping dump.
        if already is None and isinstance(working, MappingNode) and not working.value:
            return TestModuleDocument(
                address=document.address,
                text='\n',
                body=working,
            )

        # Serialize through the anchored extension. Do not safe_dump.
        try:
            text = YamlLoader.serialize_anchored(working, already=already)
        except ServiceError as error:
            if error.kwargs.get('failure') == 'anchor':
                problem = error.message or 'A shared node has no anchor name.'
                self.raise_error(TEST_ANCHOR_CONFLICT_ID, problem, detail=problem)
            raise

        # Return a new document. Do not open a file.
        return TestModuleDocument(
            address=document.address,
            text=text,
            body=working,
        )

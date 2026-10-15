"""Tiferet Test Module Context"""

# *** imports

# ** core
import re
from pathlib import Path
from typing import Any

# ** app
from ..assets import TiferetError
from ..assets.tester import TEST_MODULE_PATH_INVALID_ID
from ..domain.tester_module import TestModuleAddress, TestModuleDocument
from .core import BaseContext

# *** constants

# ** constant: test_module_directory
_TEST_MODULE_DIRECTORY = 'tiferet_tests'

# ** constant: name_pattern
_NAME_PATTERN = re.compile(r'[a-z][a-z0-9_]*\Z')

# ** constant: stem_pattern
_STEM_PATTERN = re.compile(r'test_[a-z0-9_]+\Z')

# *** contexts

# ** context: test_module_context
class TestModuleContext(BaseContext):
    '''
    Hold one test-module document for a writer call. The blueprint reads the
    bytes and the verb events decide the edit. This context keeps the bound
    document and the working graph. It does not decide an entry.
    '''

    # * attribute: domain_type
    domain_type = TestModuleDocument

    # * attribute: working
    working: Any

    # * init
    def __init__(self, services: Any = None) -> None:
        '''
        Initialize the test-module context with a null working graph.

        :param services: The shared DI context or collaborator bundle.
        :type services: Any
        :return: None
        :rtype: None
        '''

        # Initialize the base context.
        super().__init__(services=services)

        # Start the working graph as null.
        self.working = None

    # * method: bind (class)
    @classmethod
    def bind(cls, document: TestModuleDocument) -> 'TestModuleContext':
        '''
        Bind a test-module document and set working to its body.

        :param document: The document to bind.
        :type document: TestModuleDocument
        :return: The bound test-module context.
        :rtype: TestModuleContext
        '''

        # Bind the document through from_domain.
        context = cls.from_domain(document)

        # Set the working graph to the document body.
        context.working = document.body

        # Return the bound context.
        return context

    # * method: address (class)
    @classmethod
    def _address(cls, rel: str, base_dir: str = '.') -> TestModuleAddress:
        '''
        Resolve a relative stem to a read-only test-module address.

        :param rel: The relative test-module stem, without an extension.
        :type rel: str
        :param base_dir: The directory whose tiferet_tests child holds the module.
        :type base_dir: str | Path
        :return: The resolved test-module address.
        :rtype: TestModuleAddress
        '''

        # Refuse non-string rel or a base_dir that is neither str nor Path.
        if not isinstance(rel, str) or not isinstance(base_dir, (str, Path)):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address must be a relative stem.',
                rel=rel,
            )

        # Refuse empty, unstripped, absolute, backslash, dotdot, prefix, or extension stems.
        if (
            not rel
            or rel != rel.strip()
            or rel.startswith('/')
            or rel.startswith('\\')
            or '\\' in rel
            or '..' in rel
            or rel.startswith('tests/')
            or rel.startswith('tests_int/')
            or rel.startswith(f'{_TEST_MODULE_DIRECTORY}/')
            or '.py' in rel
            or '.yml' in rel
            or '.yaml' in rel
        ):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address is illegal.',
                rel=rel,
            )

        # Split the stem and require every segment to match the name pattern.
        segments = rel.split('/')
        if any(_NAME_PATTERN.fullmatch(segment) is None for segment in segments):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address is illegal.',
                rel=rel,
            )

        # Require the last segment to match the test_* stem pattern.
        if _STEM_PATTERN.fullmatch(segments[-1]) is None:
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module stem must match test_*.',
                rel=rel,
            )

        # Resolve under tiferet_tests and refuse paths that escape the base.
        try:
            base = (Path(base_dir).resolve() / _TEST_MODULE_DIRECTORY).resolve()
            path = base.joinpath(*segments).with_suffix('.yml').resolve()
            path.relative_to(base)
        except (OSError, ValueError):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module path must stay under tiferet_tests.',
                rel=rel,
            )

        # Return the read-only address; the file need not exist.
        return TestModuleAddress(
            rel=rel,
            base_dir=str(base_dir),
            path=str(path),
        )

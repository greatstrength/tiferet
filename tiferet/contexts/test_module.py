"""Tiferet Test Module Context"""

# *** imports

# ** core
import re
from pathlib import Path
from typing import Any

# ** app
from ..assets import TiferetError
from ..assets.tester import TEST_MODULE_PATH_INVALID_ID
from ..domain.test_module import TestModuleAddress, TestModuleDocument
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
    Hold one test-module document for a writer call.

    The blueprint reads the bytes and the verb events decide the edit.
    This context keeps the bound document and the working graph. It does
    not decide an entry.
    '''

    # * attribute: domain_type
    domain_type = TestModuleDocument

    # * attribute: working
    working: Any

    # * init
    def __init__(self, services: Any = None) -> None:
        '''
        Initialize the context. The working graph is set at bind.

        :param services: Unused shared services slot.
        :type services: Any
        '''

        # Do not import a loader, a mapper, or a blueprint.
        super().__init__(services=services)
        self.working = None

    # * method: bind (class)
    @classmethod
    def bind(cls, document: TestModuleDocument) -> 'TestModuleContext':
        '''
        Bind a context to one test-module document.

        :param document: The document the read event returned.
        :type document: TestModuleDocument
        :return: The bound context.
        :rtype: TestModuleContext
        '''

        # Bind the document. Do not assign its fields.
        context = cls.from_domain(document)
        context.working = document.body
        return context

    # * method: address (class)
    @classmethod
    def _address(cls, rel: str, base_dir: str = '.') -> TestModuleAddress:
        '''Resolve rel to a read-only address, or refuse it.'''

        if not isinstance(rel, str) or not isinstance(base_dir, (str, Path)):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address must be a relative stem.',
                rel=rel,
            )
        if (
            not rel
            or rel != rel.strip()
            or rel.startswith(('/', '\\'))
            or '\\' in rel
            or '..' in rel
            or rel.startswith(('tests/', 'tests_int/', f'{_TEST_MODULE_DIRECTORY}/'))
            or any(token in rel for token in ('.py', '.yml', '.yaml'))
        ):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address is illegal.',
                rel=rel,
            )
        segments = rel.split('/')
        if any(_NAME_PATTERN.fullmatch(segment) is None for segment in segments):
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module address is illegal.',
                rel=rel,
            )
        if _STEM_PATTERN.fullmatch(segments[-1]) is None:
            TiferetError.raise_error(
                TEST_MODULE_PATH_INVALID_ID,
                'A test module stem must match test_*.',
                rel=rel,
            )
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
        return TestModuleAddress(rel=rel, base_dir=str(base_dir), path=str(path))

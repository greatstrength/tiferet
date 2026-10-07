"""Tiferet Test Contexts"""

# *** imports

# ** app
from .feature import FeatureContext
from ..domain.test import Test

# *** contexts

# ** context: test_context
class TestContext(FeatureContext):
    '''
    The session's view of one test. It extends ``FeatureContext`` so a test
    runs as a feature, and it declares ``domain_type = Test`` in its own
    namespace so ``Feature`` stays mapped to ``FeatureContext``.
    '''

    # * attribute: domain_type
    domain_type = Test

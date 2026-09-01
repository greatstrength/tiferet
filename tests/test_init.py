"""Tiferet Root Package Tests"""

# *** imports

# ** core
import ast
import inspect

# ** app
import tiferet
from tiferet import assets

# *** tests

# ** test: a_alias_resolves_to_assets_module
def test_a_alias_resolves_to_assets_module():
    '''
    Test that the root `a` alias is the same module object as `tiferet.assets`.
    '''

    # Assert the root alias resolves to the assets module by identity.
    assert tiferet.a is assets

# ** test: all_first_member_is_a
def test_all_first_member_is_a():
    '''
    Test that `a` is the first public member declared in `tiferet.__all__`,
    inspected via the source AST rather than the runtime list, so the
    invariant is enforced at the declaration site.
    '''

    # Parse the root package source and locate the __all__ assignment.
    tree = ast.parse(inspect.getsource(tiferet))
    all_assign = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == '__all__' for target in node.targets)
    )

    # Assert the first element of the __all__ list is the string 'a'.
    first_element = all_assign.value.elts[0]
    assert isinstance(first_element, ast.Constant)
    assert first_element.value == 'a'

# ** test: a_import_precedes_dependent_framework_imports
def test_a_import_precedes_dependent_framework_imports():
    '''
    Test that `from . import assets as a` is bound before every other
    root-relative import in `tiferet/__init__.py`, via AST inspection of
    source structure rather than incidental runtime import order.
    '''

    # Parse the root package source into an AST.
    tree = ast.parse(inspect.getsource(tiferet))

    # Collect every root-relative (level 1) ImportFrom node.
    relative_imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level == 1
    ]

    # Locate the node binding `a` from `assets` (module is None because the
    # statement is `from . import assets as a`, not `from .assets import ...`).
    a_import = next(
        node for node in relative_imports
        if node.module is None
        and any(alias.name == 'assets' and alias.asname == 'a' for alias in node.names)
    )

    # Assert the `a` binding precedes every other root-relative import.
    other_imports = [node for node in relative_imports if node is not a_import]
    assert other_imports, 'Expected at least one other root-relative import to compare against.'
    assert all(a_import.lineno < node.lineno for node in other_imports)

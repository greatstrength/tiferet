"""Tiferet Root Package Export Tests"""

# *** imports

# ** core
import os
import subprocess
import sys

# ** app
import tiferet

# *** tests

# ** test: root_asset_alias_is_assets_package
def test_root_asset_alias_is_assets_package() -> None:
    '''
    Test that `from tiferet import a` succeeds and is the same object as
    `tiferet.assets` (identity, not a copy).

    :return: None
    :rtype: None
    '''

    # Import the root-level asset alias.
    from tiferet import a

    # Assert it is the same module object as tiferet.assets.
    assert a is tiferet.assets

# ** test: a_is_first_entry_in_all
def test_a_is_first_entry_in_all() -> None:
    '''
    Test that 'a' is present in tiferet.__all__ and is the first element.

    :return: None
    :rtype: None
    '''

    # Assert 'a' is present and leads the export list.
    assert 'a' in tiferet.__all__
    assert tiferet.__all__[0] == 'a'

# ** test: root_asset_alias_reaches_existing_assets_reexports
def test_root_asset_alias_reaches_existing_assets_reexports() -> None:
    '''
    Test that the existing tiferet.assets re-exports remain reachable
    through the root alias `a`.

    :return: None
    :rtype: None
    '''

    # Assert each existing assets re-export is reachable through a.
    assert tiferet.a.TiferetError is tiferet.assets.TiferetError
    assert tiferet.a.error is tiferet.assets.error
    assert tiferet.a.app is tiferet.assets.app
    assert tiferet.a.cli is tiferet.assets.cli
    assert tiferet.a.logging is tiferet.assets.logging

# ** test: clean_interpreter_import_succeeds_without_warning
def test_clean_interpreter_import_succeeds_without_warning() -> None:
    '''
    Test that a fresh-process import of tiferet succeeds with no warning
    printed to stderr when TIFERET_SILENT_IMPORTS is unset, confirming no
    regression to the existing try/except warning path.

    :return: None
    :rtype: None
    '''

    # Import tiferet in a clean interpreter and report the outcome.
    result = subprocess.run(
        [sys.executable, '-c', 'import tiferet; print(tiferet.a is tiferet.assets)'],
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if k != 'TIFERET_SILENT_IMPORTS'},
    )

    # Assert the import succeeded with no warning on stderr.
    assert result.returncode == 0
    assert result.stderr == ''
    assert result.stdout.strip() == 'True'

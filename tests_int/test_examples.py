# *** imports

# ** core
import shutil
import subprocess
import sys
from pathlib import Path

# ** infra
import pytest

# *** fixtures

# ** fixture: basic_calculator_dir
@pytest.fixture
def basic_calculator_dir(tmp_path: Path) -> Path:
    '''
    Copy the basic calculator example into a temporary directory so a run
    never writes the tracked formulas.yml or config.yml.

    :param tmp_path: The pytest temporary directory.
    :type tmp_path: Path
    :return: The path to the copied example.
    :rtype: Path
    '''

    # Locate the tracked example from the repository root.
    source = Path(__file__).resolve().parents[1] / 'examples' / 'basic_calculator'

    # Copy the example without its bytecode caches and return the copy.
    return shutil.copytree(
        source,
        tmp_path / 'basic_calculator',
        ignore=shutil.ignore_patterns('__pycache__'),
    )

# *** tests

# ** test: basic_calculator_cli_add
def test_basic_calculator_cli_add(basic_calculator_dir: Path):
    '''
    Test that the calculator CLI entry point adds two numbers.

    :param basic_calculator_dir: The copied basic calculator example.
    :type basic_calculator_dir: Path
    '''

    # Run the CLI entry point for calc add 1 2.
    result = subprocess.run(
        [sys.executable, 'calc_cli.py', 'calc', 'add', '1', '2'],
        cwd=basic_calculator_dir,
        capture_output=True,
        text=True,
    )

    # Assert a clean exit whose last non-empty stdout line is the sum.
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines[-1] == '3.0'

# ** test: basic_calculator_client
def test_basic_calculator_client(basic_calculator_dir: Path):
    '''
    Test that the calculator client entry point evaluates the rectangle area formula.

    :param basic_calculator_dir: The copied basic calculator example.
    :type basic_calculator_dir: Path
    '''

    # Run the client entry point.
    result = subprocess.run(
        [sys.executable, 'calc_client.py'],
        cwd=basic_calculator_dir,
        capture_output=True,
        text=True,
    )

    # Assert a clean exit and the rectangle area output.
    assert result.returncode == 0, result.stderr
    assert 'rectangle_area(width=3, height=4) = 12' in result.stdout

# ** test: basic_calculator_fluent
def test_basic_calculator_fluent(basic_calculator_dir: Path):
    '''
    Test that the calculator fluent entry point evaluates its chained expressions.

    :param basic_calculator_dir: The copied basic calculator example.
    :type basic_calculator_dir: Path
    '''

    # Run the fluent entry point.
    result = subprocess.run(
        [sys.executable, 'calc_fluent.py'],
        cwd=basic_calculator_dir,
        capture_output=True,
        text=True,
    )

    # Assert a clean exit and the chained expression output.
    assert result.returncode == 0, result.stderr
    assert '2.0 + 3.0 * 4.0 - 1.0 = 13.0' in result.stdout

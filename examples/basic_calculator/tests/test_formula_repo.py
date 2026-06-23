"""Tiferet Basic Calculator Formula Repository Tests"""

# *** imports

# ** infra
import pytest

# ** app
from app.mappers.formula import FormulaAggregate
from app.repos.formula import FormulaConfigRepository

# *** fixtures

# ** fixture: repo
@pytest.fixture
def repo(tmp_path) -> FormulaConfigRepository:
    '''
    A formula repository backed by a temporary YAML file.
    '''

    # Build the repository against a temp config file (created on first save).
    return FormulaConfigRepository(formula_config=str(tmp_path / 'formulas.yml'))

# *** tests

# ** test: save_and_get
def test_save_and_get(repo):
    '''
    A saved formula can be retrieved with its derived id and variables.
    '''

    # Save a formula, then retrieve it by its derived id.
    repo.save(FormulaAggregate(name='Rectangle Area', expression='width * height'))
    formula = repo.get('rectangle_area')

    # The retrieved formula round-trips its fields.
    assert formula is not None
    assert formula.expression == 'width * height'
    assert formula.variables == ['width', 'height']

# ** test: exists_and_get_missing
def test_exists_and_get_missing(repo):
    '''
    Missing formulas report absence and return None.
    '''

    # An unsaved formula does not exist and resolves to None.
    assert repo.exists('nope') is False
    assert repo.get('nope') is None

# ** test: list_returns_all
def test_list_returns_all(repo):
    '''
    Listing returns all saved formulas.
    '''

    # Save two formulas.
    repo.save(FormulaAggregate(name='Rectangle Area', expression='width * height'))
    repo.save(FormulaAggregate(name='Sum', expression='a + b'))

    # Listing returns both formulas.
    ids = {formula.id for formula in repo.list()}
    assert ids == {'rectangle_area', 'sum'}

# ** test: delete_is_idempotent
def test_delete_is_idempotent(repo):
    '''
    Deleting removes a formula and is safe to repeat.
    '''

    # Save then delete a formula.
    repo.save(FormulaAggregate(name='Rectangle Area', expression='width * height'))
    repo.delete('rectangle_area')

    # The formula is gone and a repeated delete does not raise.
    assert repo.exists('rectangle_area') is False
    repo.delete('rectangle_area')

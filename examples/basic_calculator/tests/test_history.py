"""Tiferet Basic Calculator History Event Tests"""

# *** imports

# ** core
import json

# ** infra
import pytest

# ** app
from tiferet.events import DomainEvent
from app.events.history import RecordCalculation, ListRecentFormulas

# *** tests

# ** test: record_calculation_creates_file
def test_record_calculation_creates_file(tmp_path):
    '''
    Recording a calculation writes a new history file and returns the result.
    '''

    # Record a single calculation into a fresh history file.
    history_file = tmp_path / 'history.json'
    result = DomainEvent.handle(
        RecordCalculation,
        result=3,
        operator='+',
        a=1,
        b=2,
        history_file=str(history_file),
    )

    # The result is returned unchanged and the entry is persisted.
    assert result == 3
    entries = json.loads(history_file.read_text())
    assert len(entries) == 1
    assert entries[0]['expression'] == '1 + 2'
    assert entries[0]['result'] == 3

# ** test: record_calculation_appends_and_trims
def test_record_calculation_appends_and_trims(tmp_path):
    '''
    Recording more than max_entries keeps only the most recent entries.
    '''

    # Record five calculations with a max of three retained entries.
    history_file = tmp_path / 'history.json'
    for i in range(5):
        DomainEvent.handle(
            RecordCalculation,
            result=i,
            operator='+',
            a=i,
            b=0,
            history_file=str(history_file),
            max_entries=3,
        )

    # Only the three most recent entries are retained.
    entries = json.loads(history_file.read_text())
    assert [entry['result'] for entry in entries] == [2, 3, 4]

# ** test: list_recent_formulas_missing_file
def test_list_recent_formulas_missing_file(tmp_path):
    '''
    Listing recent formulas returns a friendly message when no file exists.
    '''

    # Listing a non-existent history file yields a friendly message.
    result = DomainEvent.handle(
        ListRecentFormulas,
        history_file=str(tmp_path / 'missing.json'),
    )
    assert result == 'No recent calculations yet.'

# ** test: list_recent_formulas_returns_limited_entries
def test_list_recent_formulas_returns_limited_entries(tmp_path):
    '''
    Listing recent formulas honors the optional limit, newest entries last.
    '''

    # Record two calculations.
    history_file = tmp_path / 'history.json'
    DomainEvent.handle(RecordCalculation, result=3, operator='+', a=1, b=2, history_file=str(history_file))
    DomainEvent.handle(RecordCalculation, result=5, operator='+', a=2, b=3, history_file=str(history_file))

    # Listing with a limit renders only the most recent entry.
    result = DomainEvent.handle(ListRecentFormulas, history_file=str(history_file), limit=1)
    assert result == '2 + 3 = 5'

# *** imports

# ** core
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ** infra
from tiferet.events import *
from tiferet.utils import Json

# ** app
from ..assets.core import FEATURE_OPERATOR_MAP
from ..domain.expression import Expression

# *** functions

# ** function: format_history_entry
def format_history_entry(entry: dict) -> str:
    '''
    Render a single history entry as a friendly one-line string.

    :param entry: The stored calculation entry.
    :type entry: dict
    :return: A human-readable "expression = result" line.
    :rtype: str
    '''

    # Render the entry as "expression = result".
    return f"{entry.get('expression')} = {entry.get('result')}"

# *** events

# ** event: record_calculation
class RecordCalculation(DomainEvent):
    '''
    A domain event that appends the most recently executed calculation to a
    JSON history file using the Tiferet file loader, keeping only the most
    recent entries.

    Invoked once per successful feature run via CalculatorAppContext's
    session-level record_run handler (rather than as a per-feature step), so
    it derives the recorded expression from whichever data the run actually
    produced: a fluent chain's calc.resolve run passes its full logged
    values/operators term list (see FluentRequestContext), rendered via
    Expression.display() into one whole-expression entry per chain; any
    other run derives a plain "a op b" expression from feature_id via
    FEATURE_OPERATOR_MAP. Runs with neither (formula.*, calc.history,
    calc.safe_divide) are a graceful no-op.
    '''

    # * method: execute
    def execute(self,
            feature_id: str,
            a: Any = None,
            b: Any = None,
            values: list | None = None,
            operators: list | None = None,
            result: Any = None,
            history_file: str = 'history.json',
            max_entries: int = 10,
            **kwargs,
        ) -> Any:
        '''
        Record a calculation entry and return the original result unchanged.

        :param feature_id: The identifier of the feature that was executed.
        :type feature_id: str
        :param a: The first operand, if any.
        :type a: Any
        :param b: The second operand, if any.
        :type b: Any
        :param values: A fluent chain's full logged operand list, if any.
        :type values: list | None
        :param operators: A fluent chain's full logged operator list, if any.
        :type operators: list | None
        :param result: The computed result of the calculation, if any.
        :type result: Any
        :param history_file: The JSON file used to store recent calculations.
        :type history_file: str
        :param max_entries: The maximum number of entries to retain.
        :type max_entries: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The original result, unchanged.
        :rtype: Any
        '''

        # Nothing to record without a result.
        if result is None:
            return result

        # A fluent chain's calc.resolve run logs its own full expression;
        # render it directly instead of deriving one from feature_id.
        operator = None
        if values is not None and operators is not None:
            expression = Expression(values=values, operators=operators).display()

        # Otherwise derive a plain "a op b" expression from the operator
        # mapped to feature_id; skip recording entirely when there is none.
        else:
            operator = FEATURE_OPERATOR_MAP.get(feature_id)
            if operator is None:
                return result
            expression = f'{operator}{a}' if b is None else f'{a} {operator} {b}'

        # Read existing entries when the history file already exists.
        entries = Json(history_file).load() if Path(history_file).exists() else []

        # Append the new calculation entry with an ISO timestamp.
        entries.append(dict(
            expression=expression,
            a=a,
            b=b,
            operator=operator,
            result=result,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))

        # Trim the list to the most recent entries.
        entries = entries[-max_entries:]

        # Persist the updated history via the file loader.
        Json(history_file, mode='w').save(entries)

        # Return the result unchanged so the feature response is preserved.
        return result

# ** event: list_recent_formulas
class ListRecentFormulas(DomainEvent):
    '''
    A domain event that returns the most recently executed calculations from
    the JSON history file.
    '''

    # * method: execute
    def execute(self,
            history_file: str = 'history.json',
            limit: int | None = None,
            **kwargs,
        ) -> str:
        '''
        Return the recent calculation history as a rendered, human-readable string.

        :param history_file: The JSON file used to store recent calculations.
        :type history_file: str
        :param limit: Optional maximum number of entries to return.
        :type limit: int | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A newline-separated summary of the recent calculations.
        :rtype: str
        '''

        # Return a friendly message when no history file exists yet.
        if not Path(history_file).exists():
            return 'No recent calculations yet.'

        # Load the stored entries via the file loader.
        entries = Json(history_file).load()

        # Apply an optional limit to the most recent entries.
        if limit:
            entries = entries[-limit:]

        # Return a friendly message when there are no entries.
        if not entries:
            return 'No recent calculations yet.'

        # Render each entry on its own line.
        return '\n'.join(format_history_entry(entry) for entry in entries)

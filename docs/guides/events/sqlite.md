# Events – SQLite Operations

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Module:** `tiferet/events/sqlite.py`  
**Version:** 2.0.0a6

## Overview

The SQLite event module provides domain events for executing SQL operations against a SQLite database through an injected `SqliteService`. All events use the context manager protocol (`with self.sqlite_service as sql:`) to ensure proper connection lifecycle management, auto-commit on success, and auto-rollback on failure.

## Events at a Glance

| Event | Operation | Required Parameters | Returns |
|---|---|---|---|
| `QuerySql` | SELECT | `query` | `List[Dict]` or `Dict` or `None` |
| `MutateSql` | INSERT/UPDATE/DELETE | `statement` | `Dict` (rowcount, lastrowid) |
| `BulkMutateSql` | Batch INSERT/UPDATE/DELETE | `statement`, `parameters_list` | `Dict` (total_rowcount, lastrowids) |
| `ExecuteScriptSql` | Multi-statement script | `script` | `Dict` (success) |
| `BackupSql` | Online backup | `target_path` | `Dict` (success, message) |
| `CreateTableSql` | CREATE TABLE | `table_name`, `columns` | `Dict` (success) |
| `DropTableSql` | DROP TABLE | `table_name` | `Dict` (success) |

## Dependency

All events inject a single dependency:

- **`sqlite_service: SqliteService`** — the service interface for SQLite database operations, implementing the context manager protocol.

## Event Details

### QuerySql

Executes a read-only SQL query (SELECT or WITH) and returns results as dictionaries.

**Required:** `query`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `parameters` | `Sequence[Any]` | `()` | Bind parameters (tuple or dict) |
| `fetch_one` | `bool` | `False` | If True, return single row or None |

**Returns:** `List[Dict]` (default) or `Dict`/`None` (when `fetch_one=True`).

**Validation:** Query must start with `SELECT` or `WITH`.

```python
# Multi-row query
rows = DomainEvent.handle(
    QuerySql,
    dependencies={'sqlite_service': sqlite_service},
    query="SELECT * FROM users WHERE active = ?",
    parameters=(1,),
)

# Single-row query
row = DomainEvent.handle(
    QuerySql,
    dependencies={'sqlite_service': sqlite_service},
    query="SELECT * FROM users WHERE id = ?",
    parameters=(42,),
    fetch_one=True,
)
```

### MutateSql

Executes a single INSERT, UPDATE, or DELETE statement and returns operation metadata.

**Required:** `statement`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `parameters` | `Sequence[Any]` | `()` | Bind parameters (tuple or dict) |

**Returns:** `{"rowcount": int, "lastrowid": int | None}` — `lastrowid` is populated only for INSERT.

**Validation:** Statement must start with `INSERT`, `UPDATE`, or `DELETE`.

```python
result = DomainEvent.handle(
    MutateSql,
    dependencies={'sqlite_service': sqlite_service},
    statement="INSERT INTO users (name, email) VALUES (?, ?)",
    parameters=('Alice', 'alice@example.com'),
)
# result == {"rowcount": 1, "lastrowid": 42}
```

### BulkMutateSql

Executes a single statement across multiple parameter sets via `executemany`.

**Required:** `statement`, `parameters_list`

**Returns:** `{"total_rowcount": int, "lastrowids": List[int] | None}` — `lastrowids` populated only for INSERT.

**Validation:** Statement must start with `INSERT`/`UPDATE`/`DELETE`; `parameters_list` must be non-empty.

```python
result = DomainEvent.handle(
    BulkMutateSql,
    dependencies={'sqlite_service': sqlite_service},
    statement="INSERT INTO users (name) VALUES (?)",
    parameters_list=[('Alice',), ('Bob',), ('Carol',)],
)
```

### ExecuteScriptSql

Executes a multi-statement SQL script (DDL + DML) in a single operation via `executescript`.

**Required:** `script`

**Returns:** `{"success": bool}`

```python
result = DomainEvent.handle(
    ExecuteScriptSql,
    dependencies={'sqlite_service': sqlite_service},
    script="CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1);",
)
```

### BackupSql

Performs an online backup of the current SQLite database to a target file.

**Required:** `target_path`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pages` | `int` | `-1` | Pages per step (-1 = all at once) |
| `progress` | `Callable` | `None` | Optional callback(status, remaining, total) |

**Returns:** `{"success": bool, "message": str | None}`

**Errors:** `SQLITE_BACKUP_FAILED` on failure.

```python
result = DomainEvent.handle(
    BackupSql,
    dependencies={'sqlite_service': sqlite_service},
    target_path='/backups/db_backup.sqlite',
    pages=100,
)
```

### CreateTableSql

Generates and executes a CREATE TABLE statement from a columns dictionary and optional constraints.

**Required:** `table_name`, `columns`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `constraints` | `List[str]` | `()` | Table-level constraints (e.g., `UNIQUE(name)`) |
| `if_not_exists` | `bool` | `True` | Add IF NOT EXISTS clause |

**Returns:** `{"success": bool}`

**Validation:** Table name must be a valid identifier (alphanumeric + underscore, no leading digit). Columns must be a non-empty dict with non-empty string keys and values.

```python
result = DomainEvent.handle(
    CreateTableSql,
    dependencies={'sqlite_service': sqlite_service},
    table_name='products',
    columns={'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT NOT NULL', 'price': 'REAL'},
    constraints=['UNIQUE(name)', 'CHECK(price >= 0)'],
)
```

### DropTableSql

Generates and executes a DROP TABLE statement with optional IF EXISTS clause.

**Required:** `table_name`

**Optional parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `if_exists` | `bool` | `True` | Add IF EXISTS clause |

**Returns:** `{"success": bool}`

**Validation:** Table name must be a valid identifier.

```python
result = DomainEvent.handle(
    DropTableSql,
    dependencies={'sqlite_service': sqlite_service},
    table_name='old_table',
    if_exists=True,
)
```

## Migration Notes (v2.0)

- **Module docstring:** Added `"""Tiferet SQLite Events"""`.
- **Artifact comments:** `# *** commands` → `# *** events`; `# ** command:` → `# ** event:`.
- **Docstrings:** "Helper command to" → "Event to" for `CreateTableSql` and `DropTableSql`.
- **No parameter renames** — SQLite events do not use `attribute_id`.
- **Tests:** Converted from 42 function-based tests to 7 harness classes using `SqliteEventTestBase` (a `DomainEventTestBase` subclass with MagicMock context manager support). Result: 49 pass, 0 skip.

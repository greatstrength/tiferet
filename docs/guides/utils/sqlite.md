# Utilities – SqliteClient (alias: Sqlite)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 02, 2026  
**Version:** 2.0.0

<a id="sqliteclient"></a>
## Overview

`SqliteClient` is Tiferet’s friendly, safe way to work with SQLite databases.  
It builds directly on top of `FileLoader` (so it gets all the path handling and context-manager goodness for free), then adds everything you need for real database work: connections, queries, transactions, backups, and clean error handling.

What makes `SqliteClient` special compared to the other file utilities (`Yaml`, `Json`, `Csv`)?  
It also implements the full `SqliteService` interface — which means you can inject it into domain events and repositories exactly the same way you inject other services.  
At the same time, you can still use it directly (with or without the alias `Sqlite`) for quick scripts, tests, or simple one-off operations inside events.

The context manager is especially helpful here:  
- Everything inside the `with` block either succeeds completely (auto-commit)  
- or fails safely (auto-rollback + connection closed)

## Ubiquitous Language

- **URI mode** — `ro`/`rw`/`rwc`, SQLite's own connection-level access modes, distinct from the classic file-open modes other loaders use.
- **No special-cased constraint violations** — `sqlite3.IntegrityError` becomes a `SQLITE_STATEMENT_FAILED` `ServiceError` like any other driver failure; domain semantics for a specific constraint are the calling event's responsibility, not this client's.

## When should you reach for SqliteClient?

| Use case                                      | Best choice                                  | Why it fits                                                                 |
|-----------------------------------------------|----------------------------------------------|-----------------------------------------------------------------------------|
| Quick query or small script / test            | `with Sqlite(...) as db:`                    | Zero setup, immediate access                                                |
| Need to mock or swap database backends later  | Inject `SqliteService`                       | Follows dependency injection; easy to test & replace                        |
| Persistent domain objects (users, settings…)  | Use domain repository + injected service     | Keeps business logic clean and path-agnostic                                |
| One-time database backup                      | `source.backup(target_path)`                 | Built-in, safe, with proper error wrapping and optional progress callback    |
| Enforce read-only access                      | `mode='ro'`                                  | SQLite itself prevents writes at connection level                           |

## Quick examples to get you started

```python
from tiferet.utils import Sqlite

# === In-memory database (great for tests and throwaway work) ===
with Sqlite() as db:                        # defaults to :memory:
    db.execute("CREATE TABLE pets (name TEXT, age INTEGER)")
    db.execute("INSERT INTO pets VALUES (?, ?)", ("Luna", 3))
    print(db.fetch_all("SELECT * FROM pets WHERE age > 2"))  # → [('Luna', 3)]

# === Persistent file database – create if missing ===
with Sqlite(path="data/myapp.db", mode="rwc") as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    db.execute("INSERT OR REPLACE INTO config VALUES (?, ?)", ("theme", "dark"))

# === Read-only connection (safe for shared / production read paths) ===
with Sqlite("data/myapp.db", mode="ro") as db:
    theme = db.fetch_one("SELECT value FROM config WHERE key = 'theme'")[0]  # → 'dark'
```

## Constructor parameters (the ones you’ll use most)

| Parameter         | Type                  | Default       | What it does                                                                 |
|-------------------|-----------------------|---------------|------------------------------------------------------------------------------|
| `path`            | `str \| Path`         | `':memory:'`  | File path or special `:memory:` for in-memory database                       |
| `mode`            | `str`                 | `'rw'`        | `'ro'` = read-only, `'rw'` = read-write, `'rwc'` = read-write-create         |
| `isolation_level` | `str \| None`         | `None`        | `None` → autocommit, or `'DEFERRED'`, `'IMMEDIATE'`, `'EXCLUSIVE'`           |
| `timeout`         | `float`               | `5.0`         | How long to wait (seconds) when the database is locked by another connection |

## Most commonly used methods

- `execute(sql, parameters=())` → run one statement, get a cursor back  
- `executemany(sql, sequence)` → bulk insert / update  
- `executescript(sql_script)` → run several statements at once (DDL + data usually)  
- `fetch_one(query, parameters=())` → execute query and get next row (or `None`)  
- `fetch_all(query, parameters=())` → execute query and get list of all rows  
- `commit()` / `rollback()` → manual transaction control (rarely needed with context manager)  
- `backup(target_path, pages=-1, progress=None)` → efficient backup to a file path with optional progress callback

The context manager handles commit / rollback / close for you automatically.

## Typical domain-event usage (direct)

```python
from tiferet.events import DomainEvent, a
from tiferet.utils import Sqlite

class RecordVisit(DomainEvent):
    '''
    Log a page visit with timestamp.
    '''

    @DomainEvent.parameters_required(['db_path', 'page'])
    def execute(self, db_path: str, page: str, **kwargs) -> int:
        with Sqlite(path=db_path, mode='rwc') as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    page      TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("INSERT INTO visits (page) VALUES (?)", (page,))
            return db.fetch_one("SELECT COUNT(*) FROM visits")[0]
```

## Automatic rollback example (safety net)

```python
try:
    with Sqlite("data/app.db", mode="rw") as db:
        db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        db.execute("INSERT INTO transactions VALUES (...)")
        raise RuntimeError("payment gateway offline")   # simulate failure
except RuntimeError:
    pass  # ← nothing was committed – changes are gone
```

## Error handling

No `sqlite3` exception ever escapes `SqliteClient`. Every failure — a lost
connection, a rejected statement, a constraint violation — is wrapped as a
`ServiceError` (`tiferet.interfaces.core`) with the driver exception preserved as
`__cause__`, so you never have to catch `sqlite3` types in your own code.

`ServiceError` is deliberately **not** a `TiferetError`. A database failure is
infrastructural, not a domain outcome, so it is never resolved through the error
catalog and never formatted into an API response — it surfaces as an unhandled
exception, which is the intended behaviour. It is also not skippable via a feature
step's `pass_on_error`, which passes on domain errors only.

Codes are hosted in `tiferet/utils/sqlite.py` beside the raise sites:

```python
from tiferet.interfaces.core import ServiceError
from tiferet.utils.sqlite import (
    SQLITE_CONN_FAILED_ID,            # connect failed
    SQLITE_CONN_ALREADY_OPEN_ID,      # open_file called twice
    SQLITE_CONN_NOT_INITIALIZED_ID,   # used outside a 'with' block
    SQLITE_INVALID_MODE_ID,           # mode not ro / rw / rwc
    SQLITE_STATEMENT_FAILED_ID,       # execute / executemany / executescript
    SQLITE_QUERY_FAILED_ID,           # fetch_one / fetch_all row retrieval
    SQLITE_TRANSACTION_FAILED_ID,     # commit / rollback
    SQLITE_BACKUP_FAILED_ID,          # backup
)
```

**A constraint violation gets no special treatment.** `sqlite3.IntegrityError`
becomes a `SQLITE_STATEMENT_FAILED` service error like any other driver failure. If
you need domain semantics for a constraint violation, catch that specific code
inside your own event and raise a domain error of your choosing:

```python
from tiferet.interfaces.core import ServiceError
from tiferet.utils.sqlite import SQLITE_STATEMENT_FAILED_ID

try:
    with self.sqlite_service as db:
        db.execute('INSERT INTO users (email) VALUES (?)', (email,))
except ServiceError as e:
    if e.error_code == SQLITE_STATEMENT_FAILED_ID and 'UNIQUE' in str(e.__cause__):
        self.raise_error(a.error.USER_ALREADY_EXISTS_ID, email=email)
    raise
```

## Testing tip (very common pattern)

```python
def test_record_visit_creates_table_and_row(tmp_path):
    db_path = tmp_path / "visits.db"

    count = DomainEvent.handle(
        RecordVisit,
        db_path=str(db_path),
        page="/home"
    )

    assert count == 1

    with Sqlite(db_path, mode="ro") as db:
        assert db.fetch_one("SELECT page FROM visits")[0] == "/home"
```

## Quick reminders – how SqliteClient is different

- Returns `self` on `__enter__` (not a file object)  
- Auto-commits on clean exit, auto-rolls back on exception  
- Uses SQLite URI modes (`ro`/`rw`/`rwc`) instead of classic file modes  
- Implements `SqliteService` — the only utility that does this  
- No `encoding` or `newline` parameters (not meaningful for SQLite)

## Boundaries

**Inside this domain:** the SQLite connection lifecycle, statement/query execution, transactions, and backups, plus the driver-exception-to-`ServiceError` wrapping.
**Outside this domain:** the inherited file/path handling ([docs/guides/utils/file.md](file.md)); domain semantics for a specific driver failure code (the calling event's responsibility, not this client's — see the constraint-violation example above); domain-object persistence via a repository ([docs/guides/repos.md](../repos.md)).

## Related reading

- [FileLoader guide](../file.md) – the parent class everyone inherits from  
- [docs/guides/utils.md](../utils.md) – Utils layer strategy guide  
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/utils.md) – full utilities architecture  
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/interfaces.md) – `SqliteService` contract  
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/events.md) – domain events & testing patterns  
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md) – formatting & artifact comments

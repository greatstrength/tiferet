# Utilities – SqliteClient (alias: Sqlite)

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** March 02, 2026  
**Version:** 2.0.0a1

## Overview

`SqliteClient` is Tiferet’s friendly, safe way to work with SQLite databases.  
It builds directly on top of `FileLoader` (so it gets all the path handling and context-manager goodness for free), then adds everything you need for real database work: connections, queries, transactions, backups, and clean error handling.

What makes `SqliteClient` special compared to the other file utilities (`Yaml`, `Json`, `Csv`)?  
It also implements the full `SqliteService` interface — which means you can inject it into domain events and repositories exactly the same way you inject other services.  
At the same time, you can still use it directly (with or without the alias `Sqlite`) for quick scripts, tests, or simple one-off operations inside events.

The context manager is especially helpful here:  
- Everything inside the `with` block either succeeds completely (auto-commit)  
- or fails safely (auto-rollback + connection closed)

## When should you reach for SqliteClient?

| Use case                                      | Best choice                                  | Why it fits                                                                 |
|-----------------------------------------------|----------------------------------------------|-----------------------------------------------------------------------------|
| Quick query or small script / test            | `with Sqlite(...) as db:`                    | Zero setup, immediate access                                                |
| Need to mock or swap database backends later  | Inject `SqliteService`                       | Follows dependency injection; easy to test & replace                        |
| Persistent domain objects (users, settings…)  | Use domain repository + injected service     | Keeps business logic clean and path-agnostic                                |
| One-time database backup                      | `source.backup(target)`                      | Built-in, safe, with proper error wrapping                                  |
| Enforce read-only access                      | `mode='ro'`                                  | SQLite itself prevents writes at connection level                           |

## Quick examples to get you started

```python
from tiferet.utils import Sqlite

# === In-memory database (great for tests and throwaway work) ===
with Sqlite() as db:                        # defaults to :memory:
    db.execute("CREATE TABLE pets (name TEXT, age INTEGER)")
    db.execute("INSERT INTO pets VALUES (?, ?)", ("Luna", 3))
    db.execute("SELECT * FROM pets WHERE age > 2")
    print(db.fetch_all())                   # → [('Luna', 3)]

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
    db.execute("SELECT value FROM config WHERE key = 'theme'")
    theme = db.fetch_one()[0]               # → 'dark'
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
- `executescript(sql_script)` → run several statements at once ( DDL + data usually)  
- `fetch_one()` → get next row (or `None`)  
- `fetch_all()` → get list of all remaining rows  
- `commit()` / `rollback()` → manual transaction control (rarely needed with context manager)  
- `backup(target_client)` → efficient page-by-page copy to another database

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
            db.execute("SELECT COUNT(*) FROM visits")
            return db.fetch_one()[0]
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
        db.execute("SELECT page FROM visits")
        assert db.fetch_one()[0] == "/home"
```

## Quick reminders – how SqliteClient is different

- Returns `self` on `__enter__` (not a file object)  
- Auto-commits on clean exit, auto-rolls back on exception  
- Uses SQLite URI modes (`ro`/`rw`/`rwc`) instead of classic file modes  
- Implements `SqliteService` — the only utility that does this  
- No `encoding` or `newline` parameters (not meaningful for SQLite)

## Related reading

- [FileLoader guide](../file.md) – the parent class everyone inherits from  
- [docs/core/utils.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/utils.md) – full utilities architecture  
- [docs/core/interfaces.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/interfaces.md) – `SqliteService` contract  
- [docs/core/events.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/events.md) – domain events & testing patterns  
- [docs/core/code_style.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/code_style.md) – formatting & artifact comments
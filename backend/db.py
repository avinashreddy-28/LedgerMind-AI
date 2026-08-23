"""
db.py — Database Layer for LedgerMind-AI
=========================================
Provides database connectivity via SQLAlchemy.

Supports two backends (chosen automatically):
    - **PostgreSQL** — used when DB_HOST is set in .env and the server
      is reachable.
    - **SQLite**     — automatic fallback when PostgreSQL is unavailable.
      Stores data in ``data/ledgermind.db`` within the project root.

Public API:
    get_engine()   – returns a reusable SQLAlchemy Engine.
    init_db()      – creates all tables (safe to call repeatedly).

Tables:
    invoices  – stores every invoice with its reconciliation status and
                an optional AI-generated explanation for unmatched entries.

Usage:
    from backend.db import get_engine, init_db
    init_db()                       # create tables if they don't exist
    engine = get_engine()           # use for pd.read_sql / pd.to_sql
"""

import os
import sys

# ---------------------------------------------------------------------------
# 1. Load environment variables from .env
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

# Resolve the project root (one level up from backend/).
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")

# Inject .env key-value pairs into os.environ so we can read DB creds below.
load_dotenv(dotenv_path)

# ---------------------------------------------------------------------------
# 2. Read database credentials from environment variables
# ---------------------------------------------------------------------------
# Each value falls back to a sensible default for local development.

DB_HOST = os.getenv("DB_HOST", "localhost")       # PostgreSQL server host
DB_PORT = os.getenv("DB_PORT", "5432")            # Default PostgreSQL port
DB_NAME = os.getenv("DB_NAME", "ledgermind")      # Target database name
DB_USER = os.getenv("DB_USER", "postgres")        # Database user
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres") # Database password

# ---------------------------------------------------------------------------
# 3. Build the SQLAlchemy Engine with automatic fallback
# ---------------------------------------------------------------------------
# We try PostgreSQL first.  If the server isn't reachable we fall back to
# a local SQLite file so the pipeline can still run without a DB server.

from sqlalchemy import create_engine, text

# PostgreSQL connection URL.
_PG_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLite fallback — stored inside the project's data/ directory.
_SQLITE_PATH = os.path.join(project_root, "data", "ledgermind.db")
_SQLITE_URL = f"sqlite:///{_SQLITE_PATH}"

# Track which backend is active (used for log messages).
_active_backend = "unknown"


def _create_engine():
    """
    Attempt to connect to PostgreSQL; fall back to SQLite on failure.

    Returns
    -------
    sqlalchemy.engine.Engine
    """
    global _active_backend

    # --- Try PostgreSQL first ---------------------------------------------
    try:
        engine = create_engine(_PG_URL, pool_pre_ping=True, connect_args={"connect_timeout": 1})
        # Issue a lightweight query to confirm the connection is alive.
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _active_backend = "postgresql"
        return engine
    except Exception:
        # PostgreSQL is not available — fall back to SQLite.
        pass

    # --- Fallback: SQLite -------------------------------------------------
    # Ensure the data/ directory exists for the SQLite file.
    os.makedirs(os.path.dirname(_SQLITE_PATH), exist_ok=True)

    engine = create_engine(_SQLITE_URL, echo=False)
    _active_backend = "sqlite"
    return engine


# Create the singleton engine at module-load time.
_engine = _create_engine()


def get_engine():
    """
    Return the shared SQLAlchemy Engine instance.

    Use this when you need a connection for raw SQL or for pandas
    ``read_sql`` / ``to_sql`` operations.

    Returns
    -------
    sqlalchemy.engine.Engine
    """
    return _engine


# ---------------------------------------------------------------------------
# 4. Define the table schema using SQLAlchemy Core
# ---------------------------------------------------------------------------
from sqlalchemy import MetaData, Table, Column, String, Numeric, Text

# MetaData is a catalogue that holds all Table objects.
metadata = MetaData()

# Define the "invoices" table.
# - invoice_id : the human-readable invoice identifier (e.g. "INV003").
# - amount     : the invoice amount stored as a precise NUMERIC value.
# - status     : reconciliation outcome — either "MATCHED" or "UNMATCHED".
# - explanation: AI-generated reasoning for unmatched invoices (nullable,
#                because matched invoices don't need an explanation).

invoices_table = Table(
    "invoices",
    metadata,
    Column("invoice_id", String(50), primary_key=True),
    Column("amount", Numeric(15, 2), nullable=False),
    Column("status", String(20), nullable=False),
    Column("explanation", Text, nullable=True),
)


# ---------------------------------------------------------------------------
# 5. init_db() — create all tables
# ---------------------------------------------------------------------------

def init_db():
    """
    Create all tables defined in the metadata if they don't already exist.

    This uses ``CREATE TABLE IF NOT EXISTS`` under the hood, so it is safe
    to call multiple times — existing tables and data are never dropped.

    Raises
    ------
    sqlalchemy.exc.OperationalError
        If the database server is unreachable or the credentials are wrong.
    """
    # metadata.create_all() inspects the engine's target database and
    # creates any tables that are missing.  Tables that already exist
    # are silently skipped.
    metadata.create_all(_engine)


# ---------------------------------------------------------------------------
# Quick self-test — run with:  python -m backend.db
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console output.
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"🔗 Attempting database connection ...")
    print(f"   PostgreSQL target: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"   SQLite fallback:   {_SQLITE_PATH}")

    try:
        init_db()
        print(f"\n   Active backend: {_active_backend}")
    except Exception as e:
        print(f"❌ Failed to initialise database: {e}")
        sys.exit(1)

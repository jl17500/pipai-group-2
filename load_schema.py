"""Create the tables in schema.sql on the Railway Postgres database.

Reads DATABASE_URL from the environment, or from a .env file next to
this script. Running it again is safe. Existing rows are left in place.

    python load_schema.py
"""

import os
from pathlib import Path

import psycopg
from psycopg import ClientCursor

TABLES = ("scent_ratings",)


def database_url():
    url = os.environ.get("DATABASE_URL")
    if url:
        return url.strip()
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        raise SystemExit("Set DATABASE_URL, or put it in .env.")
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        key = key.strip().lower().replace(" ", "_")
        if key in {"database_url", "databaseurl"}:
            return value.strip().strip("'\"")
    raise SystemExit(".env has no DATABASE_URL.")


def main():
    url = database_url()
    if "railway.internal" in url:
        raise SystemExit(
            "That URL only works inside Railway. Use the public database URL."
        )

    sql = Path(__file__).with_name("schema.sql").read_text()
    with psycopg.connect(url, cursor_factory=ClientCursor) as conn:
        conn.execute(sql)
        for table in TABLES:
            count = conn.execute(f"select count(*) from {table}").fetchone()[0]
            print(f"{table}: {count} rows")


if __name__ == "__main__":
    main()

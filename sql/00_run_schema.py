"""
00_run_schema.py — Executes schema and index SQL files against Stylerizz DB.
Run from project root:  python sql/00_run_schema.py
"""
import mysql.connector
from pathlib import Path
import sys

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "stylerizz_analytics",
    "port": 3306,
    "charset": "utf8mb4",
    "use_pure": True,
    "autocommit": True,
    "raise_on_warnings": False,
}


def execute_sql_file(cursor, filepath: Path):
    print(f"\n▶ Running: {filepath.name}")
    sql_text = filepath.read_text(encoding="utf-8")

    # Split on ';' at end of line, ignore comments
    statements = []
    buffer = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("#"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(buffer).strip().rstrip(";").strip()
            if stmt:
                statements.append(stmt)
            buffer = []

    ok, fail = 0, 0
    for stmt in statements:
        try:
            cursor.execute(stmt)
            ok += 1
        except mysql.connector.Error as e:
            # Ignore "index already exists" errors on re-runs
            if e.errno in (1061, 1826):   # dup key name / dup FK
                continue
            fail += 1
            print(f"  ❌ {e.errno}: {e.msg[:120]}")
            print(f"     → {stmt[:80]}...")

    print(f"  ✅ {ok} statements OK  |  ❌ {fail} failed")


def main():
    here = Path(__file__).resolve().parent

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("✅ Connected to stylerizz_analytics")
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    for fname in ["01_schema.sql", "02_indexes.sql"]:
        path = here / fname
        if not path.exists():
            print(f"⚠️  Missing {fname}, skipping")
            continue
        execute_sql_file(cur, path)

    # Verify
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = 'stylerizz_analytics'
    """)
    count = cur.fetchone()[0]
    print(f"\n🎉 DONE — {count} tables exist in stylerizz_analytics")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
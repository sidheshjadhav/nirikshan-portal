"""
Sets up paimana.db (SQLite) — the transactional store for:
  - users         (login accounts for Government Official / Agency / Contractor)
  - messages      (official -> agency -> contractor communication)
  - delay_updates (contractor-submitted delay/progress reports)

Project/analytics data stays in dataset.csv (read via pandas for the ML
layer) — this DB only holds user-generated, transactional data, which is a
realistic split between an OLTP store and an analytics store.

Run this once (`python3 init_db.py`) before starting the server, or just
let main.py call it automatically on startup (it's idempotent — safe to
run multiple times; existing users/messages are never wiped).
"""
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "paimana.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # scope_value meaning depends on role:
    #   official   -> state name (their assigned location)
    #   agency     -> implementing_agency name
    #   contractor -> contractor_name
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            login_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            designation TEXT,
            password TEXT NOT NULL,
            scope_value TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_role TEXT NOT NULL,
            from_name TEXT NOT NULL,
            to_role TEXT NOT NULL,
            to_target TEXT NOT NULL,
            project_id TEXT,
            body TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS delay_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            contractor_name TEXT NOT NULL,
            update_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS monthly_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            project_name TEXT,
            reported_by TEXT NOT NULL,
            agency_name TEXT NOT NULL,
            physical_progress_pct REAL NOT NULL,
            expenditure_cr REAL NOT NULL,
            status TEXT NOT NULL,
            bottleneck_reason TEXT,
            mitigation_plan TEXT,
            target_completion_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            login_id TEXT NOT NULL,
            name TEXT NOT NULL,
            designation TEXT,
            scope_value TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def seed_demo_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.csv")
    df = pd.read_csv(dataset_path, keep_default_na=False)

    top_states = df["state"].value_counts().head(5).index.tolist()
    top_agencies = df["implementing_agency"].value_counts().head(5).index.tolist()
    top_contractors = df["contractor_name"].value_counts().head(5).index.tolist()

    demo_users = [
        ("minister", "MIN1001", "Shri Nitin Gadkari", "Union Minister, Ministry of Road Transport & Highways", "password123", "Road Transport & Highways"),
        ("mospi", "MOS1001", "Shri Alok Srivastava, IES", "Director General, MoSPI / IPMD", "password123", "National (All Projects)"),
        ("agency", "AGY2001", "Rajesh Verma", "Project Director, NHAI / ABC Infra Ltd.", "password123", "ABC Infrastructure Ltd."),
        ("official", "GOV1001", "Dr. Rajesh Kumar, IAS", "Principal Secretary / Senior Government Official", "password123", "National / State Oversight"),
        ("official", "OFF1001", "Shri S. Kumar", "State Project Officer | Maharashtra | Transport Sector", "password123", "Maharashtra"),
        ("admin", "ADM0001", "Smt. Sunita Rao", "Senior Director & Portal Administrator, NIC / MoSPI", "password123", "System Administration"),
        ("contractor", "CON3001", "L&T Infrastructure Lead", "Project Manager", "password123", "Larsen & Toubro Infra"),
    ]
    for idx, agency in enumerate(top_agencies):
        demo_users.append((
            "agency", f"AGY201{idx+1}", agency + " Regional Office", "Agency User",
            "password123", agency,
        ))
    for idx, contractor in enumerate(top_contractors):
        demo_users.append((
            "contractor", f"CON301{idx+1}", contractor, "Contractor",
            "password123", contractor,
        ))

    c.executemany(
        """INSERT OR REPLACE INTO users (role, login_id, name, designation, password, scope_value)
           VALUES (?, ?, ?, ?, ?, ?)""",
        demo_users,
    )
    conn.commit()
    conn.close()

    print("Seeded demo accounts (password for all: password123):")
    for role, login_id, name, designation, _, scope in demo_users:
        print(f"  {role:11s} | {login_id} | {name} | scope: {scope}")

    return {"official": list(zip([f"GOV100{i+1}" for i in range(5)], top_states)),
            "agency": list(zip([f"AGY200{i+1}" for i in range(5)], top_agencies)),
            "contractor": list(zip([f"CON300{i+1}" for i in range(5)], top_contractors))}


if __name__ == "__main__":
    init_db()
    seed_demo_users()
    print(f"\nDatabase ready at: {DB_PATH}")

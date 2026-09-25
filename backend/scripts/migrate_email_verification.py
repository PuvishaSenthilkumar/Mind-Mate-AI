"""
Database migration script for email verification feature.

Adds:
  - users.email_verified (boolean, default false)
  - users.email_verification_sent_at (datetime, nullable)
  - email_otps table

Run with: python scripts/migrate_email_verification.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect, text
from app.config import settings


def migrate():
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    inspector = inspect(engine)

    print("Running email verification migration...")

    with engine.begin() as conn:
        if "users" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("users")]
            if "email_verified" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0"))
                print("Added users.email_verified")
            if "email_verification_sent_at" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verification_sent_at DATETIME"))
                print("Added users.email_verification_sent_at")
        else:
            print("WARNING: users table not found, skipping column migration")

        if "email_otps" not in inspector.get_table_names():
            conn.execute(text("""
                CREATE TABLE email_otps (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    otp_code VARCHAR(6) NOT NULL,
                    purpose VARCHAR(20) NOT NULL DEFAULT 'verify',
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX ix_email_otps_email ON email_otps (email)"))
            print("Created email_otps table")

    print("Migration complete.")


if __name__ == "__main__":
    migrate()

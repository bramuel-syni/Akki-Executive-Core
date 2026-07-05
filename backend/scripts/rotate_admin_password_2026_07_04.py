"""One-shot rotation utility (2026-07-04): idempotent admin password rehash.

Reads ADMIN_SEED_PASSWORD from /app/backend/.env (loaded via python-dotenv) and
recomputes the bcrypt hash for admin@akki.ai in MongoDB. Safe to run repeatedly —
bcrypt.checkpw(env_pw, stored_hash) short-circuits when the hash already matches
(salt-invariant equivalence via re-verify).

Fingerprint-only emission per CREDENTIALS_NEVER_IN_CHANNEL_RULE:
  length + sha256_prefix (12 hex). No plaintext. No full hash.

Usage:
    python /app/backend/scripts/rotate_admin_password_2026_07_04.py
"""
from __future__ import annotations
import asyncio
import hashlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")


async def rotate() -> int:
    from motor.motor_asyncio import AsyncIOMotorClient

    from core import hash_password, verify_password  # type: ignore

    env_pw = os.environ.get("ADMIN_SEED_PASSWORD")
    if not env_pw:
        print("ERR ADMIN_SEED_PASSWORD not set in environment / .env", file=sys.stderr)
        return 2

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@akki.ai").lower()

    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    account = await db.accounts.find_one({"email": admin_email})
    if not account:
        print(f"ERR admin account {admin_email} not found in db.accounts", file=sys.stderr)
        client.close()
        return 3

    stored_hash = account.get("password_hash") or ""
    already_matches = bool(stored_hash) and verify_password(env_pw, stored_hash)

    if already_matches:
        outcome = "NO-OP (already-in-sync)"
    else:
        new_hash = hash_password(env_pw)
        await db.accounts.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": new_hash}},
        )
        outcome = "REHASHED (drift-corrected)"

    # Fingerprint-only emission
    digest = hashlib.sha256(env_pw.encode()).hexdigest()
    print(
        f"rotate_admin_password: {outcome} · "
        f"admin_email={admin_email} · "
        f"fingerprint length={len(env_pw)} sha256_prefix={digest[:12]}"
    )
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(rotate()))

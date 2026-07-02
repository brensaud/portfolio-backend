"""
CLI utility: generate a bcrypt hash for the ADMIN_PASSWORD_HASH environment variable.

Usage:
    python -m app.cli.hash_password

The tool prompts for the password twice (no echo) and prints the bcrypt hash
ready to paste into the deployment environment.

Security: uses cost factor 12 (≈ 0.4 s per verification on modern hardware).
"""

from __future__ import annotations

import getpass
import sys


def main() -> None:
    print("Admin password hash generator")
    print("=" * 32)
    print("This hash must be stored in the ADMIN_PASSWORD_HASH environment variable.\n")

    try:
        password = getpass.getpass("Enter new admin password: ")
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)

    if not password:
        print("Error: password cannot be empty.", file=sys.stderr)
        sys.exit(1)

    if len(password) < 12:
        print("Warning: password is shorter than 12 characters.", file=sys.stderr)

    try:
        confirm = getpass.getpass("Confirm password: ")
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)

    if password != confirm:
        print("Error: passwords do not match.", file=sys.stderr)
        sys.exit(1)

    # Import here so the module is importable even without passlib installed
    # (e.g. in environments where only --no-dev deps are installed).
    try:
        from app.core.admin_auth import hash_password
    except ImportError as exc:
        print(f"Error: could not import hash_password — is bcrypt installed?\n{exc}", file=sys.stderr)
        sys.exit(1)

    print("\nGenerating bcrypt hash (this may take a moment)...")
    hashed = hash_password(password)

    print("\n--- ADMIN_PASSWORD_HASH ---")
    print(hashed)
    print("-" * 30)
    print("\nSet this value as ADMIN_PASSWORD_HASH in your production environment.")


if __name__ == "__main__":
    main()

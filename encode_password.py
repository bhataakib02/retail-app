#!/usr/bin/env python3
"""
Helper script to URL-encode database password for connection string
"""
from urllib.parse import quote_plus

# Your password
password = "B!@ckB1rD@$&85"

# URL encode the password
encoded_password = quote_plus(password)

print("=" * 60)
print("DATABASE_URL Connection String Helper")
print("=" * 60)
print(f"\nOriginal password: {password}")
print(f"URL-encoded password: {encoded_password}")
print("\nFull DATABASE_URL:")
print(f"postgresql://postgres:{encoded_password}@db.wfcxwbmxvseweajyenzj.supabase.co:5432/postgres")
print("\n" + "=" * 60)
print("\nCopy this DATABASE_URL and use it in Vercel environment variables!")
print("=" * 60)


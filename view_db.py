#!/usr/bin/env python3
"""View SQLite database contents."""

import sqlite3
import json
from datetime import datetime

def view_database(db_path='dev_pulse.db'):
    """View contents of SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Show all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table['name']}")
    
    # Show cache table info
    print("\n=== Cache Table Info ===")
    cursor.execute("SELECT COUNT(*) as count FROM cache")
    count = cursor.fetchone()['count']
    print(f"Total entries: {count}")
    
    # Show schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='cache'")
    schema = cursor.fetchone()['sql']
    print(f"\nSchema:\n{schema}")
    
    # Show sample data
    print("\n=== Sample Data (first 5 entries) ===")
    cursor.execute("""
        SELECT id, cache_key, endpoint, created_at, expires_at 
        FROM cache 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"\nID: {row['id']}")
        print(f"Endpoint: {row['endpoint']}")
        print(f"Created: {row['created_at']}")
        print(f"Expires: {row['expires_at']}")
        print(f"Key: {row['cache_key'][:50]}...")
    
    # Show statistics by endpoint
    print("\n=== Statistics by Endpoint ===")
    cursor.execute("""
        SELECT endpoint, COUNT(*) as count,
               MIN(created_at) as oldest,
               MAX(created_at) as newest
        FROM cache
        GROUP BY endpoint
        ORDER BY count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"{row['endpoint']}: {row['count']} entries")
    
    # Check expired entries
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM cache 
        WHERE expires_at < datetime('now')
    """)
    expired = cursor.fetchone()['count']
    print(f"\nExpired entries: {expired}")
    
    conn.close()

if __name__ == '__main__':
    view_database()
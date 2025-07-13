#!/usr/bin/env python3
"""
Database initialization script for InsightVault backend.
Run this after branch merges or when the database is missing.
"""

import asyncio
import os
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, close_db
from app.models import Base
from sqlalchemy import create_engine

async def initialize_database():
    """Initialize the database with all tables."""
    print("Initializing InsightVault database...")
    
    try:
        # Initialize async database
        await init_db()
        print("[SUCCESS] Database tables created successfully!")
        
        # Close database connections
        await close_db()
        print("[SUCCESS] Database initialization complete!")
        
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(initialize_database())
    if success:
        print("\n[SUCCESS] Database is ready! You can now start the backend server.")
    else:
        print("\n[ERROR] Database initialization failed. Please check the error above.")
        sys.exit(1) 
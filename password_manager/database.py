"""
@Author: Henve
@Date: 2025/4/15 14:31
@File: database.py
@Description: 
"""
import sqlite3
import os
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_path: str = "passwords.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize database tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # 创建主密码表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_password (
            id INTEGER PRIMARY KEY,
            salt BLOB NOT NULL,
            hashed_password BLOB NOT NULL
        )
        """)

        # 创建分类表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            parent_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES categories(id)
        )
        """)

        # 创建密码条目表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            url TEXT,
            username TEXT,
            encrypted_password BLOB NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
        """)

        self.conn.commit()

    def is_first_run(self) -> bool:
        """Check if this is the first run of the application"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_password")
        return cursor.fetchone()[0] == 0

    def set_master_password(self, salt: bytes, hashed_password: bytes) -> None:
        """Set the master password"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM master_password")
        cursor.execute(
            "INSERT INTO master_password (salt, hashed_password) VALUES (?, ?)",
            (salt, hashed_password)
        )
        self.conn.commit()

    def get_master_password(self) -> Optional[tuple]:
        """Get the stored master password data"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT salt, hashed_password FROM master_password LIMIT 1")
        return cursor.fetchone()

    def add_password_entry(self, entry: Dict) -> int:
        """Add a new password entry"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO password_entries 
        (category_id, name, url, username, encrypted_password, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry['category_id'],
            entry['name'],
            entry['url'],
            entry['username'],
            entry['encrypted_password'],
            entry['notes']
        ))
        self.conn.commit()
        return cursor.lastrowid

    def update_password_entry(self, entry_id: int, entry: Dict) -> None:
        """Update an existing password entry"""
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE password_entries 
        SET category_id = ?, name = ?, url = ?, username = ?, 
            encrypted_password = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (
            entry['category_id'],
            entry['name'],
            entry['url'],
            entry['username'],
            entry['encrypted_password'],
            entry['notes'],
            entry_id
        ))
        self.conn.commit()

    def delete_password_entry(self, entry_id: int) -> None:
        """Delete a password entry"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM password_entries WHERE id = ?", (entry_id,))
        self.conn.commit()

    def get_password_entries(self, search_term: str = None) -> List[Dict]:
        """Get all password entries, optionally filtered by search term"""
        cursor = self.conn.cursor()

        if search_term:
            search_term = f"%{search_term}%"
            cursor.execute("""
            SELECT id, category_id, name, url, username, encrypted_password, notes
            FROM password_entries
            WHERE name LIKE ? OR url LIKE ? OR username LIKE ? OR notes LIKE ?
            ORDER BY name
            """, (search_term, search_term, search_term, search_term))
        else:
            cursor.execute("""
            SELECT id, category_id, name, url, username, encrypted_password, notes
            FROM password_entries
            ORDER BY name
            """)

        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_category(self, name: str, parent_id: int = None) -> int:
        """Add a new category"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO categories (name, parent_id) VALUES (?, ?)
        """, (name, parent_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_categories(self) -> List[Dict]:
        """Get all categories"""
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, name, parent_id FROM categories ORDER BY name
        """)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self) -> None:
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def export_data(self, export_path: str) -> None:
        """Export database to a file for migration"""
        import shutil
        shutil.copy2(self.db_path, export_path)

    def import_data(self, import_path: str) -> None:
        """Import database from a file for migration"""
        self.close()
        import shutil
        shutil.copy2(import_path, self.db_path)
        self.conn = sqlite3.connect(self.db_path)
"""
Database handler for ATS Bot
SQLite database to store JD and resumes
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class Database:
    """SQLite Database Handler"""
    
    def __init__(self, db_path: str = None):
        """Initialize database"""
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create JD table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create Resumes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                image_count INTEGER DEFAULT 0,
                image_details TEXT DEFAULT '',
                image_paths TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ensure new columns exist on older databases
        self._ensure_resume_image_columns(cursor)
        
        # Create Analysis Cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _ensure_resume_image_columns(self, cursor):
        """Add image metadata columns to resumes if missing."""
        cursor.execute('PRAGMA table_info(resumes)')
        columns = [row[1] for row in cursor.fetchall()]
        if 'image_count' not in columns:
            cursor.execute('ALTER TABLE resumes ADD COLUMN image_count INTEGER DEFAULT 0')
        if 'image_details' not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN image_details TEXT DEFAULT ''")
        if 'image_paths' not in columns:
            cursor.execute("ALTER TABLE resumes ADD COLUMN image_paths TEXT DEFAULT ''")
    
    def save_jd(self, content: str, filename: str) -> bool:
        """Save or update JD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing JD (only one JD at a time)
            cursor.execute('DELETE FROM job_descriptions')
            
            # Insert new JD
            cursor.execute('''
                INSERT INTO job_descriptions (filename, content)
                VALUES (?, ?)
            ''', (filename, content))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error saving JD: {str(e)}")
            return False
    
    def get_jd(self) -> Optional[str]:
        """Get current JD content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT content FROM job_descriptions ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Error getting JD: {str(e)}")
            return None
    
    def get_jd_filename(self) -> Optional[str]:
        """Get JD filename"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT filename FROM job_descriptions ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Error getting JD filename: {str(e)}")
            return None
    
    def save_resume(self, content: str, filename: str, image_count: int = 0, image_details: str = '', image_paths: str = '') -> bool:
        """Save resume with optional image metadata."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if resume already exists
            cursor.execute('SELECT id FROM resumes WHERE filename = ?', (filename,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE resumes SET content = ?, image_count = ?, image_details = ?, image_paths = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE filename = ?
                ''', (content, image_count, image_details, image_paths, filename))
            else:
                cursor.execute('''
                    INSERT INTO resumes (filename, content, image_count, image_details, image_paths)
                    VALUES (?, ?, ?, ?, ?)
                ''', (filename, content, image_count, image_details, image_paths))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error saving resume: {str(e)}")
            return False
    
    def get_resume(self, filename: str) -> Optional[str]:
        """Get specific resume content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT content FROM resumes WHERE filename = ?', (filename,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Error getting resume: {str(e)}")
            return None

    def get_resume_info(self) -> list:
        """Get all resume metadata along with image information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT filename, image_count, image_details, image_paths FROM resumes ORDER BY created_at DESC')
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'filename': filename,
                    'image_count': image_count,
                    'image_details': image_details or '',
                    'image_paths': json.loads(image_paths or '[]')
                }
                for filename, image_count, image_details, image_paths in results
            ] if results else []
        except Exception as e:
            print(f"❌ Error getting resume info: {str(e)}")
            return []
    
    def get_all_resumes(self) -> Dict[str, str]:
        """Get all resumes as dictionary {filename: content}"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT filename, content FROM resumes')
            results = cursor.fetchall()
            conn.close()
            
            return {filename: content for filename, content in results} if results else {}
        except Exception as e:
            print(f"❌ Error getting all resumes: {str(e)}")
            return {}
    
    def get_resume_filenames(self) -> List[str]:
        """Get all resume filenames"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT filename FROM resumes ORDER BY created_at DESC')
            results = cursor.fetchall()
            conn.close()
            
            return [r[0] for r in results] if results else []
        except Exception as e:
            print(f"❌ Error getting resume filenames: {str(e)}")
            return []

    def get_resume_images(self) -> list:
        """Get stored image paths for resumes that contain images."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT filename, image_paths FROM resumes WHERE image_count > 0 ORDER BY created_at DESC')
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'filename': filename,
                    'image_paths': json.loads(image_paths or '[]')
                }
                for filename, image_paths in results
            ] if results else []
        except Exception as e:
            print(f"❌ Error getting resume images: {str(e)}")
            return []
    
    def delete_resume(self, filename: str) -> bool:
        """Delete specific resume"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM resumes WHERE filename = ?', (filename,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error deleting resume: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM job_descriptions')
            cursor.execute('DELETE FROM resumes')
            cursor.execute('DELETE FROM analysis_cache')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error clearing database: {str(e)}")
            return False
    
    def cache_analysis(self, query_type: str, result: str) -> bool:
        """Cache analysis results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_cache (query_type, result)
                VALUES (?, ?)
            ''', (query_type, result))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error caching analysis: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM job_descriptions')
            jd_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM resumes')
            resume_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM analysis_cache')
            cache_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'jd_count': jd_count,
                'resume_count': resume_count,
                'cache_count': cache_count
            }
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            return {}

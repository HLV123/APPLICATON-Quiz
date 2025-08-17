"""Database migrations for schema changes."""
import sqlite3
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from ..utils.logger import Logger
from .connection import DatabaseManager

class Migration:
    """Base migration class."""
    
    def __init__(self, version: str, description: str):
        """
        Initialize migration.
        
        Args:
            version: Migration version (e.g., "001", "002")
            description: Migration description
        """
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self, conn: sqlite3.Connection) -> None:
        """Apply migration (override in subclass)."""
        raise NotImplementedError("Subclasses must implement up() method")
    
    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback migration (override in subclass)."""
        raise NotImplementedError("Subclasses must implement down() method")
    
    def __str__(self) -> str:
        """String representation."""
        return f"Migration {self.version}: {self.description}"

class MigrationManager:
    """Database migration manager."""
    
    def __init__(self):
        """Initialize migration manager."""
        self.db = DatabaseManager()
        self.logger = Logger(__name__)
        self.migrations: List[Migration] = []
        
        # Register all migrations
        self._register_migrations()
    
    def _register_migrations(self):
        """Register all available migrations."""
        # Migration 001: Initial schema
        self.migrations.append(InitialSchemaMigration())
        
        # Migration 002: Add indexes
        self.migrations.append(AddIndexesMigration())
        
        # Migration 003: Add tags column
        self.migrations.append(AddTagsColumnMigration())
        
        # Migration 004: Add difficulty levels
        self.migrations.append(AddDifficultyLevelsMigration())
        
        # Migration 005: Add quiz results tracking
        self.migrations.append(AddQuizResultsTrackingMigration())
        
        # Sort migrations by version
        self.migrations.sort(key=lambda m: m.version)
    
    def create_migrations_table(self):
        """Create migrations tracking table."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version TEXT PRIMARY KEY,
                        description TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        execution_time_ms INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()
                self.logger.info("Migrations table created")
        except Exception as e:
            self.logger.error(f"Failed to create migrations table: {e}")
            raise
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT version FROM schema_migrations ORDER BY version')
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Migrations table doesn't exist yet
            return []
        except Exception as e:
            self.logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        return [m for m in self.migrations if m.version not in applied]
    
    def apply_migration(self, migration: Migration) -> bool:
        """
        Apply a single migration.
        
        Args:
            migration: Migration to apply
            
        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.now()
        
        try:
            with self.db.get_connection() as conn:
                # Begin transaction
                conn.execute('BEGIN')
                
                try:
                    # Apply migration
                    self.logger.info(f"Applying migration: {migration}")
                    migration.up(conn)
                    
                    # Record migration
                    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO schema_migrations (version, description, execution_time_ms)
                        VALUES (?, ?, ?)
                    ''', (migration.version, migration.description, execution_time))
                    
                    # Commit transaction
                    conn.commit()
                    
                    self.logger.info(f"Migration {migration.version} applied successfully in {execution_time}ms")
                    return True
                    
                except Exception as e:
                    # Rollback on error
                    conn.rollback()
                    self.logger.error(f"Migration {migration.version} failed: {e}")
                    raise
                    
        except Exception as e:
            self.logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False
    
    def rollback_migration(self, migration: Migration) -> bool:
        """
        Rollback a single migration.
        
        Args:
            migration: Migration to rollback
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                # Begin transaction
                conn.execute('BEGIN')
                
                try:
                    # Rollback migration
                    self.logger.info(f"Rolling back migration: {migration}")
                    migration.down(conn)
                    
                    # Remove migration record
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM schema_migrations WHERE version = ?', (migration.version,))
                    
                    # Commit transaction
                    conn.commit()
                    
                    self.logger.info(f"Migration {migration.version} rolled back successfully")
                    return True
                    
                except Exception as e:
                    # Rollback on error
                    conn.rollback()
                    self.logger.error(f"Migration rollback {migration.version} failed: {e}")
                    raise
                    
        except Exception as e:
            self.logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False
    
    def migrate(self) -> bool:
        """
        Apply all pending migrations.
        
        Returns:
            True if all migrations successful, False otherwise
        """
        try:
            # Ensure migrations table exists
            self.create_migrations_table()
            
            # Get pending migrations
            pending = self.get_pending_migrations()
            
            if not pending:
                self.logger.info("No pending migrations")
                return True
            
            self.logger.info(f"Applying {len(pending)} pending migrations")
            
            # Apply each pending migration
            for migration in pending:
                if not self.apply_migration(migration):
                    self.logger.error(f"Migration process stopped at {migration.version}")
                    return False
            
            self.logger.info("All migrations applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration process failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            applied = self.get_applied_migrations()
            pending = self.get_pending_migrations()
            
            return {
                'total_migrations': len(self.migrations),
                'applied_count': len(applied),
                'pending_count': len(pending),
                'applied_versions': applied,
                'pending_versions': [m.version for m in pending],
                'latest_version': applied[-1] if applied else None,
                'is_up_to_date': len(pending) == 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return {}
    
    def reset_database(self) -> bool:
        """Reset database by dropping all tables and reapplying migrations."""
        try:
            self.logger.warning("Resetting database - all data will be lost!")
            
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Drop all tables
                for table in tables:
                    if table != 'sqlite_sequence':  # Don't drop SQLite internal table
                        cursor.execute(f'DROP TABLE IF EXISTS {table}')
                
                conn.commit()
                self.logger.info("All tables dropped")
            
            # Reapply all migrations
            return self.migrate()
            
        except Exception as e:
            self.logger.error(f"Failed to reset database: {e}")
            return False

# ===========================================
# Concrete Migration Classes
# ===========================================

class InitialSchemaMigration(Migration):
    """Initial database schema migration."""
    
    def __init__(self):
        super().__init__("001", "Create initial schema with questions and users tables")
    
    def up(self, conn: sqlite3.Connection):
        """Create initial tables."""
        cursor = conn.cursor()
        
        # Create questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                answer TEXT NOT NULL CHECK(answer IN ('A', 'B', 'C')),
                category TEXT DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
    
    def down(self, conn: sqlite3.Connection):
        """Drop initial tables."""
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS questions')
        cursor.execute('DROP TABLE IF EXISTS users')

class AddIndexesMigration(Migration):
    """Add database indexes for performance."""
    
    def __init__(self):
        super().__init__("002", "Add indexes for better query performance")
    
    def up(self, conn: sqlite3.Connection):
        """Create indexes."""
        cursor = conn.cursor()
        
        # Questions indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at)')
        
        # Users indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    
    def down(self, conn: sqlite3.Connection):
        """Drop indexes."""
        cursor = conn.cursor()
        cursor.execute('DROP INDEX IF EXISTS idx_questions_category')
        cursor.execute('DROP INDEX IF EXISTS idx_questions_created_at')
        cursor.execute('DROP INDEX IF EXISTS idx_users_username')
        cursor.execute('DROP INDEX IF EXISTS idx_users_role')

class AddTagsColumnMigration(Migration):
    """Add tags column to questions table."""
    
    def __init__(self):
        super().__init__("003", "Add tags column to questions table")
    
    def up(self, conn: sqlite3.Connection):
        """Add tags column."""
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE questions ADD COLUMN tags TEXT DEFAULT ""')
    
    def down(self, conn: sqlite3.Connection):
        """Remove tags column (SQLite doesn't support DROP COLUMN before 3.35.0)."""
        # Note: SQLite doesn't support dropping columns easily
        # This would require recreating the table without the column
        # For simplicity, we'll just clear the column data
        cursor = conn.cursor()
        cursor.execute('UPDATE questions SET tags = ""')

class AddDifficultyLevelsMigration(Migration):
    """Add difficulty levels to questions."""
    
    def __init__(self):
        super().__init__("004", "Add difficulty levels to questions")
    
    def up(self, conn: sqlite3.Connection):
        """Add difficulty column."""
        cursor = conn.cursor()
        cursor.execute('ALTER TABLE questions ADD COLUMN difficulty TEXT DEFAULT "Medium" CHECK(difficulty IN ("Easy", "Medium", "Hard"))')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty)')
    
    def down(self, conn: sqlite3.Connection):
        """Remove difficulty features."""
        cursor = conn.cursor()
        cursor.execute('DROP INDEX IF EXISTS idx_questions_difficulty')
        # Clear difficulty data (can't drop column easily in SQLite)
        cursor.execute('UPDATE questions SET difficulty = "Medium"')

class AddQuizResultsTrackingMigration(Migration):
    """Add quiz results tracking table."""
    
    def __init__(self):
        super().__init__("005", "Add quiz results tracking system")
    
    def up(self, conn: sqlite3.Connection):
        """Create quiz results table."""
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                time_taken INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                questions_attempted TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Add indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quiz_results_user ON quiz_results(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quiz_results_completed ON quiz_results(completed_at)')
    
    def down(self, conn: sqlite3.Connection):
        """Drop quiz results table."""
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS quiz_results')

# ===========================================
# Utility Functions
# ===========================================

def run_migrations():
    """Run all pending migrations."""
    manager = MigrationManager()
    return manager.migrate()

def get_migration_status():
    """Get current migration status."""
    manager = MigrationManager()
    return manager.get_migration_status()

def reset_database():
    """Reset database completely."""
    manager = MigrationManager()
    return manager.reset_database()

def create_sample_migration(version: str, description: str) -> str:
    """
    Create a sample migration template.
    
    Args:
        version: Migration version
        description: Migration description
        
    Returns:
        Migration class template as string
    """
    template = f'''
class Migration{version}(Migration):
    """{description}"""
    
    def __init__(self):
        super().__init__("{version}", "{description}")
    
    def up(self, conn: sqlite3.Connection):
        """Apply migration."""
        cursor = conn.cursor()
        # Add your migration code here
        # cursor.execute("ALTER TABLE ...")
        pass
    
    def down(self, conn: sqlite3.Connection):
        """Rollback migration."""
        cursor = conn.cursor()
        # Add your rollback code here
        # cursor.execute("DROP TABLE ...")
        pass
'''
    return template.strip()

if __name__ == "__main__":
    # Command line interface for migrations
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrations.py [migrate|status|reset]")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = MigrationManager()
    
    if command == "migrate":
        print("Running migrations...")
        success = manager.migrate()
        print("✅ Migrations completed successfully!" if success else "❌ Migration failed!")
        
    elif command == "status":
        print("Migration Status:")
        status = manager.get_migration_status()
        print(f"Total migrations: {status.get('total_migrations', 0)}")
        print(f"Applied: {status.get('applied_count', 0)}")
        print(f"Pending: {status.get('pending_count', 0)}")
        print(f"Up to date: {'Yes' if status.get('is_up_to_date') else 'No'}")
        
    elif command == "reset":
        print("⚠️  WARNING: This will delete all data!")
        confirm = input("Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            success = manager.reset_database()
            print("✅ Database reset successfully!" if success else "❌ Reset failed!")
        else:
            print("Reset cancelled.")
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
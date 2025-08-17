"""Database connection management."""
import sqlite3
import threading
from typing import Optional, Any, Dict, List, Tuple
from contextlib import contextmanager
from ..utils.logger import Logger
from ..config.settings import Config

class DatabaseManager:
    """Singleton database manager for SQLite connections."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize database manager."""
        if self._initialized:
            return
            
        self.db_path = Config.DATABASE_PATH
        self.logger = Logger(__name__)
        self._local = threading.local()
        self._initialized = True
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database with tables."""
        try:
            with self.get_connection() as conn:
                self._create_tables(conn)
                self._insert_sample_data(conn)
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables."""
        cursor = conn.cursor()
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                answer TEXT NOT NULL CHECK(answer IN ('A', 'B', 'C')),
                category TEXT DEFAULT 'General',
                difficulty TEXT DEFAULT 'Medium' CHECK(difficulty IN ('Easy', 'Medium', 'Hard')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT DEFAULT ''
            )
        ''')
        
        # Users table
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
        
        # Quiz results table
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
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quiz_results_user ON quiz_results(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_quiz_results_completed ON quiz_results(completed_at)')
        
        conn.commit()
    
    def _insert_sample_data(self, conn: sqlite3.Connection):
        """Insert sample data if tables are empty."""
        cursor = conn.cursor()
        
        # Check if questions exist
        cursor.execute('SELECT COUNT(*) FROM questions')
        if cursor.fetchone()[0] == 0:
            sample_questions = [
                ("Python được phát hành lần đầu vào năm nào?", 
                 "A. 1989", "B. 1991", "C. 1995", "B", "Python", "Easy", "python,history"),
                ("Ai là cha đẻ của ngôn ngữ Python?", 
                 "A. Guido van Rossum", "B. Bill Gates", "C. Linus Torvalds", "A", "Python", "Easy", "python,creator"),
                ("Thư viện nào được sử dụng để làm việc với mảng trong Python?", 
                 "A. Pandas", "B. NumPy", "C. Matplotlib", "B", "Python", "Medium", "python,libraries"),
                ("Phương thức nào được sử dụng để thêm phần tử vào cuối list?", 
                 "A. append()", "B. insert()", "C. extend()", "A", "Python", "Easy", "python,list"),
                ("Trong Python, từ khóa nào được sử dụng để định nghĩa hàm?", 
                 "A. function", "B. def", "C. func", "B", "Python", "Easy", "python,syntax"),
                ("Cấu trúc dữ liệu nào trong Python là có thứ tự và có thể thay đổi?", 
                 "A. tuple", "B. set", "C. list", "C", "Python", "Medium", "python,data-structures"),
                ("Phương thức nào được sử dụng để chuyển đổi string thành chữ hoa?", 
                 "A. upper()", "B. capitalize()", "C. title()", "A", "Python", "Easy", "python,string"),
                ("Từ khóa nào được sử dụng để xử lý ngoại lệ trong Python?", 
                 "A. catch", "B. except", "C. handle", "B", "Python", "Medium", "python,exception"),
            ]
            
            cursor.executemany('''
                INSERT INTO questions (prompt, option_a, option_b, option_c, answer, category, difficulty, tags) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_questions)
        
        # Check if admin user exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            # In a real app, password should be properly hashed
            cursor.execute('''
                INSERT INTO users (username, password_hash, role) 
                VALUES (?, ?, ?)
            ''', ('admin', 'admin123', 'admin'))  # Simple password for demo
        
        conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign keys
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """Execute SELECT query and return results."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Update execution failed: {e}")
            raise
    
    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT query and return last insert ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Insert execution failed: {e}")
            raise
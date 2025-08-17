"""Repository pattern for database operations."""
from typing import List, Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod
from ..models.question import Question
from ..models.user import User, QuizResult
from .connection import DatabaseManager
from ..utils.logger import Logger

class BaseRepository(ABC):
    """Base repository class."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.logger = Logger(__name__)

class QuestionRepository(BaseRepository):
    """Repository for question operations."""
    
    def create(self, question: Question) -> int:
        """Create a new question."""
        try:
            query = '''
                INSERT INTO questions (prompt, option_a, option_b, option_c, answer, category, difficulty, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                question.prompt, question.option_a, question.option_b, question.option_c,
                question.answer, question.category, question.difficulty, 
                ','.join(question.tags) if question.tags else ''
            )
            question_id = self.db.execute_insert(query, params)
            self.logger.info(f"Created question with ID: {question_id}")
            return question_id
        except Exception as e:
            self.logger.error(f"Failed to create question: {e}")
            raise
    
    def get_by_id(self, question_id: int) -> Optional[Question]:
        """Get question by ID."""
        try:
            query = 'SELECT * FROM questions WHERE id = ?'
            rows = self.db.execute_query(query, (question_id,))
            if rows:
                return self._row_to_question(rows[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get question by ID {question_id}: {e}")
            return None
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Question]:
        """Get all questions with optional pagination."""
        try:
            query = 'SELECT * FROM questions ORDER BY created_at DESC'
            if limit:
                query += f' LIMIT {limit} OFFSET {offset}'
            
            rows = self.db.execute_query(query)
            return [self._row_to_question(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get all questions: {e}")
            return []
    
    def search(self, search_term: str, category: Optional[str] = None, 
               difficulty: Optional[str] = None) -> List[Question]:
        """Search questions by term, category, and difficulty."""
        try:
            query = '''
                SELECT * FROM questions 
                WHERE (prompt LIKE ? OR option_a LIKE ? OR option_b LIKE ? OR option_c LIKE ?)
            '''
            params = [f'%{search_term}%'] * 4
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            if difficulty:
                query += ' AND difficulty = ?'
                params.append(difficulty)
            
            query += ' ORDER BY created_at DESC'
            
            rows = self.db.execute_query(query, tuple(params))
            return [self._row_to_question(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to search questions: {e}")
            return []
    
    def update(self, question: Question) -> bool:
        """Update an existing question."""
        try:
            query = '''
                UPDATE questions 
                SET prompt = ?, option_a = ?, option_b = ?, option_c = ?, 
                    answer = ?, category = ?, difficulty = ?, tags = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            '''
            params = (
                question.prompt, question.option_a, question.option_b, question.option_c,
                question.answer, question.category, question.difficulty,
                ','.join(question.tags) if question.tags else '', question.id
            )
            affected_rows = self.db.execute_update(query, params)
            success = affected_rows > 0
            if success:
                self.logger.info(f"Updated question ID: {question.id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to update question: {e}")
            return False
    
    def delete(self, question_id: int) -> bool:
        """Delete a question by ID."""
        try:
            query = 'DELETE FROM questions WHERE id = ?'
            affected_rows = self.db.execute_update(query, (question_id,))
            success = affected_rows > 0
            if success:
                self.logger.info(f"Deleted question ID: {question_id}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete question: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        try:
            query = 'SELECT DISTINCT category FROM questions ORDER BY category'
            rows = self.db.execute_query(query)
            return [row['category'] for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            return []
    
    def get_random_questions(self, count: int, category: Optional[str] = None,
                           difficulty: Optional[str] = None) -> List[Question]:
        """Get random questions for quiz."""
        try:
            query = 'SELECT * FROM questions'
            params = []
            
            conditions = []
            if category:
                conditions.append('category = ?')
                params.append(category)
            
            if difficulty:
                conditions.append('difficulty = ?')
                params.append(difficulty)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY RANDOM() LIMIT ?'
            params.append(count)
            
            rows = self.db.execute_query(query, tuple(params))
            return [self._row_to_question(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get random questions: {e}")
            return []
    
    def get_count(self) -> int:
        """Get total number of questions."""
        try:
            query = 'SELECT COUNT(*) as count FROM questions'
            rows = self.db.execute_query(query)
            return rows[0]['count'] if rows else 0
        except Exception as e:
            self.logger.error(f"Failed to get question count: {e}")
            return 0
    
    def _row_to_question(self, row) -> Question:
        """Convert database row to Question object."""
        from datetime import datetime
        
        question = Question(
            id=row['id'],
            prompt=row['prompt'],
            option_a=row['option_a'],
            option_b=row['option_b'],
            option_c=row['option_c'],
            answer=row['answer'],
            category=row['category'],
            difficulty=row['difficulty']
        )
        
        # Handle datetime fields
        if row['created_at']:
            try:
                question.created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            except:
                question.created_at = datetime.now()
        
        if row['updated_at']:
            try:
                question.updated_at = datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00'))
            except:
                question.updated_at = datetime.now()
        
        # Handle tags
        if row['tags']:
            question.tags = [tag.strip() for tag in row['tags'].split(',') if tag.strip()]
        
        return question

class UserRepository(BaseRepository):
    """Repository for user operations."""
    
    def create(self, user: User) -> int:
        """Create a new user."""
        try:
            query = '''
                INSERT INTO users (username, password_hash, role, is_active)
                VALUES (?, ?, ?, ?)
            '''
            params = (user.username, user.password_hash, user.role, user.is_active)
            user_id = self.db.execute_insert(query, params)
            self.logger.info(f"Created user with ID: {user_id}")
            return user_id
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            raise
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            query = 'SELECT * FROM users WHERE username = ?'
            rows = self.db.execute_query(query, (username,))
            if rows:
                return self._row_to_user(rows[0])
            return None
        except Exception as e:
            self.logger.error(f"Failed to get user by username {username}: {e}")
            return None
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        try:
            user = self.get_by_username(username)
            if user and user.password_hash == password and user.is_active:
                # Update last login
                self.update_last_login(user.id)
                return user
            return None
        except Exception as e:
            self.logger.error(f"Authentication failed for {username}: {e}")
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?'
            affected_rows = self.db.execute_update(query, (user_id,))
            return affected_rows > 0
        except Exception as e:
            self.logger.error(f"Failed to update last login for user {user_id}: {e}")
            return False
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User object."""
        from datetime import datetime
        
        user = User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=row['role'],
            is_active=bool(row['is_active'])
        )
        
        # Handle datetime fields
        if row['created_at']:
            try:
                user.created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            except:
                user.created_at = datetime.now()
        
        if row['last_login']:
            try:
                user.last_login = datetime.fromisoformat(row['last_login'].replace('Z', '+00:00'))
            except:
                pass
        
        return user

class QuizResultRepository(BaseRepository):
    """Repository for quiz result operations."""
    
    def create(self, result: QuizResult) -> int:
        """Save quiz result."""
        try:
            query = '''
                INSERT INTO quiz_results (user_id, score, total_questions, time_taken, questions_attempted)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (
                result.user_id, result.score, result.total_questions, result.time_taken,
                ','.join(map(str, result.questions_attempted)) if result.questions_attempted else ''
            )
            result_id = self.db.execute_insert(query, params)
            self.logger.info(f"Saved quiz result with ID: {result_id}")
            return result_id
        except Exception as e:
            self.logger.error(f"Failed to save quiz result: {e}")
            raise
    
    def get_user_results(self, user_id: int, limit: int = 10) -> List[QuizResult]:
        """Get quiz results for a user."""
        try:
            query = '''
                SELECT * FROM quiz_results 
                WHERE user_id = ? 
                ORDER BY completed_at DESC 
                LIMIT ?
            '''
            rows = self.db.execute_query(query, (user_id, limit))
            return [self._row_to_result(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get user results: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get quiz statistics."""
        try:
            stats = {}
            
            # Total quizzes taken
            query = 'SELECT COUNT(*) as count FROM quiz_results'
            rows = self.db.execute_query(query)
            stats['total_quizzes'] = rows[0]['count'] if rows else 0
            
            # Average score
            query = 'SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score FROM quiz_results'
            rows = self.db.execute_query(query)
            stats['average_score'] = round(rows[0]['avg_score'] or 0, 2)
            
            # Best score
            query = 'SELECT MAX(CAST(score AS FLOAT) / total_questions * 100) as best_score FROM quiz_results'
            rows = self.db.execute_query(query)
            stats['best_score'] = round(rows[0]['best_score'] or 0, 2)
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def _row_to_result(self, row) -> QuizResult:
        """Convert database row to QuizResult object."""
        from datetime import datetime
        
        result = QuizResult(
            id=row['id'],
            user_id=row['user_id'],
            score=row['score'],
            total_questions=row['total_questions'],
            time_taken=row['time_taken']
        )
        
        # Handle datetime
        if row['completed_at']:
            try:
                result.completed_at = datetime.fromisoformat(row['completed_at'].replace('Z', '+00:00'))
            except:
                result.completed_at = datetime.now()
        
        # Handle questions attempted
        if row['questions_attempted']:
            try:
                result.questions_attempted = [
                    int(qid) for qid in row['questions_attempted'].split(',') 
                    if qid.strip()
                ]
            except:
                result.questions_attempted = []
        
        return result
    
    # Trong class QuizResultRepository, thêm phương thức:

    def get_latest_result(self, user_id: Optional[int] = None) -> Optional[QuizResult]:
        """
        Get the most recent quiz result.
    
        Args:
            user_id: User ID (None for all users)
        
        Returns:
            Latest quiz result or None
        """
        try:
            if user_id:
                query = '''
                    SELECT * FROM quiz_results 
                    WHERE user_id = ? 
                    ORDER BY completed_at DESC 
                    LIMIT 1
                '''
                rows = self.db.execute_query(query, (user_id,))
            else:
                query = '''
                    SELECT * FROM quiz_results 
                    ORDER BY completed_at DESC 
                    LIMIT 1
                '''
                rows = self.db.execute_query(query)
        
            if rows:
                return self._row_to_result(rows[0])
            return None
        
        except Exception as e:
            self.logger.error(f"Failed to get latest result: {e}")
            return None
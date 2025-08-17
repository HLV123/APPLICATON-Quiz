"""Admin service for managing questions and users."""
from typing import List, Optional, Dict, Any, Tuple
from ..models.question import Question
from ..models.user import User
from ..database.repository import QuestionRepository, UserRepository, QuizResultRepository
from ..utils.validators import InputValidator
from ..utils.logger import Logger

class AdminService:
    """Service class for admin operations."""
    
    def __init__(self):
        self.question_repo = QuestionRepository()
        self.user_repo = UserRepository()
        self.result_repo = QuizResultRepository()
        self.validator = InputValidator()
        self.logger = Logger(__name__)
    
    # Question Management
    def create_question(self, prompt: str, options: List[str], answer: str,
                       category: str = "General", difficulty: str = "Medium",
                       tags: List[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Create a new question.
        
        Args:
            prompt: Question text
            options: List of 3 options
            answer: Correct answer (A, B, or C)
            category: Question category
            difficulty: Question difficulty
            tags: List of tags
            
        Returns:
            Tuple of (success, message, question_id)
        """
        try:
            # Validate input
            is_valid, error_msg = self.validator.validate_question(prompt, options, answer, category)
            if not is_valid:
                return False, error_msg, None
            
            # Sanitize inputs
            prompt = self.validator.sanitize_input(prompt)
            options = [self.validator.sanitize_input(opt) for opt in options]
            category = self.validator.sanitize_input(category)
            
            # Create question object
            question = Question(
                prompt=prompt,
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                answer=answer,
                category=category or "General",
                difficulty=difficulty,
                tags=tags or []
            )
            
            # Save to database
            question_id = self.question_repo.create(question)
            self.logger.info(f"Admin created question: {question_id}")
            return True, "Câu hỏi đã được tạo thành công!", question_id
            
        except Exception as e:
            error_msg = f"Lỗi khi tạo câu hỏi: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def update_question(self, question_id: int, prompt: str, options: List[str], 
                       answer: str, category: str = "General", 
                       difficulty: str = "Medium", tags: List[str] = None) -> Tuple[bool, str]:
        """
        Update an existing question.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate input
            is_valid, error_msg = self.validator.validate_question(prompt, options, answer, category)
            if not is_valid:
                return False, error_msg
            
            # Get existing question
            existing_question = self.question_repo.get_by_id(question_id)
            if not existing_question:
                return False, "Không tìm thấy câu hỏi!"
            
            # Sanitize inputs
            prompt = self.validator.sanitize_input(prompt)
            options = [self.validator.sanitize_input(opt) for opt in options]
            category = self.validator.sanitize_input(category)
            
            # Update question object
            existing_question.prompt = prompt
            existing_question.option_a = options[0]
            existing_question.option_b = options[1]
            existing_question.option_c = options[2]
            existing_question.answer = answer
            existing_question.category = category or "General"
            existing_question.difficulty = difficulty
            existing_question.tags = tags or []
            
            # Save to database
            success = self.question_repo.update(existing_question)
            if success:
                self.logger.info(f"Admin updated question: {question_id}")
                return True, "Câu hỏi đã được cập nhật thành công!"
            else:
                return False, "Không thể cập nhật câu hỏi!"
                
        except Exception as e:
            error_msg = f"Lỗi khi cập nhật câu hỏi: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def delete_question(self, question_id: int) -> Tuple[bool, str]:
        """
        Delete a question.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if question exists
            question = self.question_repo.get_by_id(question_id)
            if not question:
                return False, "Không tìm thấy câu hỏi!"
            
            # Delete question
            success = self.question_repo.delete(question_id)
            if success:
                self.logger.info(f"Admin deleted question: {question_id}")
                return True, "Câu hỏi đã được xóa thành công!"
            else:
                return False, "Không thể xóa câu hỏi!"
                
        except Exception as e:
            error_msg = f"Lỗi khi xóa câu hỏi: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_all_questions(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all questions with pagination.
        
        Returns:
            Dictionary with questions and pagination info
        """
        try:
            offset = (page - 1) * per_page
            questions = self.question_repo.get_all(limit=per_page, offset=offset)
            total_count = self.question_repo.get_count()
            total_pages = (total_count + per_page - 1) // per_page
            
            return {
                'questions': questions,
                'current_page': page,
                'total_pages': total_pages,
                'total_count': total_count,
                'per_page': per_page
            }
        except Exception as e:
            self.logger.error(f"Error getting questions: {e}")
            return {
                'questions': [],
                'current_page': 1,
                'total_pages': 0,
                'total_count': 0,
                'per_page': per_page
            }
    
    def search_questions(self, search_term: str, category: Optional[str] = None,
                        difficulty: Optional[str] = None) -> List[Question]:
        """Search questions by criteria."""
        try:
            # Validate and sanitize search term
            is_valid, clean_term = self.validator.validate_search_query(search_term)
            if not is_valid:
                return []
            
            return self.question_repo.search(clean_term, category, difficulty)
        except Exception as e:
            self.logger.error(f"Error searching questions: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get all question categories."""
        try:
            return self.question_repo.get_categories()
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return []
    
    # Bulk Operations
    def delete_multiple_questions(self, question_ids: List[int]) -> Tuple[bool, str, int]:
        """
        Delete multiple questions.
        
        Returns:
            Tuple of (success, message, deleted_count)
        """
        try:
            deleted_count = 0
            failed_ids = []
            
            for question_id in question_ids:
                success = self.question_repo.delete(question_id)
                if success:
                    deleted_count += 1
                else:
                    failed_ids.append(question_id)
            
            if deleted_count == len(question_ids):
                self.logger.info(f"Admin deleted {deleted_count} questions")
                return True, f"Đã xóa thành công {deleted_count} câu hỏi!", deleted_count
            elif deleted_count > 0:
                message = f"Đã xóa {deleted_count}/{len(question_ids)} câu hỏi. Không thể xóa: {failed_ids}"
                return False, message, deleted_count
            else:
                return False, "Không thể xóa bất kỳ câu hỏi nào!", 0
                
        except Exception as e:
            error_msg = f"Lỗi khi xóa nhiều câu hỏi: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, 0
    
    def duplicate_question(self, question_id: int) -> Tuple[bool, str, Optional[int]]:
        """
        Create a duplicate of an existing question.
        
        Returns:
            Tuple of (success, message, new_question_id)
        """
        try:
            # Get original question
            original = self.question_repo.get_by_id(question_id)
            if not original:
                return False, "Không tìm thấy câu hỏi gốc!", None
            
            # Create duplicate
            duplicate = Question(
                prompt=f"[Copy] {original.prompt}",
                option_a=original.option_a,
                option_b=original.option_b,
                option_c=original.option_c,
                answer=original.answer,
                category=original.category,
                difficulty=original.difficulty,
                tags=original.tags.copy() if original.tags else []
            )
            
            new_id = self.question_repo.create(duplicate)
            self.logger.info(f"Admin duplicated question {question_id} -> {new_id}")
            return True, "Câu hỏi đã được sao chép thành công!", new_id
            
        except Exception as e:
            error_msg = f"Lỗi khi sao chép câu hỏi: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    # Statistics and Reports
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics."""
        try:
            stats = {}
            
            # Question statistics
            stats['total_questions'] = self.question_repo.get_count()
            categories = self.question_repo.get_categories()
            stats['total_categories'] = len(categories)
            
            # Quiz statistics
            quiz_stats = self.result_repo.get_statistics()
            stats.update(quiz_stats)
            
            # Questions by category
            stats['questions_by_category'] = {}
            for category in categories:
                questions = self.question_repo.search("", category=category)
                stats['questions_by_category'][category] = len(questions)
            
            # Questions by difficulty
            stats['questions_by_difficulty'] = {}
            for difficulty in ['Easy', 'Medium', 'Hard']:
                questions = self.question_repo.search("", difficulty=difficulty)
                stats['questions_by_difficulty'][difficulty] = len(questions)
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    # User Management (basic)
    def authenticate_admin(self, username: str, password: str) -> Optional[User]:
        """Authenticate admin user."""
        try:
            is_valid, error_msg = self.validator.validate_credentials(username, password)
            if not is_valid:
                self.logger.warning(f"Invalid admin credentials format: {error_msg}")
                return None
            
            user = self.user_repo.authenticate(username, password)
            if user and user.is_admin():
                self.logger.info(f"Admin {username} authenticated successfully")
                return user
            else:
                self.logger.warning(f"Failed admin authentication for {username}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error authenticating admin: {e}")
            return None
"""Quiz service for handling quiz operations."""
from typing import List, Optional, Dict, Any, Tuple
from ..models.question import Question
from ..models.user import QuizResult
from ..database.repository import QuestionRepository, QuizResultRepository
from ..utils.validators import InputValidator
from ..utils.logger import Logger
from ..config.settings import Config

class QuizService:
    """Service class for quiz operations."""
    
    def __init__(self):
        self.question_repo = QuestionRepository()
        self.result_repo = QuizResultRepository()
        self.validator = InputValidator()
        self.logger = Logger(__name__)
    
    def get_available_categories(self) -> List[str]:
        """Get all available question categories."""
        try:
            return self.question_repo.get_categories()
        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return []
    
    def get_quiz_questions(self, num_questions: int, category: Optional[str] = None, 
                          difficulty: Optional[str] = None) -> List[Question]:
        """
        Get random questions for a quiz.
        
        Args:
            num_questions: Number of questions to get
            category: Filter by category (optional)
            difficulty: Filter by difficulty (optional)
            
        Returns:
            List of questions for the quiz
        """
        try:
            questions = self.question_repo.get_random_questions(
                count=num_questions,
                category=category,
                difficulty=difficulty
            )
            
            self.logger.info(f"Generated quiz with {len(questions)} questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Error getting quiz questions: {e}")
            return []
    
    def validate_quiz_settings(self, num_questions: int, category: Optional[str] = None,
                             difficulty: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate quiz settings before creating quiz.
        
        Args:
            num_questions: Number of questions requested
            category: Category filter
            difficulty: Difficulty filter
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check number of questions
            if num_questions < 1:
                return False, "Số câu hỏi phải lớn hơn 0"
            
            if num_questions > 50:
                return False, "Số câu hỏi không được vượt quá 50"
            
            # Check if enough questions are available
            available_questions = self.question_repo.search(
                search_term="",
                category=category,
                difficulty=difficulty
            )
            
            if len(available_questions) < num_questions:
                return False, f"Chỉ có {len(available_questions)} câu hỏi phù hợp. Vui lòng giảm số câu hỏi hoặc thay đổi bộ lọc."
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error validating quiz settings: {e}")
            return False, "Lỗi khi kiểm tra cài đặt quiz"
    
    def calculate_score(self, questions: List[Question], user_answers: List[str]) -> Tuple[int, List[bool]]:
        """
        Calculate quiz score based on questions and user answers.
        
        Args:
            questions: List of quiz questions
            user_answers: List of user's answers
            
        Returns:
            Tuple of (score, list_of_correct_results)
        """
        try:
            score = 0
            correct_results = []
            
            for i, question in enumerate(questions):
                if i < len(user_answers):
                    user_answer = user_answers[i]
                    is_correct = user_answer == question.answer
                    if is_correct:
                        score += 1
                    correct_results.append(is_correct)
                else:
                    # No answer provided
                    correct_results.append(False)
            
            self.logger.info(f"Quiz scored: {score}/{len(questions)}")
            return score, correct_results
            
        except Exception as e:
            self.logger.error(f"Error calculating score: {e}")
            return 0, [False] * len(questions)
    
    def generate_quiz_report(self, questions: List[Question], user_answers: List[str], 
                           correct_results: List[bool], time_taken: int) -> Dict[str, Any]:
        """
        Generate detailed quiz report.
        
        Args:
            questions: Quiz questions
            user_answers: User's answers
            correct_results: Which answers were correct
            time_taken: Total time taken in seconds
            
        Returns:
            Dictionary containing quiz report data
        """
        try:
            total_questions = len(questions)
            score = sum(correct_results)
            percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            # Calculate grade
            if percentage >= 90:
                grade = "A"
            elif percentage >= 80:
                grade = "B"
            elif percentage >= 70:
                grade = "C"
            elif percentage >= 60:
                grade = "D"
            else:
                grade = "F"
            
            # Calculate average time per question
            avg_time_per_question = time_taken // total_questions if total_questions > 0 else 0
            
            report = {
                'score': score,
                'total_questions': total_questions,
                'percentage': percentage,
                'grade': grade,
                'time_taken': time_taken,
                'avg_time_per_question': avg_time_per_question,
                'questions': questions,
                'user_answers': user_answers,
                'correct_results': correct_results
            }
            
            self.logger.info(f"Generated quiz report: {score}/{total_questions} ({percentage:.1f}%)")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating quiz report: {e}")
            return {
                'score': 0,
                'total_questions': len(questions),
                'percentage': 0,
                'grade': 'F',
                'time_taken': time_taken,
                'avg_time_per_question': 0,
                'questions': questions,
                'user_answers': user_answers,
                'correct_results': [False] * len(questions)
            }
    
    def save_quiz_result(self, user_id: Optional[int], score: int, total_questions: int, 
                        time_taken: int, question_ids: List[int]) -> bool:
        """
        Save quiz result to database.
        
        Args:
            user_id: User ID (None for anonymous)
            score: Quiz score
            total_questions: Total number of questions
            time_taken: Time taken in seconds
            question_ids: List of question IDs attempted
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            result = QuizResult(
                user_id=user_id,
                score=score,
                total_questions=total_questions,
                time_taken=time_taken,
                questions_attempted=question_ids
            )
            
            result_id = self.result_repo.create(result)
            success = result_id is not None
            
            if success:
                self.logger.info(f"Quiz result saved with ID: {result_id}")
            else:
                self.logger.warning("Failed to save quiz result")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving quiz result: {e}")
            return False
    
    def get_quiz_statistics(self) -> Dict[str, Any]:
        """Get quiz statistics."""
        try:
            return self.result_repo.get_statistics()
        except Exception as e:
            self.logger.error(f"Error getting quiz statistics: {e}")
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'best_score': 0
            }
    
    def get_question_counts_by_criteria(self) -> Dict[str, Any]:
        """Get question counts by different criteria."""
        try:
            total_count = self.question_repo.get_count()
            categories = self.question_repo.get_categories()
            
            # Count by category
            category_counts = {}
            for category in categories:
                count = len(self.question_repo.search("", category=category))
                category_counts[category] = count
            
            # Count by difficulty
            difficulty_counts = {}
            for difficulty in ['Easy', 'Medium', 'Hard']:
                count = len(self.question_repo.search("", difficulty=difficulty))
                difficulty_counts[difficulty] = count
            
            return {
                'total': total_count,
                'by_category': category_counts,
                'by_difficulty': difficulty_counts
            }
            
        except Exception as e:
            self.logger.error(f"Error getting question counts: {e}")
            return {
                'total': 0,
                'by_category': {},
                'by_difficulty': {}
            }
    
    # Trong class QuizService, thêm phương thức:

    def get_latest_quiz_score(self) -> Dict[str, Any]:
        """
        Get the latest quiz score information.

        Returns:
            Dictionary with latest score info
        """
        try:
            latest_result = self.result_repo.get_latest_result()

            if latest_result:
                percentage = (latest_result.score / latest_result.total_questions * 100) if latest_result.total_questions > 0 else 0

                return {
                    'score': latest_result.score,
                    'total': latest_result.total_questions,
                    'percentage': percentage,
                    'grade': latest_result.grade,
                    'time_taken': latest_result.time_taken,
                    'completed_at': latest_result.completed_at,
                    'has_result': True
                }
            else:
                return {
                    'score': 0,
                    'total': 0,
                    'percentage': 0,
                    'grade': 'N/A',
                    'time_taken': 0,
                    'completed_at': None,
                    'has_result': False
                }

        except Exception as e:
            self.logger.error(f"Error getting latest score: {e}")
            return {
                'score': 0,
                'total': 0,
                'percentage': 0,
                'grade': 'N/A',
                'time_taken': 0,
                'completed_at': None,
                'has_result': False
            }


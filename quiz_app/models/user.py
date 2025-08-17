"""User model."""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """User data model."""
    
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""  # In real app, should be hashed
    role: str = "user"  # user, admin
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        user = cls(
            id=data.get('id'),
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True)
        )
        
        # Handle datetime fields
        if data.get('created_at'):
            try:
                user.created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                user.created_at = datetime.now()
        
        if data.get('last_login'):
            try:
                user.last_login = datetime.fromisoformat(data['last_login'])
            except (ValueError, TypeError):
                pass
        
        return user
    
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == 'admin'
    
    def __str__(self) -> str:
        """String representation of user."""
        return f"User({self.username}, {self.role})"

@dataclass
class QuizResult:
    """Quiz result data model."""
    
    id: Optional[int] = None
    user_id: Optional[int] = None
    score: int = 0
    total_questions: int = 0
    time_taken: int = 0  # seconds
    completed_at: Optional[datetime] = None
    questions_attempted: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.completed_at is None:
            self.completed_at = datetime.now()
    
    @property
    def percentage(self) -> float:
        """Get percentage score."""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100
    
    @property
    def grade(self) -> str:
        """Get letter grade based on percentage."""
        percentage = self.percentage
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quiz result to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'time_taken': self.time_taken,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'questions_attempted': ','.join(map(str, self.questions_attempted)),
            'percentage': self.percentage,
            'grade': self.grade
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuizResult':
        """Create quiz result from dictionary."""
        result = cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            score=data.get('score', 0),
            total_questions=data.get('total_questions', 0),
            time_taken=data.get('time_taken', 0)
        )
        
        # Handle datetime
        if data.get('completed_at'):
            try:
                result.completed_at = datetime.fromisoformat(data['completed_at'])
            except (ValueError, TypeError):
                result.completed_at = datetime.now()
        
        # Handle questions attempted
        if data.get('questions_attempted'):
            try:
                result.questions_attempted = [
                    int(qid) for qid in data['questions_attempted'].split(',') 
                    if qid.strip()
                ]
            except (ValueError, TypeError):
                result.questions_attempted = []
        
        return result
    
    def __str__(self) -> str:
        """String representation of quiz result."""
        return f"QuizResult({self.score}/{self.total_questions}, {self.percentage:.1f}%)"
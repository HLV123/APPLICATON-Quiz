"""Question model."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Question:
    """Question data model."""
    
    id: Optional[int] = None
    prompt: str = ""
    option_a: str = ""
    option_b: str = ""
    option_c: str = ""
    answer: str = ""  # A, B, or C
    category: str = "General"
    difficulty: str = "Medium"  # Easy, Medium, Hard
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.created_at is None:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @property
    def options(self) -> List[str]:
        """Get options as a list."""
        return [self.option_a, self.option_b, self.option_c]
    
    @options.setter
    def options(self, options: List[str]):
        """Set options from a list."""
        if len(options) >= 3:
            self.option_a = options[0]
            self.option_b = options[1]
            self.option_c = options[2]
    
    def get_correct_option(self) -> str:
        """Get the correct option text based on answer."""
        option_map = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c
        }
        return option_map.get(self.answer, "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary."""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': ','.join(self.tags) if self.tags else ""
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Create question from dictionary."""
        question = cls(
            id=data.get('id'),
            prompt=data.get('prompt', ''),
            option_a=data.get('option_a', ''),
            option_b=data.get('option_b', ''),
            option_c=data.get('option_c', ''),
            answer=data.get('answer', ''),
            category=data.get('category', 'General'),
            difficulty=data.get('difficulty', 'Medium')
        )
        
        # Handle datetime fields
        if data.get('created_at'):
            try:
                question.created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                question.created_at = datetime.now()
        
        if data.get('updated_at'):
            try:
                question.updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                question.updated_at = datetime.now()
        
        # Handle tags
        if data.get('tags'):
            question.tags = [tag.strip() for tag in data['tags'].split(',') if tag.strip()]
        
        return question
    
    def is_valid(self) -> bool:
        """Check if question is valid."""
        return (
            bool(self.prompt and self.prompt.strip()) and
            bool(self.option_a and self.option_a.strip()) and
            bool(self.option_b and self.option_b.strip()) and
            bool(self.option_c and self.option_c.strip()) and
            self.answer in ['A', 'B', 'C']
        )
    
    def __str__(self) -> str:
        """String representation of question."""
        return f"Question({self.id}): {self.prompt[:50]}..."
# src/quiz_app/models/__init__.py
"""Models package for data structures."""

from .question import Question
from .user import User, QuizResult

__all__ = ['Question', 'User', 'QuizResult']

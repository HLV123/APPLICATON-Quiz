"""Input validation utilities."""
import re
from typing import List, Optional, Tuple

class InputValidator:
    """Input validation class."""
    
    @staticmethod
    def validate_question(prompt: str, options: List[str], answer: str, 
                         category: str = "") -> Tuple[bool, Optional[str]]:
        """
        Validate question input.
        
        Args:
            prompt: Question prompt
            options: List of options (should be 3 items)
            answer: Correct answer
            category: Question category
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check prompt
        if not prompt or len(prompt.strip()) < 5:
            return False, "Câu hỏi phải có ít nhất 5 ký tự"
        
        if len(prompt.strip()) > 500:
            return False, "Câu hỏi không được quá 500 ký tự"
        
        # Check options
        if len(options) != 3:
            return False, "Phải có đúng 3 lựa chọn"
        
        for i, option in enumerate(options):
            if not option or len(option.strip()) < 1:
                return False, f"Lựa chọn {chr(65+i)} không được để trống"
            
            if len(option.strip()) > 200:
                return False, f"Lựa chọn {chr(65+i)} không được quá 200 ký tự"
        
        # Check answer
        if answer not in ['A', 'B', 'C']:
            return False, "Đáp án phải là A, B hoặc C"
        
        # Check category (optional)
        if category and len(category.strip()) > 50:
            return False, "Danh mục không được quá 50 ký tự"
        
        return True, None
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize input text.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags and content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Limit length
        if len(text) > 1000:
            text = text[:1000]
        
        return text.strip()
    
    @staticmethod
    def validate_credentials(username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate login credentials.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or len(username.strip()) < 3:
            return False, "Tên đăng nhập phải có ít nhất 3 ký tự"
        
        if len(username.strip()) > 50:
            return False, "Tên đăng nhập không được quá 50 ký tự"
        
        if not password or len(password) < 4:
            return False, "Mật khẩu phải có ít nhất 4 ký tự"
        
        if len(password) > 100:
            return False, "Mật khẩu không được quá 100 ký tự"
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Tên đăng nhập chỉ được chứa chữ cái, số, _ và -"
        
        return True, None
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """
        Validate and sanitize search query.
        
        Args:
            query: Search query
            
        Returns:
            Tuple of (is_valid, sanitized_query)
        """
        if not query:
            return True, ""
        
        # Sanitize
        query = InputValidator.sanitize_input(query)
        
        # Length check
        if len(query) > 100:
            query = query[:100]
        
        return True, query
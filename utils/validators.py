import re

class Validators:
    """Validation helper class."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format."""
        if not email or not isinstance(email, str):
            return False
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_regex, email.strip()))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate HTTP/HTTPS URL format."""
        if not url or not isinstance(url, str):
            return False
        url_regex = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_regex, url.strip()))

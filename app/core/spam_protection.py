import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class SpamProtection:
    # Common spam keywords
    SPAM_KEYWORDS = [
        'viagra', 'casino', 'porn', 'sex', 'adult', 'dating',
        'loans', 'mortgage', 'insurance', 'credit', 'debt',
        'weight loss', 'diet pill', 'pharmacy', 'medication',
        'click here', 'buy now', 'free money', 'make money',
        'work from home', 'online casino', 'gambling'
    ]
    
    # Common spam domains
    SPAM_DOMAINS = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'mail.ru', 'yandex.com', 'protonmail.com',
        'tutanota.com', 'guerrillamail.com', '10minutemail.com'
    ]
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+',  # URLs
        r'<[^>]+>',  # HTML tags
        r'\b(?:h[1-6]|div|span|p|br)\b',  # HTML tags
        r'[^\w\s.,!?@-]',  # Unusual characters
    ]

    @classmethod
    def check_spam(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Check if the form data contains spam.
        Returns: (is_spam, reasons)
        """
        reasons = []
        is_spam = False
        
        # Combine all text values
        text_values = []
        for key, value in data.items():
            if isinstance(value, str):
                text_values.append(value.lower())
            elif isinstance(value, list):
                text_values.extend([str(v).lower() for v in value])
            else:
                text_values.append(str(value).lower())
        
        combined_text = ' '.join(text_values)
        
        # Check for spam keywords
        found_keywords = []
        for keyword in cls.SPAM_KEYWORDS:
            if keyword in combined_text:
                found_keywords.append(keyword)
        
        if found_keywords:
            reasons.append(f"Contains spam keywords: {', '.join(found_keywords)}")
            is_spam = True
        
        # Check for suspicious patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                # Only flag if it's not a legitimate URL
                if pattern != r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+':
                    reasons.append(f"Contains suspicious pattern: {pattern}")
                    is_spam = True
        
        # Check for multiple URLs
        urls = re.findall(r'https?://[^\s]+', combined_text)
        if len(urls) > 2:
            reasons.append(f"Contains {len(urls)} URLs (suspicious)")
            is_spam = True
        
        # Check for excessive formatting
        if len(re.findall(r'<[^>]+>', combined_text)) > 3:
            reasons.append("Contains excessive HTML tags")
            is_spam = True
        
        # Check for email spam (multiple @ symbols)
        if combined_text.count('@') > 3:
            reasons.append("Contains multiple email addresses")
            is_spam = True
        
        # Check for repeated characters (spam signal)
        for char in '!?.':
            if char in combined_text and combined_text.count(char) > 10:
                reasons.append(f"Excessive '{char}' characters")
                is_spam = True
        
        # Check for ALL CAPS (spam signal)
        words = combined_text.split()
        caps_words = [w for w in words if w.isupper() and len(w) > 3]
        if len(caps_words) > len(words) * 0.3:
            reasons.append("Excessive use of ALL CAPS")
            is_spam = True
        
        # Check if message is mostly numbers
        if len(combined_text) > 20:
            digit_ratio = sum(1 for c in combined_text if c.isdigit()) / len(combined_text)
            if digit_ratio > 0.3:
                reasons.append("Excessive use of numbers")
                is_spam = True
        
        # Check for short, meaningless messages
        if len(combined_text) < 10 and data.get('message') and len(data.get('message', '')) < 10:
            reasons.append("Message too short to be legitimate")
            is_spam = True
        
        # Log spam detection
        if is_spam:
            logger.warning(f"Spam detected: {reasons}")
        
        return is_spam, reasons

    @classmethod
    def validate_email(cls, email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email and check if it's from a spam domain.
        Returns: (is_valid, reason)
        """
        if not email:
            return False, "Email is required"
        
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email format"
        
        # Check spam domains
        domain = email.split('@')[1].lower()
        if domain in cls.SPAM_DOMAINS:
            return False, f"Email domain '{domain}' is known for spam"
        
        # Check for disposable email patterns
        disposable_patterns = [
            r'temp', r'test', r'fake', r'dummy', r'spam',
            r'throwaway', r'guerrilla', r'10min', r'disposable'
        ]
        for pattern in disposable_patterns:
            if pattern in domain:
                return False, f"Email domain '{domain}' appears to be disposable"
        
        return True, None

    @classmethod
    def validate_phone(cls, phone: str) -> tuple[bool, Optional[str]]:
        """
        Validate phone number.
        Returns: (is_valid, reason)
        """
        if not phone:
            return True, None  # Phone is optional
        
        # Clean phone number
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check length
        if len(cleaned) < 7:
            return False, "Phone number too short"
        if len(cleaned) > 15:
            return False, "Phone number too long"
        
        return True, None

    @classmethod
    def check_rate_abuse(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Check for rate-based abuse patterns.
        Returns: (is_abuse, reasons)
        """
        reasons = []
        is_abuse = False
        
        # Check for identical submissions
        # This would require accessing the database, so it's a placeholder
        # The actual implementation would check for duplicate submissions
        
        # Check for rapid submissions
        # This is handled by the rate limiter
        
        return is_abuse, reasons

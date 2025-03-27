# Amatak String Utilities
# String manipulation and text processing

import re
import unicodedata
from typing import List, Dict, Union
from amatak.error_handling import ErrorHandler
from amatak.security.middleware import SecurityMiddleware

class Strings:
    """String manipulation and text processing utilities"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.security = SecurityMiddleware()
        
    def sanitize(self, text: str, level: str = 'medium') -> str:
        """
        Sanitize potentially dangerous input
        
        Args:
            text: Input string to sanitize
            level: One of 'low', 'medium', 'high'
        """
        sanitized = text
        
        if level == 'high':
            sanitized = re.sub(r'[^a-zA-Z0-9\s\-_.,]', '', sanitized)
        elif level == 'medium':
            sanitized = re.sub(r'[<>"\'\\;=]', '', sanitized)
        # Low level does basic HTML escaping
            
        return sanitized.replace('<', '&lt;').replace('>', '&gt;')
        
    def slugify(self, text: str, separator: str = '-') -> str:
        """Convert text to URL-friendly slug"""
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', separator, text).strip('-_')
        
    def truncate(self, text: str, length: int = 100, suffix: str = '...') -> str:
        """Truncate text with optional suffix"""
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix
        
    def pluralize(self, count: int, singular: str, plural: str = None) -> str:
        """Return singular or plural form based on count"""
        if count == 1:
            return singular
        return plural or (singular + 's')
        
    def levenshtein(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)
            
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
        
    def soundex(self, word: str) -> str:
        """Soundex algorithm for phonetic matching"""
        word = word.upper()
        soundex_code = word[0]
        mapping = {
            'BFPV': '1',
            'CGJKQSXZ': '2',
            'DT': '3',
            'L': '4',
            'MN': '5',
            'R': '6'
        }
        
        for char in word[1:]:
            for letters, code in mapping.items():
                if char in letters:
                    if code != soundex_code[-1]:
                        soundex_code += code
                    break
                    
        soundex_code = soundex_code.ljust(4, '0')
        return soundex_code[:4]
        
    def parse_query(self, query: str) -> Dict[str, Union[str, List[str]]]:
        """Parse URL query string into dictionary"""
        params = {}
        for pair in query.split('&'):
            if not pair:
                continue
                
            if '=' in pair:
                key, value = pair.split('=', 1)
            else:
                key, value = pair, ''
                
            key = self.security.sanitize_input(key)
            value = self.security.sanitize_input(value)
            
            if key in params:
                if isinstance(params[key], list):
                    params[key].append(value)
                else:
                    params[key] = [params[key], value]
            else:
                params[key] = value
                
        return params
        
    def wrap(self, text: str, width: int = 80) -> str:
        """Wrap text to specified width"""
        import textwrap
        return textwrap.fill(text, width)
        
    def count_words(self, text: str) -> int:
        """Count words in text"""
        words = re.findall(r'\w+', text)
        return len(words)
        
    def rotate(self, text: str, shift: int) -> str:
        """Caesar cipher rotation"""
        result = []
        for char in text:
            if char.isupper():
                result.append(chr((ord(char) + shift - 65) % 26 + 65))
            elif char.islower():
                result.append(chr((ord(char) + shift - 97) % 26 + 97))
            else:
                result.append(char)
        return ''.join(result)
        
    def is_palindrome(self, text: str) -> bool:
        """Check if text is palindrome"""
        clean = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        return clean == clean[::-1]
        
    def fingerprint(self, text: str) -> str:
        """Create text fingerprint for comparison"""
        # Normalize
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.strip()
        
        # Sort words and remove duplicates
        words = sorted(set(text.split()))
        return ' '.join(words)

# Export default strings instance
strings = Strings()
import re  
from typing import List, Dict, Optional, Tuple  
from dataclasses import dataclass  
from enum import Enum  
  
class PatternType(Enum):  
    """Predefined pattern types for common redaction scenarios."""  
    EMAIL = "email"  
    PHONE = "phone"  
    SSN = "ssn"  
    CREDIT_CARD = "credit_card"  
    CUSTOM = "custom"  
  
@dataclass  
class PatternTemplate:  
    """Template for predefined patterns."""  
    name: str  
    pattern: str  
    description: str  
  
class EnhancedPatternMatcher:  
    """Enhanced pattern matching with optimization and predefined templates."""  
      
    # Predefined pattern templates  
    PATTERN_TEMPLATES: Dict[PatternType, PatternTemplate] = {  
        PatternType.EMAIL: PatternTemplate(  
            "Email Address",  
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",  
            "Matches email addresses"  
        ),  
        PatternType.PHONE: PatternTemplate(  
            "Phone Number",  
            r"(\+?[0-9]{1,4}[-.\s]?)?([0-9]{3,5})[-.\s]?([0-9]{6,8})",  
            "Matches US phone numbers in various formats"  
        ),  
        PatternType.SSN: PatternTemplate(  
            "Social Security Number",  
            r"\b\d{3}-?\d{2}-?\d{4}\b",  
            "Matches SSN in XXX-XX-XXXX or XXXXXXXXX format"  
        ),  
        PatternType.CREDIT_CARD: PatternTemplate(  
            "Credit Card Number",  
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  
            "Matches credit card numbers with optional separators"  
        )  
    }  
      
    def __init__(self):  
        self._compiled_patterns: List[Tuple[re.Pattern, str]] = []  
        self._pattern_cache: Dict[str, re.Pattern] = {}  
      
    def add_pattern(self, pattern: str, ignore_case: bool = False,   
                   pattern_type: PatternType = PatternType.CUSTOM) -> None:  
        """Add a pattern to the matcher with caching."""  
        cache_key = f"{pattern}_{ignore_case}"  
          
        if cache_key not in self._pattern_cache:  
            flags = re.IGNORECASE if ignore_case else 0  
            try:  
                compiled_pattern = re.compile(pattern, flags)  
                self._pattern_cache[cache_key] = compiled_pattern  
            except re.error as e:  
                raise ValueError(f"Invalid regex pattern '{pattern}': {e}")  
          
        self._compiled_patterns.append((self._pattern_cache[cache_key], pattern))  
      
    def add_predefined_pattern(self, pattern_type: PatternType,   
                             ignore_case: bool = False) -> None:  
        """Add a predefined pattern template."""        
        if pattern_type not in self.PATTERN_TEMPLATES:  
            raise ValueError(f"Unknown pattern type: {pattern_type}")  
          
        template = self.PATTERN_TEMPLATES[pattern_type]  
        self.add_pattern(template.pattern, ignore_case, pattern_type)  
      
    def validate_patterns(self, patterns: List[str]) -> List[str]:  
        """Validate regex patterns and return error messages for invalid ones."""  
        errors = []  
        for pattern in patterns:  
            try:  
                re.compile(pattern)  
            except re.error as e:  
                errors.append(f"Invalid pattern '{pattern}': {e}")  
        return errors  
      
    def find_matches(self, text: str) -> List[Tuple[int, int, str, str]]:  
        """Find all matches in text. Returns (start, end, matched_text, pattern)."""  
        matches = []  
        for compiled_pattern, original_pattern in self._compiled_patterns:  
            for match in compiled_pattern.finditer(text):  
                start, end = match.span()  
                matched_text = text[start:end]  
                matches.append((start, end, matched_text, original_pattern))  
          
        # Sort matches by position to handle overlapping matches  
        return sorted(matches, key=lambda x: x[0])  
      
    def get_pattern_info(self) -> List[Dict[str, str]]:  
        """Get information about all loaded patterns."""  
        info = []  
        for _, pattern in self._compiled_patterns:  
            # Check if it's a predefined pattern  
            template_info = None  
            for pattern_type, template in self.PATTERN_TEMPLATES.items():  
                if template.pattern == pattern:  
                    template_info = template  
                    break  
              
            if template_info:  
                info.append({  
                    "pattern": pattern,  
                    "name": template_info.name,  
                    "description": template_info.description,  
                    "type": "predefined"  
                })  
            else:  
                info.append({  
                    "pattern": pattern,  
                    "name": "Custom Pattern",  
                    "description": "User-defined pattern",  
                    "type": "custom"  
                })  
          
        return info  
      
    def clear_patterns(self) -> None:  
        """Clear all loaded patterns."""  
        self._compiled_patterns.clear()  
        self._pattern_cache.clear()
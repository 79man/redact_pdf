import pytest  
import re  
from pdf_redacter.pattern_matcher import EnhancedPatternMatcher, PatternType, PatternTemplate  
  
class TestPatternType:  
    """Test the PatternType enum."""  
      
    def test_pattern_type_values(self):  
        """Test that all expected pattern types exist."""  
        assert PatternType.EMAIL.value == "email"  
        assert PatternType.PHONE.value == "phone"  
        assert PatternType.SSN.value == "ssn"  
        assert PatternType.CREDIT_CARD.value == "credit_card"  
        assert PatternType.CUSTOM.value == "custom"  
  
class TestPatternTemplate:  
    """Test the PatternTemplate dataclass."""  
      
    def test_pattern_template_creation(self):  
        """Test creating a pattern template."""  
        template = PatternTemplate(  
            name="Test Pattern",  
            pattern=r"\d+",  
            description="Matches digits"  
        )  
          
        assert template.name == "Test Pattern"  
        assert template.pattern == r"\d+"  
        assert template.description == "Matches digits"  
  
class TestEnhancedPatternMatcher:  
    """Test the enhanced pattern matching functionality."""  
      
    def test_init(self):  
        """Test matcher initialization."""  
        matcher = EnhancedPatternMatcher()  
        assert len(matcher._compiled_patterns) == 0  
        assert len(matcher._pattern_cache) == 0  
        assert len(matcher.PATTERN_TEMPLATES) == 4  # email, phone, ssn, credit_card  
      
    def test_add_custom_pattern(self):  
        """Test adding custom patterns."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern(r"\d{3}-\d{2}-\d{4}", ignore_case=False)  
          
        assert len(matcher._compiled_patterns) == 1  
        assert len(matcher._pattern_cache) == 1  
          
        text = "SSN: 123-45-6789"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) == 1  
        assert matches[0][2] == "123-45-6789"  # matched_text  
        assert matches[0][3] == r"\d{3}-\d{2}-\d{4}"  # pattern  
      
    def test_add_pattern_with_ignore_case(self):  
        """Test adding patterns with case insensitive flag."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern("confidential", ignore_case=True)  
          
        text = "This is CONFIDENTIAL information"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) == 1  
        assert matches[0][2] == "CONFIDENTIAL"  
      
    def test_add_predefined_pattern_email(self):  
        """Test adding predefined email pattern."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_predefined_pattern(PatternType.EMAIL)  
          
        text = "Contact: user@example.com and admin@test.org"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) == 2  
        assert "user@example.com" in [match[2] for match in matches]  
        assert "admin@test.org" in [match[2] for match in matches]  
      
    def test_add_predefined_pattern_phone(self):  
        """Test adding predefined phone pattern."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_predefined_pattern(PatternType.PHONE)

        text = "Call +91-9877655456 or 080-5544355667"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) >= 1  # Should match at least one phone number  
      
    def test_add_predefined_pattern_ssn(self):  
        """Test adding predefined SSN pattern."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_predefined_pattern(PatternType.SSN)  
          
        text = "SSN: 123-45-6789 or 987654321"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) >= 1  
        assert any("123-45-6789" in match[2] for match in matches)  
      
    def test_add_predefined_pattern_credit_card(self):  
        """Test adding predefined credit card pattern."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_predefined_pattern(PatternType.CREDIT_CARD)  
          
        text = "Card: 1234 5678 9012 3456 or 1234-5678-9012-3456"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) >= 1  
      
    def test_add_invalid_predefined_pattern(self):  
        """Test adding invalid predefined pattern type."""  
        matcher = EnhancedPatternMatcher()  
          
        # This should raise ValueError for unknown pattern type  
        with pytest.raises(ValueError, match="Unknown pattern type"):  
            matcher.add_predefined_pattern("invalid_pattern")  
      
    def test_pattern_validation_valid(self):  
        """Test validation of valid regex patterns."""  
        matcher = EnhancedPatternMatcher()  
          
        valid_patterns = ["test", r"\d+", "email@domain.com", r"[A-Z]+"]  
        errors = matcher.validate_patterns(valid_patterns)  
          
        assert len(errors) == 0  
      
    def test_pattern_validation_invalid(self):  
        """Test validation of invalid regex patterns."""  
        matcher = EnhancedPatternMatcher()  
          
        invalid_patterns = ["[unclosed", "*invalid", "(?P<incomplete"]  
        errors = matcher.validate_patterns(invalid_patterns)  
          
        assert len(errors) > 0  
        assert any("Invalid pattern" in error for error in errors)  
      
    def test_pattern_caching(self):  
        """Test that patterns are cached properly."""  
        matcher = EnhancedPatternMatcher()  
          
        # Add same pattern twice with same flags  
        matcher.add_pattern("test", ignore_case=False)  
        matcher.add_pattern("test", ignore_case=False)  
          
        # Should have two entries in compiled patterns but only one in cache  
        assert len(matcher._compiled_patterns) == 2  
        assert len(matcher._pattern_cache) == 1  
          
        # Add same pattern with different flags  
        matcher.add_pattern("test", ignore_case=True)  
          
        # Should now have two cache entries (different flags)  
        assert len(matcher._pattern_cache) == 2  
      
    def test_find_matches_multiple_patterns(self):  
        """Test finding matches with multiple patterns."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern("confidential", ignore_case=True)  
        matcher.add_predefined_pattern(PatternType.EMAIL)  
          
        text = "This CONFIDENTIAL document contains user@example.com"  
        matches = matcher.find_matches(text)  
          
        assert len(matches) == 2  
        # Matches should be sorted by position  
        assert matches[0][0] < matches[1][0]  # start positions  
      
    def test_find_matches_overlapping(self):  
        """Test handling of overlapping matches."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern("test", ignore_case=False)  
        matcher.add_pattern("testing", ignore_case=False)  
          
        text = "This is testing"  
        matches = matcher.find_matches(text)  
          
        # Should find both "test" and "testing"  
        assert len(matches) == 2  
        # Should be sorted by position  
        assert matches[0][0] <= matches[1][0]  
      
    def test_get_pattern_info_predefined(self):  
        """Test getting information about predefined patterns."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_predefined_pattern(PatternType.EMAIL)  
        matcher.add_predefined_pattern(PatternType.PHONE)  
          
        info = matcher.get_pattern_info()  
          
        assert len(info) == 2  
        assert all(item["type"] == "predefined" for item in info)  
        assert any(item["name"] == "Email Address" for item in info)  
        assert any(item["name"] == "Phone Number" for item in info)  
      
    def test_get_pattern_info_custom(self):  
        """Test getting information about custom patterns."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern(r"\d+", ignore_case=False)  
        matcher.add_pattern("custom_text", ignore_case=True)  
          
        info = matcher.get_pattern_info()  
          
        assert len(info) == 2  
        assert all(item["type"] == "custom" for item in info)  
        assert all(item["name"] == "Custom Pattern" for item in info)  
      
    def test_get_pattern_info_mixed(self):  
        """Test getting information about mixed pattern types."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern("custom", ignore_case=False)  
        matcher.add_predefined_pattern(PatternType.EMAIL)  
          
        info = matcher.get_pattern_info()  
          
        assert len(info) == 2  
        types = [item["type"] for item in info]  
        assert "custom" in types  
        assert "predefined" in types  
      
    def test_clear_patterns(self):  
        """Test clearing all patterns."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern("test", ignore_case=False)  
        matcher.add_predefined_pattern(PatternType.EMAIL)  
          
        assert len(matcher._compiled_patterns) == 2  
        assert len(matcher._pattern_cache) == 2  
          
        matcher.clear_patterns()  
          
        assert len(matcher._compiled_patterns) == 0  
        assert len(matcher._pattern_cache) == 0  
      
    def test_invalid_regex_pattern_error(self):  
        """Test that invalid regex patterns raise appropriate errors."""  
        matcher = EnhancedPatternMatcher()  
          
        with pytest.raises(ValueError, match="Invalid regex pattern"):  
            matcher.add_pattern("[unclosed bracket")  
      
    @pytest.mark.parametrize("pattern_type,expected_name", [  
        (PatternType.EMAIL, "Email Address"),  
        (PatternType.PHONE, "Phone Number"),  
        (PatternType.SSN, "Social Security Number"),  
        (PatternType.CREDIT_CARD, "Credit Card Number"),  
    ])  
    def test_predefined_pattern_templates(self, pattern_type, expected_name):  
        """Test that predefined pattern templates are correctly defined."""  
        template = EnhancedPatternMatcher.PATTERN_TEMPLATES[pattern_type]  
          
        assert template.name == expected_name  
        assert isinstance(template.pattern, str)  
        assert len(template.pattern) > 0  
        assert isinstance(template.description, str)  
        assert len(template.description) > 0  
          
        # Verify the pattern compiles without errors  
        re.compile(template.pattern)  
      
    def test_pattern_matching_performance(self):  
        """Test pattern matching with large text."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_predefined_pattern(PatternType.EMAIL)  
        matcher.add_pattern("test", ignore_case=False)  
          
        # Create large text with multiple matches  
        large_text = "test " * 1000 + "user@example.com " * 100  
          
        matches = matcher.find_matches(large_text)  
          
        # Should find all matches efficiently  
        assert len(matches) == 1100  # 1000 "test" + 100 emails  
      
    def test_case_sensitivity_combinations(self):  
        """Test various case sensitivity combinations."""  
        matcher = EnhancedPatternMatcher()  
        matcher.add_pattern("Test", ignore_case=False)  # Case sensitive  
        matcher.add_pattern("CASE", ignore_case=True)   # Case insensitive  
          
        text = "test Test CASE case"  
        matches = matcher.find_matches(text)  
          
        # Should match "Test" (exact case) and both "CASE" and "case"  
        assert len(matches) == 3  
        matched_texts = [match[2] for match in matches]  
        assert "Test" in matched_texts  
        assert "CASE" in matched_texts  
        assert "case" in matched_texts  
        assert "test" not in matched_texts  # Should not match due to case sensitivity
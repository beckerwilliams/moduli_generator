def validate_integer_parameters(key_length=None, nice_value=None):
    """
    Validates that key_length and nice_value are proper integers.

    This function addresses the security concerns identified in the code analysis,
    particularly the command injection risks from unvalidated inputs to subprocess calls.

    :param key_length: The cryptographic key length in bits (e.g., 1024, 2048, 4096)
    :type key_length: Any
    :param nice_value: The process priority value for 'nice' command (-20 to 19)
    :type nice_value: Any
    :raises ValueError: If parameters are not valid integers or are out of expected ranges
    :raises TypeError: If parameters are not of expected types
    :return: Tuple of validated integers (key_length, nice_value) or None values
    :rtype: tuple[int | None, int | None]
    """
    validated_key_length = None
    validated_nice_value = None

    # Validate key_length
    if key_length is not None:
        if not isinstance(key_length, (int, str)):
            raise TypeError(f"key_length must be an integer or string, got {type(key_length).__name__}")

        try:
            validated_key_length = int(key_length)
        except (ValueError, OverflowError) as e:
            raise ValueError(f"key_length must be convertible to integer: {e}")

        # Additional validation for reasonable key lengths
        if validated_key_length < 3072:
            raise ValueError(f"key_length {validated_key_length} is too small (minimum 512 bits)")
        if validated_key_length > 8192:
            raise ValueError(f"key_length {validated_key_length} is too large (maximum 16384 bits)")
        if validated_key_length % 8 != 0:
            raise ValueError(f"key_length {validated_key_length} must be divisible by 8")

    # Validate nice_value
    if nice_value is not None:
        if not isinstance(nice_value, (int, str)):
            raise TypeError(f"nice_value must be an integer or string, got {type(nice_value).__name__}")

        try:
            validated_nice_value = int(nice_value)
        except (ValueError, OverflowError) as e:
            raise ValueError(f"nice_value must be convertible to integer: {e}")

        # Validate nice_value range (standard Unix nice values)
        if not -20 <= validated_nice_value <= 19:
            raise ValueError(f"nice_value {validated_nice_value} must be between -20 and 19")

    return validated_key_length, validated_nice_value


def validate_subprocess_args(key_length, nice_value):
    """
    Specialized validation for subprocess arguments to prevent command injection.

    This function ensures that parameters passed to subprocess calls are safe
    and cannot be exploited for command injection attacks.

    :param key_length: The cryptographic key length in bits
    :type key_length: Any
    :param nice_value: The process priority value
    :type nice_value: Any
    :raises ValueError: If parameters fail validation
    :raises TypeError: If parameters are not of expected types
    :return: Tuple of validated string representations safe for subprocess
    :rtype: tuple[str, str]
    """
    # Use the main validation function first
    validated_key_length, validated_nice_value = validate_integer_parameters(
        key_length=key_length,
        nice_value=nice_value
    )

    if validated_key_length is None:
        raise ValueError("key_length is required for subprocess validation")
    if validated_nice_value is None:
        raise ValueError("nice_value is required for subprocess validation")

    # Convert to strings safe for subprocess
    safe_key_length = str(validated_key_length)
    safe_nice_value = str(validated_nice_value)

    # Additional security check - ensure no special characters
    import re
    if not re.match(r'^\d+$', safe_key_length):
        raise ValueError(f"key_length contains invalid characters: {safe_key_length}")
    if not re.match(r'^-?\d+$', safe_nice_value):
        raise ValueError(f"nice_value contains invalid characters: {safe_nice_value}")

    return safe_key_length, safe_nice_value


# Example usage and test cases
if __name__ == "__main__":
    # Test cases for the validation function
    test_cases = [
        # Valid cases
        (2048, 10, True, "Valid standard case"),
        ("4096", "15", True, "Valid string inputs"),
        (1024, -5, True, "Valid negative nice value"),

        # Invalid key_length cases
        (256, 10, False, "Key length too small"),
        (32768, 10, False, "Key length too large"),
        (2049, 10, False, "Key length not divisible by 8"),
        ("not_a_number", 10, False, "Key length not numeric"),

        # Invalid nice_value cases
        (2048, 25, False, "Nice value too high"),
        (2048, -25, False, "Nice value too low"),
        (2048, "invalid", False, "Nice value not numeric"),

        # Type error cases
        ([], 10, False, "Key length wrong type"),
        (2048, {}, False, "Nice value wrong type"),
    ]

    print("Testing validate_integer_parameters function:")
    print("-" * 50)

    for key_len, nice_val, should_pass, description in test_cases:
        try:
            result = validate_integer_parameters(key_len, nice_val)
            if should_pass:
                print(f"✓ PASS: {description} -> {result}")
            else:
                print(f"✗ FAIL: {description} -> Should have raised exception but got {result}")
        except (ValueError, TypeError) as e:
            if not should_pass:
                print(f"✓ PASS: {description} -> Correctly raised: {type(e).__name__}: {e}")
            else:
                print(f"✗ FAIL: {description} -> Unexpectedly raised: {type(e).__name__}: {e}")

    print("\nTesting validate_subprocess_args function:")
    print("-" * 50)

    try:
        safe_key, safe_nice = validate_subprocess_args(2048, 10)
        print(f"✓ PASS: Subprocess validation -> key_length='{safe_key}', nice_value='{safe_nice}'")
    except Exception as e:
        print(f"✗ FAIL: Subprocess validation -> {type(e).__name__}: {e}")
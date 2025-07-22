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
        # Allow 0 as a special case for screening operations that don't need key length
        if validated_key_length != 0:
            if validated_key_length < 3072:
                raise ValueError(f"key_length {validated_key_length} is too small (minimum 3072 bits)")
            if validated_key_length > 8192:
                raise ValueError(f"key_length {validated_key_length} is too large (maximum 8192 bits)")
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


@staticmethod
def _screen_candidates_static(config, candidates_file: Path) -> Path:
    """
    Screen candidate moduli files using provided configuration and the `ssh-keygen` tool.
    """
    screened_file = config.moduli_dir / f'{candidates_file.name.replace('candidates', 'moduli')}'
    logger = config.get_logger()

    # For screening operations, we only need to validate the nice_value
    # Key length is not needed since we're processing existing candidates
    _, safe_nice_value = validate_subprocess_args(0, config.nice_value)

    try:
        checkpoint_file = config.candidates_dir / f".{candidates_file.name}"
        result = subprocess.run([
            'nice', '-n', f'{safe_nice_value}',
            'ssh-keygen',
            '-M', 'screen',
            '-O', f'generator={config.generator_type}',
            '-O', f'checkpoint={str(checkpoint_file)}',
            '-f', str(candidates_file),
            str(screened_file)
        ], check=True, capture_output=True, text=True)

        # Log the output after successful completion
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(line.strip())

        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    logger.debug(line.strip())

        # Cleanup used Moduli Candidates
        candidates_file.unlink()
        return screened_file

    except subprocess.CalledProcessError as err:
        # Log any captured output from the failed process
        if err.stdout:
            for line in err.stdout.strip().split('\n'):
                if line.strip():
                    logger.error(f"stdout: {line.strip()}")

        if err.stderr:
            for line in err.stderr.strip().split('\n'):
                if line.strip():
                    logger.error(f"stderr: {line.strip()}")

        logger.error(f'ssh-keygen screen failed for {candidates_file}: {err}')
        raise err
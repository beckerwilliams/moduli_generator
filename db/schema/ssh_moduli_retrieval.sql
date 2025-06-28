SELECT
    DATE_FORMAT(timestamp, '%Y%m%d%H%M%S') AS formatted_timestamp,
    type,
    tests,
    trials,
    size,
    generator,
    modulus
FROM
    moduli_db.moduli_view
ORDER BY
    timestamp, size;
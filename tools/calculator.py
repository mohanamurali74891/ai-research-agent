"""
tools/calculator.py
────────────────────────────────────────────────
Tool: Safe math expression evaluator
Part of: AI Research Agent - Module 5
"""

import math
import re


# Allowed names for safe eval
SAFE_NAMES = {
    name: getattr(math, name)
    for name in dir(math)
    if not name.startswith("_")
}
SAFE_NAMES.update({"abs": abs, "round": round, "min": min, "max": max, "sum": sum})


def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A math expression string (e.g., "2 ** 10 + sqrt(16)")

    Returns:
        Result as a string, or an error message
    """
    # Sanitize: only allow safe characters
    if re.search(r"[a-zA-Z_]", expression):
        # Allow only whitelisted math function names
        allowed_words = set(SAFE_NAMES.keys())
        words_used = set(re.findall(r"[a-zA-Z_]+", expression))
        disallowed = words_used - allowed_words
        if disallowed:
            return f"Error: Disallowed identifiers: {disallowed}. Only math functions are allowed."

    try:
        result = eval(expression, {"__builtins__": {}}, SAFE_NAMES)  # noqa: S307
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between common units.

    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., 'km', 'kg', 'celsius')
        to_unit: Target unit (e.g., 'miles', 'pounds', 'fahrenheit')

    Returns:
        Conversion result as string
    """
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("kg", "pounds"): lambda x: x * 2.20462,
        ("pounds", "kg"): lambda x: x * 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9 / 5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("liters", "gallons"): lambda x: x * 0.264172,
        ("gallons", "liters"): lambda x: x * 3.78541,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.4f} {to_unit}"
    else:
        return f"Conversion from '{from_unit}' to '{to_unit}' is not supported."

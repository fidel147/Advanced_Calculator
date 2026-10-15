"""Deterministic symbolic mathematics services for the Scientific mode."""

import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

TRANSFORMATIONS = standard_transformations + (convert_xor, implicit_multiplication_application)
SYMBOLS = {name: sp.Symbol(name) for name in ("x", "y", "z", "t")}
LOCALS = {
    **SYMBOLS,
    "pi": sp.pi,
    "E": sp.E,
    "I": sp.I,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "Abs": sp.Abs,
}
ALLOWED_NAMES = set(LOCALS)
NAME_PATTERN = re.compile(r"[A-Za-z_]\w*")
CHARACTER_PATTERN = re.compile(r"^[A-Za-z0-9_+*/().,^=\- \t]+$")


def parse_expression(text):
    """Parse a bounded mathematical expression with an explicit symbol/function allowlist."""
    text = text.strip()
    if not text or len(text) > 500:
        raise ValueError("Enter an expression of 1-500 characters")
    if not CHARACTER_PATTERN.fullmatch(text):
        raise ValueError("Use mathematical characters only")
    names = set(NAME_PATTERN.findall(text))
    unknown = names - ALLOWED_NAMES
    if unknown:
        raise ValueError(f"Unknown name: {sorted(unknown)[0]}")
    return parse_expr(text, local_dict=LOCALS, transformations=TRANSFORMATIONS, evaluate=True)


def _symbol(name):
    if name not in SYMBOLS:
        raise ValueError("Variable must be x, y, z, or t")
    return SYMBOLS[name]


def solve(expression, variable="x"):
    """Solve an expression or equation for one supported variable."""
    if "=" in expression:
        left, right = expression.split("=", 1)
        equation = parse_expression(left) - parse_expression(right)
    else:
        equation = parse_expression(expression)
    return sp.solve(equation, _symbol(variable))


def calculate(expression, operation="Simplify", variable="x"):
    """Apply one supported symbolic operation."""
    if operation == "Solve":
        return solve(expression, variable)
    parsed = parse_expression(expression)
    symbol = _symbol(variable)
    if operation == "Simplify":
        return sp.simplify(parsed)
    if operation == "Expand":
        return sp.expand(parsed)
    if operation == "Factor":
        return sp.factor(parsed)
    if operation == "Differentiate":
        return sp.diff(parsed, symbol)
    if operation == "Integrate":
        return sp.integrate(parsed, symbol)
    if operation == "Limit":
        return sp.limit(parsed, symbol, 0)
    raise ValueError(f"Unknown symbolic operation: {operation}")


def format_result(value):
    """Format SymPy values for a readable result panel."""
    if isinstance(value, list):
        return "[" + ", ".join(sp.sstr(item) for item in value) + "]"
    return sp.sstr(value)

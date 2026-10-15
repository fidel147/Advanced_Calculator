import cmath
import re

from engine.basic import ERRORS
from engine.evaluator import NAME, Evaluator, format_value


class KeyboardCalculator:
    """Typed expressions: 2*(3+4), 5!, sin(30), x = 4, f(x) = x^2 + 1."""

    def __init__(self, evaluator=None):
        self.evaluator = evaluator or Evaluator()

    def submit(self, text):
        """Returns (message, ok). The message is the result, or what went wrong."""
        function = re.fullmatch(rf"\s*{NAME}\s*\([^)]*\)\s*=\s*.+", text)
        if function:
            error = self.evaluator.define_function(text)
            return (error, False) if error else ("function saved", True)
        assign = re.fullmatch(rf"\s*({NAME})\s*=\s*(.+)", text)
        name, formula = assign.groups() if assign else (None, text)
        try:
            value = self.evaluator.evaluate(formula)
            if not cmath.isfinite(value):
                raise ValueError("not finite")
        except ERRORS:
            return "Error", False
        if name:
            error = self.evaluator.save_variable(name, value)
            if error:
                return error, False
        self.evaluator.variables["ans"] = value
        return (f"{name} = " if name else "") + format_value(value), True

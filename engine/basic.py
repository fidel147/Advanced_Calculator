import cmath
import re

from engine.evaluator import Evaluator, format_value

OPERATORS = "+-×÷^∧∨⊻≪≫"
BINARY_ONLY = "×÷^∧∨⊻≪≫"      # operators that can't start an expression
SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
ERRORS = (ArithmeticError, ValueError, TypeError, SyntaxError, RecursionError)
UNDO_LIMIT = 200


class BasicCalculator:
    def __init__(self, evaluator=None):
        # one Evaluator can be shared by every mode, so variables and ans follow you around
        self.evaluator = evaluator or Evaluator()
        self._undo, self._redo = [], []
        self.clear()

    # ---------- read-only views for the UI ----------
    @property
    def variables(self):
        return self.evaluator.variables

    @property
    def functions(self):
        return self.evaluator.functions

    # ---------- state ----------
    def clear(self):
        self.expression = ""
        self.previous = ""     # shows "2+3 =" in the history area
        self.done = False      # True right after "="
        self.subscript = False  # True after pressing ↓n: digits become subscripts

    def _state(self):
        return (self.expression, self.previous, self.done, self.subscript)

    def _record(self, before):
        if self._state() != before:
            self._undo.append(before)
            del self._undo[:-UNDO_LIMIT]
            self._redo.clear()

    def undo(self):
        if self._undo:
            self._redo.append(self._state())
            self.expression, self.previous, self.done, self.subscript = self._undo.pop()
        return self.expression

    def redo(self):
        if self._redo:
            self._undo.append(self._state())
            self.expression, self.previous, self.done, self.subscript = self._redo.pop()
        return self.expression

    def press(self, key):
        before = self._state()
        if self.expression == "Error":
            self.clear()
        if key == "C":
            self.clear()
        elif key == "DEL":
            self._backspace()
        elif key == "=":
            self._equals()
        elif key == "()":
            self._paren()
        elif key == "↓n":
            self.subscript = True
        else:
            self._append({"↑n": "^", "mod": " mod "}.get(key, key), typed=True)
        self._record(before)
        return self.expression

    def insert(self, text):
        """Used by the x / f(x) menus and function keys: constants, variables, 'sin(' ..."""
        before = self._state()
        if self.expression == "Error":
            self.clear()
        self._append(text)
        self._record(before)
        return self.expression

    def save_variable(self, name):
        if "ans" not in self.variables:
            return "Calculate something first (press =)"
        return self.evaluator.save_variable(name, self.variables["ans"])

    def define_function(self, text):
        return self.evaluator.define_function(text)

    # ---------- hooks (the Programming calculator overrides these) ----------
    def _evaluate(self, text):
        return self.evaluator.evaluate(text)

    def _format(self, value):
        return format_value(value)

    # ---------- editing ----------
    def _append(self, token, typed=False):
        is_operator = token[0] in OPERATORS or token.strip() == "mod" or token == "%"
        if self.done:
            if not is_operator:        # a number after "=" starts fresh
                self.expression = ""
            elif token != "%" and (self.expression.startswith("-") or "i" in self.expression):
                self.expression = f"({self.expression})"   # -5 then ^2 means (-5)^2
            self.done = False
        if self.subscript:
            if len(token) == 1 and token in "0123456789":
                self.expression += token.translate(SUBSCRIPT)
                return
            self.subscript = False
        if not self.expression and token[0] in BINARY_ONLY:
            return
        if token == "." and "." in re.split(r"[^\d.]", self.expression)[-1]:
            return

        last = self.expression[-1:]
        if token in tuple(OPERATORS) and last in tuple(OPERATORS):
            if not (token == "-" and last in tuple("×÷^")):   # allow 2×-3
                self.expression = self.expression.rstrip(OPERATORS)

        # implicit multiplication: 2π, 3(4+5), (1+2)(3+4), π2, 2sin(, 2×10^(
        last = self.expression[-1:]
        after_number = last.isdigit() or last == "."
        after_name = last.isalpha()
        after_close = last in (")", "%")
        if token[0] == "(" or token[0].isalpha():
            need = after_number or after_name or after_close
            if token[0] == "(" and re.search(r"[^\W\d_][₀-₉]+$", self.expression):
                need = False                                   # log₂( is a function call
        elif token[0] in "0123456789.":
            need = after_name or after_close or (after_number and len(token) > 1)
        else:
            need = False
        if need:
            self.expression += "×"
        self.expression += token

    def _paren(self):
        opened = self.expression.count("(") - self.expression.count(")")
        last = self.expression[-1:]
        if opened > 0 and (last.isdigit() or last.isalpha() or last in (")", "%", "!")):
            self._append(")")
        else:
            self._append("(")

    def _backspace(self):
        if self.done:
            return
        self.subscript = False
        text = self.expression
        if text.endswith(" mod "):
            self.expression = text[:-5]
        else:   # delete a whole "sin(" at once, otherwise one character
            m = re.search(r"[^\W\d]\w*\($", text)
            self.expression = text[:m.start()] if m else text[:-1]

    def _equals(self):
        if not self.expression or self.done:
            return
        shown = self.expression
        try:
            value = self._evaluate(shown)
            if not cmath.isfinite(value):
                raise ValueError("not finite")
            result = self._format(value)
        except ERRORS:
            self.expression = "Error"
            return
        self.variables["ans"] = value
        self.previous = shown + " ="
        self.expression = result
        self.done = True

import re

from engine import library
from engine.basic import BasicCalculator, ERRORS
from engine.evaluator import format_value

BASES = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
WORD_SIZES = (8, 16, 32, 64)
HEX = "0123456789ABCDEF"

# a run of digits that is not part of a name: FF, 1010, but not "abs(" or "log₂"
NUMBER = re.compile(r"(?<![A-Za-z_0-9₀-₉])[0-9A-Fa-f]+(?![A-Za-z_(₀-₉])")


def to_base(n, base):
    digits = ""
    while True:
        n, d = divmod(n, base)
        digits = HEX[d] + digits
        if n == 0:
            return digits


class ProgrammingCalculator(BasicCalculator):
    """Same keypad logic as Basic, but numbers live in a base (2/8/10/16) and a word size."""

    def __init__(self, evaluator=None):
        self.base = 10
        super().__init__(evaluator)
        library.WORD["bits"] = 64
        self.bits = 64

    @property
    def mask(self):
        return (1 << self.bits) - 1

    # ---------- settings ----------
    def set_bits(self, bits):
        value = self._current_value()
        self.bits = library.WORD["bits"] = bits
        self._show(value)

    def set_base(self, base):
        value = self._current_value()
        self.base = base
        self._show(value)

    def _current_value(self):
        return self.live_value() if self.expression and self.expression != "Error" else None

    def _show(self, value):
        """Re-write the input in the current base / word size."""
        if value is not None:
            self.expression = self._format(value)
            self.subscript = False

    def set_value(self, value):
        self.expression = self._format(value & self.mask)
        self.done = False
        self.subscript = False

    # ---------- evaluation ----------
    def _evaluate(self, text):
        if self.base != 10:
            text = NUMBER.sub(lambda m: str(int(m.group(), self.base)), text)
        return self.evaluator.evaluate(text)

    def _format(self, value):
        if isinstance(value, complex):
            raise ValueError("complex")
        if self.base == 10 and value != int(value):
            return format_value(value)                 # 7 ÷ 2 = 3.5
        n = int(value) & self.mask                     # the number wraps to the word size
        if self.base == 10:
            if n >> (self.bits - 1):
                n -= 1 << self.bits                    # shown signed: 255 in 8 bits is -1
            return str(n)
        return to_base(n, self.base)

    def live_value(self):
        """Current input as an unsigned word, or None if it is not a finished number yet."""
        if not self.expression or self.expression == "Error":
            return 0
        try:
            value = self._evaluate(self.expression)
            if isinstance(value, complex):
                return None
            return int(value) & self.mask
        except ERRORS:
            return None

    # ---------- typing digits ----------
    def _append(self, token, typed=False):
        if len(token) == 1 and token.upper() in HEX:
            if self.base > 10:                         # hex: A-F are digits, not names
                if self.done:
                    self.expression, self.done = "", False
                if self.expression[-1:] in (")", "%"):
                    self.expression += "×"
                self.expression += token.upper()
                return
            if typed and token.upper() not in "0123456789":
                return                                 # letters only count in hex
            if typed and int(token) >= self.base:
                return                                 # 8 and 9 in binary / octal
        elif token == "." and self.base != 10:
            return
        super()._append(token, typed)

import tkinter as tk

from engine import library
from engine.programming import BASES, WORD_SIZES, ProgrammingCalculator
from ui import theme
from ui.modes.advanced import ANGLE_LABELS
from ui.modes.basic import BasicMode

# 50 columns: a GNOME column is 5 units wide, the hex digits are 3 units wide
_TOP = ["⇧", "x²", "xʸ", "twos", "⌈x⌉", "C", "↑n", "↓n", "÷", "mod"]
_LEFT = [["∧", "∨", "logᵧ", "swap", "⌊x⌋"],
         ["¬", "⊻", "log", "int", "|x|"],
         ["≪", "≫", "log₂", "frac", "x!"]]
_DIGITS = [["B", "hC", "D", "E", "F"],          # "hC" is the hex digit C (plain "C" clears)
           ["6", "7", "8", "9", "A"],
           ["1", "2", "3", "4", "5"]]
_OPS = [("×", "%"), ("-", "()"), ("+", "=")]
LAYOUT = [(key, 0, i * 5, 1, 5) for i, key in enumerate(_TOP)]
for r in range(3):
    row = r + 1
    LAYOUT += [(key, row, i * 5, 1, 5) for i, key in enumerate(_LEFT[r])]
    LAYOUT += [(key, row, 25 + i * 3, 1, 3) for i, key in enumerate(_DIGITS[r])]
    LAYOUT += [(_OPS[r][0], row, 40, 1, 5)]
    LAYOUT += [(_OPS[r][1], row, 45, 2 if _OPS[r][1] == "=" else 1, 5)]
LAYOUT += [("BASE", 4, 0, 1, 10), ("BITS", 4, 10, 1, 10),
           ("0", 4, 25, 1, 5), (".", 4, 30, 1, 5), ("x", 4, 35, 1, 5), ("f(x)", 4, 40, 1, 5)]


class BitGrid(tk.Frame):
    """The 64 bits, as in GNOME Calculator. Click a bit to flip it."""

    def __init__(self, parent, on_toggle):
        super().__init__(parent, bg=theme.BG)
        self.labels = {}
        for top in (63, 31):
            row = tk.Frame(self, bg=theme.BG)
            row.pack()
            self._marker(row, top)
            for n in range(32):
                bit = top - n
                if n == 16:
                    self._marker(row, bit)
                label = tk.Label(row, text="0", bg=theme.BG, fg=theme.BIT_OFF, cursor="hand2",
                                 font=(theme.FONT, -15, "bold"))
                label.pack(side="left", padx=(0, 9 if n % 4 == 3 else 1))
                label.bind("<ButtonRelease-1>", lambda e, b=bit: on_toggle(b))
                self.labels[bit] = label
            self._marker(row, top - 31)

    @staticmethod
    def _marker(row, number):
        tk.Label(row, text=str(number), bg=theme.BG, fg=theme.DIM, width=3,
                 font=(theme.FONT, -11)).pack(side="left")

    def show(self, value, size):
        for bit, label in self.labels.items():
            if bit >= size:
                label.configure(text="0", fg=theme.BIT_OUTSIDE)
            else:
                on = (value >> bit) & 1
                label.configure(text=str(on), fg=theme.BIT_ON if on else theme.BIT_OFF)


class ProgrammingMode(BasicMode):
    COLUMNS = 50
    LAYOUT = LAYOUT
    LABELS = {**BasicMode.LABELS, "⇧": "⇧⁻¹", "hC": "C", "BASE": "Decimal ▾", "BITS": "64-bit ▾"}
    DIGITS = set("0123456789ABDEF") | {"hC"}
    SHIFT_KEY = "⇧"
    INSERTS = {
        "x²": "^2", "xʸ": "^", "x!": "!", "|x|": "abs(", "twos": "twos(", "swap": "swap(",
        "⌈x⌉": "ceil(", "⌊x⌋": "floor(", "int": "trunc(", "frac": "frac(",
        "log": "log(", "log₂": "log₂(", "hC": "C",
        "∧": "∧", "∨": "∨", "⊻": "⊻", "¬": "¬", "≪": "≪", "≫": "≫",
    }
    SHIFTED = {"x²": ("√x", "sqrt("), "xʸ": ("ʸ√x", "^(1÷"),
               "log": ("10ˣ", "10^("), "log₂": ("2ˣ", "2^(")}
    TYPED = BasicMode.TYPED + "!"
    CHARS = {**BasicMode.CHARS, "&": "∧", "|": "∨", "~": "¬"}

    def make_calculator(self, evaluator):
        return ProgrammingCalculator(evaluator)

    def build_extra(self):
        self.bit_grid = BitGrid(self, self._toggle_bit)
        self.bit_grid.grid(row=2, column=0, pady=(6, 0))
        self._last_value = 0

    def after_build(self):
        self._sync_digits()

    def after_refresh(self):
        value = self.calc.live_value()
        if value is not None:
            self._last_value = value
        self.bit_grid.show(self._last_value, self.calc.bits)

    # ---------- keys ----------
    def key_from_event(self, event):
        ch = event.char
        if self.calc.base == 16 and ch and ch.upper() in "ABCDEF":
            return "hC" if ch.upper() == "C" else ch.upper()
        return super().key_from_event(event)

    def run_special(self, key):
        if key == "BASE":
            self._menu(key, [(b, name, "") for b, name in BASES.items()], self.calc.base, self._set_base)
            return True
        if key == "BITS":
            self._menu(key, [(n, f"{n}-bit", "") for n in WORD_SIZES], self.calc.bits, self._set_bits)
            return True
        return False

    def _menu(self, key, items, current, on_pick):
        if self.app:
            self.app.menu.open(self.buttons[key], items, current, on_pick, below=False)

    def _set_base(self, base):
        self.calc.set_base(base)
        self.buttons["BASE"].set_text(f"{BASES[base]} ▾")
        self._sync_digits()
        self._refresh()

    def _set_bits(self, bits):
        self.calc.set_bits(bits)
        self.buttons["BITS"].set_text(f"{bits}-bit ▾")
        self._refresh()

    def _toggle_bit(self, bit):
        if bit >= self.calc.bits:
            return
        value = self.calc.live_value()
        if value is not None:
            self.calc.set_value(value ^ (1 << bit))
            self._refresh()

    def _sync_digits(self):
        base = self.calc.base
        for key, button in self.buttons.items():
            if key in self.DIGITS:
                digit = "C" if key == "hC" else key
                button.set_enabled(int(digit, 16) < base)
        self.buttons["."].set_enabled(base == 10)

    def on_show(self):
        library.WORD["bits"] = self.calc.bits           # word size is shared with the evaluator
        super().on_show()

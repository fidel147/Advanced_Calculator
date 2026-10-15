from engine import finance
from ui.modes.advanced import MATH_INSERTS, MATH_SHIFTED
from ui.modes.basic import BasicMode

# 30 columns: every GNOME column is 3 units wide, the financial keys are 5 units wide
_RIGHT = [  # the number block, columns 15..29
    ("7", 1, 15), ("8", 1, 18), ("9", 1, 21), ("×", 1, 24), ("%", 1, 27),
    ("4", 2, 15), ("5", 2, 18), ("6", 2, 21), ("-", 2, 24), ("()", 2, 27),
    ("1", 3, 15), ("2", 3, 18), ("3", 3, 21), ("+", 3, 24),
]
LAYOUT = (
    [(key, 0, col * 3, 1, 3) for col, key in enumerate(
        ["⇧", "x²", "xʸ", "log", "ln", "C", "↑n", "↓n", "÷", "mod"])]
    + [(key, row, col, 1, 3) for key, row, col in _RIGHT]
    + [("=", 3, 27, 2, 3)]
    + [(key, 1 + i // 3, (i % 3) * 5, 1, 5) for i, key in enumerate(
        ["Ctrm", "Ddb", "Fv", "Gpm", "Pmt", "Pv", "Rate", "Sln", "Syd"])]
    + [("Term", 4, 0, 1, 5), ("Currency Conversion", 4, 5, 1, 10),
       ("0", 4, 15, 1, 3), (".", 4, 18, 1, 3), ("x", 4, 21, 1, 3), ("f(x)", 4, 24, 1, 3)]
)
LAYOUT = [item if len(item) > 3 else (*item, 1, 1) for item in LAYOUT]


class FinancialMode(BasicMode):
    COLUMNS = 30
    LAYOUT = LAYOUT
    LABELS = {**BasicMode.LABELS, "⇧": "⇧⁻¹"}
    MENU_KEYS = ("x", "f(x)") + tuple(finance.SPECS)       # these open a popup
    SHIFT_KEY = "⇧"
    INSERTS = {k: v for k, v in MATH_INSERTS.items() if k in ("x²", "xʸ", "log", "ln")}
    SHIFTED = {k: v for k, v in MATH_SHIFTED.items() if k in ("x²", "xʸ", "log", "ln")}

    def run_special(self, key):
        if key == "Currency Conversion" and self.app:
            self.app.show("Conversion", category="Currency")
            return True
        return key == "Currency Conversion"

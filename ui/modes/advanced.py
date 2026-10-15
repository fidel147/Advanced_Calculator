from ui.modes.basic import BasicMode

ANGLE_LABELS = {"deg": "Deg", "rad": "Rad", "grad": "Grad"}
ANGLE_NEXT = {"deg": "rad", "rad": "grad", "grad": "deg"}

# 10 columns, as in GNOME Calculator
LAYOUT = [
    ("⇧", 0, 0), ("x²", 0, 1), ("xʸ", 0, 2), ("conj", 0, 3), ("x⁻¹", 0, 4),
    ("C", 0, 5), ("↑n", 0, 6), ("↓n", 0, 7), ("÷", 0, 8), ("mod", 0, 9),
    ("sin", 1, 0), ("sinh", 1, 1), ("logᵧ", 1, 2), ("Arg", 1, 3), ("[x]", 1, 4),
    ("7", 1, 5), ("8", 1, 6), ("9", 1, 7), ("×", 1, 8), ("%", 1, 9),
    ("cos", 2, 0), ("cosh", 2, 1), ("log", 2, 2), ("Re", 2, 3), ("|x|", 2, 4),
    ("4", 2, 5), ("5", 2, 6), ("6", 2, 7), ("-", 2, 8), ("()", 2, 9),
    ("tan", 3, 0), ("tanh", 3, 1), ("ln", 3, 2), ("Im", 3, 3), ("x!", 3, 4),
    ("1", 3, 5), ("2", 3, 6), ("3", 3, 7), ("+", 3, 8), ("=", 3, 9, 2),
    ("Deg", 4, 0), ("π", 4, 1), ("e", 4, 2), ("i", 4, 3), ("×10ʸ", 4, 4),
    ("0", 4, 5), (".", 4, 6), ("x", 4, 7), ("f(x)", 4, 8),
]

# the shared math keys (Financial and Programming use some of these too)
MATH_INSERTS = {
    "x²": "^2", "xʸ": "^", "x⁻¹": "^(-1)", "x!": "!", "|x|": "abs(", "[x]": "round(",
    "sin": "sin(", "cos": "cos(", "tan": "tan(", "sinh": "sinh(", "cosh": "cosh(", "tanh": "tanh(",
    "log": "log(", "ln": "ln(", "conj": "conj(", "Re": "re(", "Im": "im(", "Arg": "arg(",
    "π": "π", "e": "e", "i": "i", "×10ʸ": "×10^(",
}
MATH_SHIFTED = {
    "x²": ("√x", "sqrt("), "xʸ": ("ʸ√x", "^(1÷"),
    "sin": ("sin⁻¹", "asin("), "cos": ("cos⁻¹", "acos("), "tan": ("tan⁻¹", "atan("),
    "sinh": ("sinh⁻¹", "asinh("), "cosh": ("cosh⁻¹", "acosh("), "tanh": ("tanh⁻¹", "atanh("),
    "ln": ("eˣ", "e^("), "log": ("10ˣ", "10^("),
}


class AdvancedMode(BasicMode):
    COLUMNS = 10
    LAYOUT = LAYOUT
    LABELS = {**BasicMode.LABELS, "⇧": "⇧⁻¹"}
    SHIFT_KEY = "⇧"
    INSERTS = MATH_INSERTS
    SHIFTED = MATH_SHIFTED
    TYPED = BasicMode.TYPED + "!"

    def run_special(self, key):
        evaluator = self.calc.evaluator
        if key == "Deg":                              # Deg -> Rad -> Grad
            evaluator.angle = ANGLE_NEXT[evaluator.angle]
            self.buttons["Deg"].set_text(ANGLE_LABELS[evaluator.angle])
            return True
        if key == "logᵧ":                             # type the base as a subscript, then (
            self.calc.insert("log")
            self.calc.subscript = True
            return True
        return False

    def on_show(self):
        if "Deg" in self.buttons:
            self.buttons["Deg"].set_text(ANGLE_LABELS[self.calc.evaluator.angle])
        super().on_show()

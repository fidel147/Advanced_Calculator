import tkinter as tk

import customtkinter as ctk

from engine.basic import BasicCalculator
from ui import theme
from ui.popover import Popover
from ui.widgets import SoftButton

# (key, row, column, rowspan, columnspan) - the last two are optional
LAYOUT = [
    ("C", 0, 0), ("↑n", 0, 1), ("↓n", 0, 2), ("÷", 0, 3), ("mod", 0, 4),
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("×", 1, 3), ("%", 1, 4),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("-", 2, 3), ("()", 2, 4),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("+", 3, 3), ("=", 3, 4, 2),
    ("0", 4, 0), (".", 4, 1), ("x", 4, 2), ("f(x)", 4, 3),
]


class BasicMode(ctk.CTkFrame):
    """The keypad screen. Advanced, Financial and Programming reuse it with another layout."""

    # ---- what a subclass changes ----
    COLUMNS = 5
    LAYOUT = LAYOUT
    LABELS = {"x": "x ▾", "f(x)": "f(x) ▾", "-": "−"}
    DIGITS = set("0123456789")
    MENU_KEYS = ("x", "f(x)")          # buttons that open a popup
    INSERTS = {}                       # key -> text put into the expression ("sin" -> "sin(")
    SHIFT_KEY = None                   # key id of the ⇧ button, if there is one
    SHIFTED = {}                       # key -> (label, text) while ⇧ is on
    SPECIAL = {"Return": "=", "KP_Enter": "=", "BackSpace": "DEL", "Escape": "C"}
    CHARS = {"*": "×", "/": "÷", "^": "↑n", "=": "=", "m": "mod", "_": "↓n"}
    TYPED = "0123456789.+-%(),"
    supports_undo = True

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.calc = self.make_calculator(app.evaluator if app else None)
        self.shift = False
        self.buttons, self.toggles = {}, {}
        self.popover = Popover(self, self.calc, self._insert, self._notify)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)          # the history area takes the free space

        # history (top), input bar (middle), [extra], keypad (bottom) - GNOME Calculator proportions
        self.history = tk.Label(self, text="", anchor="se", bg=theme.HISTORY, fg=theme.DIM,
                                font=(theme.FONT, -16), padx=16, pady=12)
        self.history.surface = theme.HISTORY
        self.history.grid(row=0, column=0, sticky="nsew")

        bar = tk.Frame(self, bg=theme.INPUT, height=68)
        bar.surface = theme.INPUT
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_rowconfigure(0, weight=1)
        self.expr = tk.Label(bar, text="0", anchor="e", bg=theme.INPUT, fg=theme.TEXT,
                             font=(theme.FONT, -32), padx=16)
        self.expr.grid(row=0, column=0, sticky="nsew")
        SoftButton(bar, "⌫", lambda: self._on_press("DEL"), theme.FLAT, theme.INPUT,
                   width=48, height=36).grid(row=0, column=1, padx=(0, 12))

        self.build_extra()                           # row 2 (Programming puts its bit grid here)

        pad = tk.Frame(self, bg=theme.BG)
        pad.surface = theme.BG
        pad.grid(row=3, column=0, sticky="ew", padx=9, pady=(5, 9))
        for i in range(self.COLUMNS):
            pad.grid_columnconfigure(i, weight=1, uniform="c")
        for key, row, col, *rest in self.LAYOUT:
            rowspan = rest[0] if rest else 1
            colspan = rest[1] if len(rest) > 1 else 1
            button = self._make_button(pad, key)
            button.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
                        sticky="nsew", padx=2, pady=2)
            self.buttons[key] = button
            if key in self.MENU_KEYS:
                self.toggles[key] = button
        self.bind("<Configure>", lambda e: self.popover.reposition())
        self.after_build()
        self._refresh()

    # ---------- hooks for subclasses ----------
    def make_calculator(self, evaluator):
        return BasicCalculator(evaluator)

    def build_extra(self):
        pass

    def after_build(self):
        pass

    def after_refresh(self):
        pass

    def run_special(self, key):
        """Handle keys that are not plain inserts. Return True if the key was handled."""
        return False

    # ---------- the app calls these ----------
    def on_show(self):
        self._refresh()

    def close_popups(self):
        self.popover.close()

    def undo(self):
        self.calc.undo()
        self._refresh()

    def redo(self):
        self.calc.redo()
        self._refresh()

    # ---------- buttons ----------
    def _make_button(self, pad, key):
        if key == "=":
            colors = theme.EQUALS
        elif key in self.DIGITS:
            colors = theme.DIGIT
        else:
            colors = theme.OPERATOR
        command = lambda k=key: self._on_press(k)
        if key in self.MENU_KEYS:
            command = lambda k=key: self.popover.toggle(k, self.buttons[k])
        return SoftButton(pad, self.LABELS.get(key, key), command, colors, theme.BG,
                          height=44 if key != "=" else 40)

    def _on_press(self, key):
        if key == self.SHIFT_KEY:
            self._set_shift(not self.shift)
            return
        if not self.run_special(key):
            if self.shift and key in self.SHIFTED:
                self.calc.insert(self.SHIFTED[key][1])
            elif key in self.INSERTS:
                self.calc.insert(self.INSERTS[key])
            else:
                self.calc.press(key)
        if self.shift:
            self._set_shift(False)
        self._refresh()

    def _set_shift(self, on):
        self.shift = on
        for key, (label, _) in self.SHIFTED.items():
            self.buttons[key].set_text(label if on else self.LABELS.get(key, key))
        self.buttons[self.SHIFT_KEY].set_colors(theme.EQUALS if on else theme.OPERATOR)

    def _insert(self, text):
        self.calc.insert(text)
        self._refresh()

    def _notify(self, message):
        self.history.configure(text=message)

    def _refresh(self):
        text = self.calc.expression or "0"
        size = 32 if len(text) <= 14 else 24 if len(text) <= 20 else 18
        self.history.configure(text=self.calc.previous)
        self.expr.configure(text=text, font=(theme.FONT, -size))
        self.after_refresh()

    # ---------- keyboard and clicks (the app forwards them to the visible mode) ----------
    def key_from_event(self, event):
        key = self.SPECIAL.get(event.keysym)
        if key is None:
            ch = event.char
            key = ch if ch and ch in self.TYPED else self.CHARS.get(ch)
        return key

    def handle_key(self, event):
        if isinstance(event.widget, tk.Entry):      # typing inside a popup entry
            return
        if event.keysym == "Escape" and self.popover.is_open:
            self.popover.close()
            return
        key = self.key_from_event(event)
        if key:
            self._on_press(key)

    def handle_click(self, event):
        """Click outside the popup closes it (the popup buttons toggle it themselves)."""
        if not self.popover.is_open:
            return
        if self.popover.contains(event.widget) or event.widget in self.toggles.values():
            return
        self.popover.close()

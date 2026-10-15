import tkinter as tk

import customtkinter as ctk

from engine import conversion
from ui import theme
from ui.widgets import SoftButton

KEYS = [
    ("C", 0, 0), ("⇅", 0, 1), ("⌫", 0, 2),
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2),
    ("0", 4, 0), (".", 4, 1), ("°′″", 4, 2),
]
MAX_LENGTH = 16


class ConversionMode(ctk.CTkFrame):
    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.category = "Angle"
        self.units = list(conversion.DEFAULTS[self.category])      # [top unit, bottom unit]
        self.texts = ["0", "0"]
        self.active = 0                                            # the field you are typing in
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        area = tk.Frame(self, bg=theme.HISTORY)
        area.grid(row=0, column=0, sticky="nsew")
        self.category_button = SoftButton(area, "", self._pick_category, theme.DISPLAY_BTN,
                                          theme.HISTORY, align="w", width=170, height=34)
        self.category_button.pack(anchor="w", padx=8, pady=(10, 0))
        self.values, self.unit_buttons = [], []
        for i in range(2):
            value = tk.Label(area, text="0", anchor="w", bg=theme.HISTORY, fg=theme.TEXT,
                             font=(theme.FONT, -34), padx=16)
            value.pack(fill="x", pady=(14, 0))
            value.bind("<Button-1>", lambda e, i=i: self._activate(i))
            unit = SoftButton(area, "", lambda i=i: self._pick_unit(i), theme.DISPLAY_BTN,
                              theme.HISTORY, align="w", width=250, height=34)
            unit.pack(anchor="w", padx=8)
            self.values.append(value)
            self.unit_buttons.append(unit)
        self.note = tk.Label(area, text="", anchor="w", bg=theme.HISTORY, fg=theme.DIM,
                             font=(theme.FONT, -11), padx=16)
        self.note.pack(fill="x", pady=(6, 8))

        pad = tk.Frame(self, bg=theme.BG)
        pad.grid(row=1, column=0, sticky="ew", padx=9, pady=(5, 9))
        for i in range(3):
            pad.grid_columnconfigure(i, weight=1, uniform="c")
        self.keys = {}
        for key, row, col in KEYS:
            colors = theme.DIGIT if key.isdigit() or key == "." else theme.OPERATOR
            button = SoftButton(pad, key, lambda k=key: self._press(k), colors, theme.BG, height=48)
            button.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self.keys[key] = button
        self._refresh()

    # ---------- the app calls these ----------
    def on_show(self):
        self._refresh()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def select_category(self, category):
        self.category = category
        self.units = list(conversion.DEFAULTS[category])
        self.texts = ["0", "0"]
        self.active = 0
        self._refresh()

    # ---------- dropdowns ----------
    def _pick_category(self):
        if self.app:
            items = [(c, c, "") for c in conversion.CATEGORIES]
            self.app.menu.open(self.category_button, items, self.category, self.select_category)

    def _pick_unit(self, index):
        if self.app:
            items = [(u, u, "") for u in conversion.units(self.category)]
            self.app.menu.open(self.unit_buttons[index], items, self.units[index],
                               lambda unit, i=index: self._set_unit(i, unit))

    def _set_unit(self, index, unit):
        self.units[index] = unit
        self._refresh()

    # ---------- typing ----------
    def _activate(self, index):
        if index != self.active:
            self.active = index
            self._refresh()

    def _press(self, key):
        text = self.texts[self.active]
        if key == "C":
            text = "0"
        elif key == "⌫":
            text = text[:-1]
            if text in ("", "-"):
                text = "0"
        elif key == "⇅":                                  # swap the two units and values
            self.units.reverse()
            self.texts.reverse()
            self._refresh()
            return
        elif key == "-":                                  # from the keyboard: flip the sign
            text = "0" if text == "-" else text[1:] if text.startswith("-") \
                else "-" + ("" if text == "0" else text)
        elif key == "°′″":
            if self.category == "Angle":
                text += "″" if "′" in text and "″" not in text else \
                        "′" if "°" in text and "′" not in text else \
                        "°" if "°" not in text else ""
        elif key == ".":
            if "." not in text.split("°")[-1].split("′")[-1].split("″")[-1]:
                text += "."
        elif len(text) < MAX_LENGTH:                      # a digit
            text = key if text == "0" else text + key
        self.texts[self.active] = text
        self._refresh()

    def _refresh(self):
        other = 1 - self.active
        try:
            self.texts[other] = conversion.convert(
                self.category, self.units[self.active], self.units[other], self.texts[self.active])
            note = ""
        except (ValueError, OverflowError):
            self.texts[other] = "Error"
            note = "Can't convert that number"
        if self.category == "Currency" and not note:
            note = "Sample exchange rates - edit RATES in engine/conversion.py"
        self.note.configure(text=note)
        self.category_button.set_text(f"{self.category} ▾")
        for i in range(2):
            self.values[i].configure(text=self.texts[i],
                                     fg=theme.TEXT if i == self.active else theme.DIM)
            self.unit_buttons[i].set_text(f"{self.units[i]} ▾")
        self.keys["°′″"].set_enabled(self.category == "Angle")

    # ---------- keyboard ----------
    def handle_key(self, event):
        ch = event.char
        key = {"BackSpace": "⌫", "Escape": "C"}.get(event.keysym)
        if key is None and ch and (ch.isdigit() or ch in ".-"):
            key = ch
        if key:
            self._press(key)

    def handle_click(self, event):
        pass

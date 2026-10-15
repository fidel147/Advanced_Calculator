import importlib
import tkinter as tk

import customtkinter as ctk

from engine.evaluator import Evaluator
from ui import theme
from ui.choice import ChoiceMenu
from ui.widgets import SoftButton

# name, Ctrl+Alt shortcut, module, class, (width, height)
MODES = [
    ("Basic", "b", "ui.modes.basic", "BasicMode", (380, 580)),
    ("Advanced", "a", "ui.modes.advanced", "AdvancedMode", (700, 580)),
    ("Financial", "f", "ui.modes.financial", "FinancialMode", (700, 580)),
    ("Programming", "p", "ui.modes.programming", "ProgrammingMode", (720, 640)),
    ("Keyboard", "k", "ui.modes.keyboard", "KeyboardMode", (560, 480)),
    ("Conversion", "c", "ui.modes.conversion", "ConversionMode", (380, 600)),
    ("Scientific", "s", "ui.modes.scientific", "ScientificMode", (720, 620)),
    ("Matrix", "m", "ui.modes.matrix", "MatrixMode", (720, 620)),
    ("Numerical", "n", "ui.modes.numerical", "NumericalMode", (760, 700)),
    ("Number Theory", "t", "ui.modes.number_theory", "NumberTheoryMode", (720, 680)),
    ("Image Studio", "i", "ui.modes.image", "ImageMode", (1100, 760)),
    ("Data Lab", "d", "ui.modes.data", "DataMode", (1280, 820)),
    ("About", "h", "ui.modes.about", "AboutMode", (900, 760)),
]
INFO = {name: (module, cls, size) for name, _, module, cls, size in MODES}


class CalculatorApp(ctk.CTk):
    def __init__(self, start="Basic"):
        super().__init__(fg_color=theme.BG)
        self.title("Calculator")
        self.evaluator = Evaluator()          # shared: variables, functions and ans in every mode
        self.modes, self.current, self.current_name = {}, None, None

        self.shell = tk.Frame(self, bg=theme.BG)
        self.shell.pack(fill="both", expand=True)
        self.shell.grid_columnconfigure(0, weight=1)
        self.shell.grid_rowconfigure(1, weight=1)
        self._build_header()
        self.body = tk.Frame(self.shell, bg=theme.BG)
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_rowconfigure(0, weight=1)
        self.menu = ChoiceMenu(self.shell)     # floats over the header and the keypad

        self.bind("<Key>", self._on_key)
        self.bind("<ButtonPress-1>", self._on_click, add="+")
        for name, shortcut, *_ in MODES:
            for letter in (shortcut, shortcut.upper()):
                self.bind(f"<Control-Alt-{letter}>", lambda e, n=name: self._shortcut(n))
        self.show(start)

    # ---------- header: undo, redo, and the mode picker ----------
    def _build_header(self):
        bar = tk.Frame(self.shell, bg=theme.HEADER, height=48)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        self.undo_button = SoftButton(bar, "↶", lambda: self._history("undo"), theme.HEADER_BTN,
                                      theme.HEADER, width=36, height=32)
        self.undo_button.place(x=10, rely=0.5, anchor="w")
        self.redo_button = SoftButton(bar, "↷", lambda: self._history("redo"), theme.HEADER_BTN,
                                      theme.HEADER, width=36, height=32)
        self.redo_button.place(x=52, rely=0.5, anchor="w")
        self.title_button = SoftButton(bar, "Basic ▾", self._open_menu, theme.HEADER_BTN,
                                       theme.HEADER, width=170, height=34)
        self.title_button.place(relx=0.5, rely=0.5, anchor="center")

    def _open_menu(self):
        items = [(name, name, f"Ctrl+Alt+{shortcut.upper()}") for name, shortcut, *_ in MODES]
        self.menu.open(self.title_button, items, self.current_name, self.show,
                       below=True, center=True)

    def _history(self, which):
        if self.current is not None and self.current.supports_undo:
            getattr(self.current, which)()

    # ---------- switching modes ----------
    def show(self, name, category=None):
        self.menu.close()
        if self.current is not None:
            self.current.close_popups()
            self.current.grid_remove()
        mode = self.modes.get(name)
        if mode is None:
            module, cls, _ = INFO[name]
            mode = getattr(importlib.import_module(module), cls)(self.body, app=self)
            self.modes[name] = mode
        if category:
            mode.select_category(category)
        self.current, self.current_name = mode, name
        mode.grid(row=0, column=0, sticky="nsew")
        width, height = INFO[name][2]
        self.geometry(f"{width}x{height}")
        self.minsize(min(width, 360), min(height, 480))
        self.title_button.set_text(f"{name} ▾")
        for button in (self.undo_button, self.redo_button):
            button.set_enabled(mode.supports_undo)
        mode.on_show()

    def _shortcut(self, name):
        self.show(name)
        return "break"

    # ---------- keyboard and clicks go to the visible mode ----------
    def _on_key(self, event):
        if event.state & 0x4:                  # Ctrl+something is a shortcut, not typing
            return
        if event.keysym == "Escape" and self.menu.is_open:
            self.menu.close()
            return
        if self.current is not None:
            self.current.handle_key(event)

    def _on_click(self, event):
        if (self.menu.is_open and event.widget is not self.menu.anchor
                and not self.menu.contains(event.widget)):
            self.menu.close()
        if self.current is not None:
            self.current.handle_click(event)

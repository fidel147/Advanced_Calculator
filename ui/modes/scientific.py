import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from engine import scientific
from ui import theme
from ui.widgets import SoftButton


class ScientificMode(ctk.CTkFrame):
    """Symbolic algebra and calculus workspace backed by SymPy."""

    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = tk.Frame(self, bg=theme.HISTORY)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        header.grid_columnconfigure(1, weight=1)
        tk.Label(header, text="Symbolic mathematics", bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold")).grid(row=0, column=0, padx=(12, 18), pady=12)
        self.operation = ttk.Combobox(header, state="readonly", values=(
            "Simplify", "Expand", "Factor", "Differentiate", "Integrate", "Limit", "Solve"))
        self.operation.current(0)
        self.operation.grid(row=0, column=1, sticky="ew", padx=6)
        self.variable = ttk.Combobox(header, state="readonly", values=("x", "y", "z", "t"), width=5)
        self.variable.set("x")
        self.variable.grid(row=0, column=2, padx=6)
        SoftButton(header, "Calculate", self.calculate, theme.EQUALS, theme.HISTORY,
                   width=110, height=34).grid(row=0, column=3, padx=(6, 12))

        workspace = tk.Frame(self, bg=theme.BG)
        workspace.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(2, weight=1)
        tk.Label(workspace, text="Expression or equation", bg=theme.BG, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=0, column=0, sticky="ew")
        self.expression = tk.Entry(workspace, bg=theme.INPUT, fg=theme.TEXT,
                                   insertbackground=theme.TEXT, relief="flat", bd=0,
                                   font=(theme.FONT, -18), highlightthickness=1,
                                   highlightbackground=theme.POPOVER_BORDER)
        self.expression.grid(row=1, column=0, sticky="ew", ipady=10, pady=(4, 12))
        self.expression.insert(0, "sin(x)^2 + cos(x)^2")
        self.expression.bind("<Return>", lambda _event: self.calculate())

        result_panel = tk.Frame(workspace, bg=theme.HISTORY)
        result_panel.grid(row=2, column=0, sticky="nsew")
        result_panel.grid_columnconfigure(0, weight=1)
        result_panel.grid_rowconfigure(1, weight=1)
        tk.Label(result_panel, text="Verified result", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        self.result = tk.Text(result_panel, bg=theme.HISTORY, fg=theme.TEXT,
                              insertbackground=theme.TEXT, relief="flat", bd=0,
                              wrap="word", font=(theme.FONT, -18), padx=14, pady=10)
        self.result.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.result.configure(state="disabled")
        self.note = tk.Label(workspace, text="Examples: x^2 + 2*x + 1 | diff: sin(x) | solve: x^2 - 4 = 0",
                             bg=theme.BG, fg=theme.DIM, anchor="w", font=(theme.FONT, -10))
        self.note.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self.calculate()

    def calculate(self):
        try:
            value = scientific.calculate(self.expression.get(), self.operation.get(), self.variable.get())
            text = scientific.format_result(value)
            self._show_result(text, theme.TEXT)
        except (TypeError, ValueError, SyntaxError) as error:
            self._show_result(str(error), theme.ERROR)

    def _show_result(self, text, color):
        self.result.configure(state="normal", fg=color)
        self.result.delete("1.0", "end")
        self.result.insert("1.0", text)
        self.result.configure(state="disabled")

    def on_show(self):
        self.expression.focus_set()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def handle_key(self, event):
        if event.keysym == "Return":
            self.calculate()

    def handle_click(self, _event):
        pass
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from engine import numerical
from ui import theme
from ui.widgets import SoftButton


class NumericalMode(ctk.CTkFrame):
    """Numerical methods workspace with convergence information."""

    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        header = tk.Frame(self, bg=theme.HISTORY)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        header.grid_columnconfigure(1, weight=1)
        tk.Label(header, text="Numerical methods", bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold")).grid(row=0, column=0, padx=(12, 18), pady=12)
        self.method = ttk.Combobox(header, state="readonly", values=(
            "Bisection", "Newton-Raphson", "Secant", "Brent", "Numerical integral", "Numerical derivative"))
        self.method.current(0)
        self.method.grid(row=0, column=1, sticky="ew", padx=6)
        SoftButton(header, "Run", self.calculate, theme.EQUALS, theme.HISTORY,
                   width=90, height=34).grid(row=0, column=2, padx=(6, 12))

        workspace = tk.Frame(self, bg=theme.BG)
        workspace.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(5, weight=1)
        self._label(workspace, "Function f(x)", 0)
        self.expression = self._entry(workspace, "x^2 - 2", 1)
        self._label(workspace, "Start / left bound", 2)
        self.first = self._entry(workspace, "0", 3)
        self._label(workspace, "End / right bound / step", 4)
        self.second = self._entry(workspace, "2", 5)
        self._label(workspace, "Tolerance", 6)
        self.tolerance = self._entry(workspace, "1e-8", 7)
        result_panel = tk.Frame(workspace, bg=theme.HISTORY)
        result_panel.grid(row=8, column=0, sticky="nsew", pady=(14, 0))
        result_panel.grid_columnconfigure(0, weight=1)
        result_panel.grid_rowconfigure(1, weight=1)
        tk.Label(result_panel, text="Result and convergence", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        self.result = tk.Text(result_panel, bg=theme.HISTORY, fg=theme.TEXT,
                              relief="flat", bd=0, wrap="word", font=(theme.FONT, -16),
                              padx=14, pady=10)
        self.result.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.result.configure(state="disabled")
        self.note = tk.Label(workspace, text="Root methods need a bracket or starting values. Integral uses bounds; derivative uses the second field as x.",
                             bg=theme.BG, fg=theme.DIM, anchor="w", justify="left",
                             wraplength=680, font=(theme.FONT, -10))
        self.note.grid(row=9, column=0, sticky="ew", pady=(8, 0))
        self.calculate()

    @staticmethod
    def _label(parent, text, row):
        tk.Label(parent, text=text, bg=theme.BG, fg=theme.DIM, anchor="w",
                 font=(theme.FONT, -11)).grid(row=row, column=0, sticky="ew")

    @staticmethod
    def _entry(parent, value, row):
        entry = tk.Entry(parent, bg=theme.INPUT, fg=theme.TEXT, insertbackground=theme.TEXT,
                         relief="flat", bd=0, font=(theme.FONT, -14), highlightthickness=1,
                         highlightbackground=theme.POPOVER_BORDER)
        entry.insert(0, value)
        entry.grid(row=row, column=0, sticky="ew", ipady=7, pady=(2, 5))
        return entry

    def calculate(self):
        try:
            expression = self.expression.get()
            first = float(self.first.get())
            second = float(self.second.get())
            tolerance = float(self.tolerance.get())
            method = self.method.get()
            if method == "Bisection":
                result = numerical.bisection(expression, first, second, tolerance)
            elif method == "Newton-Raphson":
                result = numerical.newton(expression, first, tolerance)
            elif method == "Secant":
                result = numerical.secant(expression, first, second, tolerance)
            elif method == "Brent":
                result = numerical.brent(expression, first, second, tolerance)
            elif method == "Numerical integral":
                result = numerical.integrate(expression, first, second)
            else:
                result = numerical.differentiate(expression, second, tolerance)
            text = (f"value = {result.value:.12g}\n"
                    f"iterations = {result.iterations}\n"
                    f"residual / estimated error = {result.residual:.6g}\n"
                    f"converged = {result.converged}")
            self._show_result(text, theme.TEXT)
        except (TypeError, ValueError, OverflowError) as error:
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

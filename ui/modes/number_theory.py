import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from engine import number_theory
from ui import theme
from ui.widgets import SoftButton


class NumberTheoryMode(ctk.CTkFrame):
    """Integer arithmetic and number-theory workspace."""

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
        tk.Label(header, text="Number theory", bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold")).grid(row=0, column=0, padx=(12, 18), pady=12)
        self.operation = ttk.Combobox(header, state="readonly", values=(
            "Prime test", "Prime factorization", "GCD", "LCM", "Modular inverse",
            "Modular power", "Fibonacci", "Divisors", "Euler totient"))
        self.operation.current(0)
        self.operation.grid(row=0, column=1, sticky="ew", padx=6)
        SoftButton(header, "Calculate", self.calculate, theme.EQUALS, theme.HISTORY,
                   width=110, height=34).grid(row=0, column=2, padx=(6, 12))

        workspace = tk.Frame(self, bg=theme.BG)
        workspace.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(7, weight=1)
        self._label(workspace, "First integer / value", 0)
        self.first = self._entry(workspace, "84", 1)
        self._label(workspace, "Second integer / modulus", 2)
        self.second = self._entry(workspace, "30", 3)
        self._label(workspace, "Exponent / third value", 4)
        self.third = self._entry(workspace, "7", 5)
        result_panel = tk.Frame(workspace, bg=theme.HISTORY)
        result_panel.grid(row=7, column=0, sticky="nsew", pady=(14, 0))
        result_panel.grid_columnconfigure(0, weight=1)
        result_panel.grid_rowconfigure(1, weight=1)
        tk.Label(result_panel, text="Result", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        self.result = tk.Text(result_panel, bg=theme.HISTORY, fg=theme.TEXT,
                              relief="flat", bd=0, wrap="word", font=(theme.FONT, -18), padx=14, pady=10)
        self.result.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.result.configure(state="disabled")
        self.note = tk.Label(workspace, text="Use the second field for GCD, LCM, modular inverse, and modular power.",
                             bg=theme.BG, fg=theme.DIM, anchor="w", font=(theme.FONT, -10))
        self.note.grid(row=8, column=0, sticky="ew", pady=(8, 0))
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
            operation = self.operation.get()
            first = self.first.get()
            second = self.second.get()
            third = self.third.get()
            if operation == "Prime test":
                value = number_theory.is_prime(first)
            elif operation == "Prime factorization":
                factors = number_theory.factorize(first)
                value = " * ".join(str(prime) + (f"^{power}" if power > 1 else "")
                                   for prime, power in factors.items())
            elif operation == "GCD":
                value = number_theory.gcd(first, second)
            elif operation == "LCM":
                value = number_theory.lcm(first, second)
            elif operation == "Modular inverse":
                value = number_theory.modular_inverse(first, second)
            elif operation == "Modular power":
                value = number_theory.modular_power(first, second, third)
            elif operation == "Fibonacci":
                value = number_theory.fibonacci(first)
            elif operation == "Divisors":
                value = number_theory.divisors(first)
            else:
                value = number_theory.totient(first)
            self._show_result(str(value), theme.TEXT)
        except (TypeError, ValueError, OverflowError) as error:
            self._show_result(str(error), theme.ERROR)

    def _show_result(self, text, color):
        self.result.configure(state="normal", fg=color)
        self.result.delete("1.0", "end")
        self.result.insert("1.0", text)
        self.result.configure(state="disabled")

    def on_show(self):
        self.first.focus_set()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def handle_key(self, event):
        if event.keysym == "Return":
            self.calculate()

    def handle_click(self, _event):
        pass

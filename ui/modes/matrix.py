import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
import numpy as np

from engine import matrix
from ui import theme
from ui.widgets import SoftButton


class MatrixMode(ctk.CTkFrame):
    """Matrix and vector calculator with explicit A/B inputs."""

    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        toolbar = tk.Frame(self, bg=theme.HISTORY)
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        toolbar.grid_columnconfigure(1, weight=1)
        tk.Label(toolbar, text="Matrix laboratory", bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold")).grid(row=0, column=0, padx=(12, 18), pady=12)
        self.operation = ttk.Combobox(toolbar, state="readonly", values=matrix.OPERATIONS)
        self.operation.current(0)
        self.operation.grid(row=0, column=1, sticky="ew", padx=6)
        SoftButton(toolbar, "Calculate", self.calculate, theme.EQUALS, theme.HISTORY,
                   width=110, height=34).grid(row=0, column=2, padx=(6, 12))

        workspace = tk.Frame(self, bg=theme.BG)
        workspace.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=1)
        workspace.grid_rowconfigure(3, weight=1)
        self.left = self._matrix_input(workspace, "Matrix A", "1 2; 3 4", 0)
        self.right = self._matrix_input(workspace, "Matrix B or vector b", "5 6; 7 8", 1)

        result_panel = tk.Frame(workspace, bg=theme.HISTORY)
        result_panel.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(14, 0))
        result_panel.grid_columnconfigure(0, weight=1)
        result_panel.grid_rowconfigure(1, weight=1)
        tk.Label(result_panel, text="Verified result", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        self.result = tk.Text(result_panel, bg=theme.HISTORY, fg=theme.TEXT,
                              relief="flat", bd=0, wrap="word", font=(theme.FONT, -18),
                              padx=14, pady=10)
        self.result.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 8))
        self.result.configure(state="disabled")
        self.note = tk.Label(workspace, text="Rows: 1 2; 3 4    Columns may also be comma-separated.",
                             bg=theme.BG, fg=theme.DIM, anchor="w", font=(theme.FONT, -10))
        self.note.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.calculate()

    @staticmethod
    def _matrix_input(parent, label, initial, column):
        frame = tk.Frame(parent, bg=theme.BG)
        frame.grid(row=1, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column == 0 else 0))
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        tk.Label(frame, text=label, bg=theme.BG, fg=theme.DIM, anchor="w",
                 font=(theme.FONT, -11)).grid(row=0, column=0, sticky="ew")
        entry = tk.Text(frame, height=5, bg=theme.INPUT, fg=theme.TEXT,
                        insertbackground=theme.TEXT, relief="flat", bd=0,
                        font=(theme.FONT, -14), padx=10, pady=8)
        entry.insert("1.0", initial)
        entry.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        return entry

    def calculate(self):
        try:
            value = matrix.calculate(self.operation.get(), self.left.get("1.0", "end"),
                                     self.right.get("1.0", "end"))
            self._show_result(matrix.format_result(value), theme.TEXT)
        except (TypeError, ValueError, np.linalg.LinAlgError) as error:
            self._show_result(str(error), theme.ERROR)

    def _show_result(self, text, color):
        self.result.configure(state="normal", fg=color)
        self.result.delete("1.0", "end")
        self.result.insert("1.0", text)
        self.result.configure(state="disabled")

    def on_show(self):
        self.left.focus_set()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def handle_key(self, event):
        if event.keysym == "F5":
            self.calculate()

    def handle_click(self, _event):
        pass

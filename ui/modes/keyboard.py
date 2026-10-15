import tkinter as tk

import customtkinter as ctk

from engine.keyboard import KeyboardCalculator
from ui import theme


class KeyboardMode(ctk.CTkFrame):
    """Type expressions and press Enter. Up / Down bring back what you typed before."""

    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.calc = KeyboardCalculator(app.evaluator if app else None)
        self.typed, self.recall = [], 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.log = tk.Text(self, bg=theme.HISTORY, fg=theme.TEXT, bd=0, highlightthickness=0,
                           relief="flat", wrap="word", state="disabled", cursor="arrow",
                           padx=16, pady=12, takefocus=0, font=(theme.FONT, -16))
        self.log.tag_configure("expr", justify="right", foreground=theme.DIM, font=(theme.FONT, -16))
        self.log.tag_configure("ok", justify="right", font=(theme.FONT, -26))
        self.log.tag_configure("bad", justify="right", foreground=theme.ERROR, font=(theme.FONT, -18))
        self.log.bind("<Button-1>", self._focus_entry)
        self.log.grid(row=0, column=0, sticky="nsew")

        bar = tk.Frame(self, bg=theme.INPUT, height=64)
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_rowconfigure(0, weight=1)
        self.entry = tk.Entry(bar, bg=theme.INPUT, fg=theme.TEXT, insertbackground=theme.TEXT,
                              relief="flat", bd=0, highlightthickness=0, font=(theme.FONT, -22))
        self.entry.grid(row=0, column=0, sticky="nsew", padx=16, pady=10)
        for sequence in ("<Return>", "<KP_Enter>"):
            self.entry.bind(sequence, self._submit)
        self.entry.bind("<Up>", lambda e: self._history(-1))
        self.entry.bind("<Down>", lambda e: self._history(1))
        self.entry.bind("<Escape>", lambda e: self.entry.delete(0, "end"))

    # ---------- the app calls these ----------
    def on_show(self):
        self.entry.focus_set()

    def close_popups(self):
        pass

    def handle_key(self, event):
        pass                                   # the entry box takes the typing

    def handle_click(self, event):
        pass

    # ---------- behaviour ----------
    def _focus_entry(self, event=None):
        self.entry.focus_set()
        return "break"

    def _submit(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        message, ok = self.calc.submit(text)
        self.typed.append(text)
        self.recall = len(self.typed)
        self.entry.delete(0, "end")
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n", "expr")
        self.log.insert("end", ("= " if ok else "") + message + "\n", "ok" if ok else "bad")
        self.log.configure(state="disabled")
        self.log.see("end")

    def _history(self, step):
        if not self.typed:
            return
        self.recall = max(0, min(len(self.typed), self.recall + step))
        self.entry.delete(0, "end")
        if self.recall < len(self.typed):
            self.entry.insert(0, self.typed[self.recall])

import tkinter as tk

from engine import finance
from engine.basic import ERRORS
from engine.evaluator import format_value
from engine.library import CONSTANTS, EXTRA_SYMBOLS, FUNCTIONS, HINTS
from ui import theme
from ui.widgets import Panel, SoftButton

FUNCTION_GROUPS = ("Trigonometry", "Complex", "Programming", "Rounding", "Statistics", "Sundry")
MAX_LISTED = 6      # most recent saved variables / functions shown in the list
WIDTH = 330


class Popover:
    """The x and f(x) popups. They live inside the window, so they can't land off-screen."""

    def __init__(self, host, calc, insert, notify):
        self.host, self.calc, self.insert, self.notify = host, calc, insert, notify
        self.panel = self.kind = self.page = self.anchor = self._status = None

    # ---------- open / close ----------
    @property
    def is_open(self):
        return self.panel is not None

    def contains(self, widget):
        while widget is not None:
            if widget is self.panel:
                return True
            widget = getattr(widget, "master", None)
        return False

    def toggle(self, kind, anchor):
        was_same = self.is_open and self.kind == kind
        self.close()
        if was_same:
            return
        self.kind, self.anchor, self.page = kind, anchor, None
        self.panel = Panel(self.host, theme.POPOVER, theme.POPOVER_BORDER)
        self._render()

    def close(self):
        if self.panel is not None:
            self.panel.destroy()
        self.panel = self.kind = self.page = self.anchor = self._status = None
        self.host.winfo_toplevel().focus_set()

    # ---------- pages ----------
    def _render(self):
        inner = self.panel.inner
        for child in inner.winfo_children():
            child.destroy()
        if self.page is not None:
            self._category(inner)
        elif self.kind == "x":
            self._variables_page(inner)
        elif self.kind in finance.SPECS:
            self._form_page(inner)
        else:
            self._functions_page(inner)
        self.reposition()
        if self.kind in finance.SPECS and self.page is None:
            self.first_field.focus_set()

    def _variables_page(self, inner):
        variables = self.calc.variables
        if "ans" in variables:
            self._row(inner, "ans", lambda: self._pick("ans"), hint=format_value(variables["ans"]))
        self._row(inner, "rand", lambda: self._pick("rand"), hint="random 0 to 1")
        for name, value in [(n, v) for n, v in variables.items() if n != "ans"][-MAX_LISTED:]:
            self._row(inner, name, lambda n=name: self._pick(n), hint=format_value(value))
        self._separator(inner)
        self._section(inner, "Constants")
        for group in CONSTANTS:
            self._row(inner, group, lambda g=group: self._open(g), arrow=True)
        self._separator(inner)
        self._entry_row(inner, "Variable name", "Save", self._save_variable)

    def _functions_page(self, inner):
        for group in FUNCTION_GROUPS:
            self._row(inner, group, lambda g=group: self._open(g), arrow=True)
        mine = list(self.calc.functions.items())[-MAX_LISTED:]
        if mine:
            self._separator(inner)
            self._section(inner, "My functions")
            for name, (params, _) in mine:
                self._row(inner, f"{name}({', '.join(params)})", lambda n=name: self._pick(n + "("))
        self._separator(inner)
        self._entry_row(inner, "f(x) = x^2 + 1", "+", self._define_function)

    def _form_page(self, inner):
        """Financial functions: a few labelled fields and a Calculate button."""
        title, labels, compute = finance.SPECS[self.kind]
        self._section(inner, title)
        entries = []
        for label in labels:
            tk.Label(inner, text=label, bg=theme.POPOVER, fg=theme.DIM, anchor="w",
                     font=(theme.FONT, -12)).pack(fill="x", padx=12, pady=(6, 0))
            entry = tk.Entry(inner, bg=theme.ENTRY, fg=theme.TEXT, insertbackground=theme.TEXT,
                             relief="flat", bd=0, font=(theme.FONT, -14), highlightthickness=1,
                             highlightbackground=theme.POPOVER_BORDER, highlightcolor=theme.EQUALS[0])
            entry.pack(fill="x", padx=10, ipady=5)
            entries.append(entry)
        self.first_field = entries[0]

        def run(_=None):
            try:
                values = [self.calc.evaluator.evaluate(e.get()) for e in entries]
                if any(isinstance(v, complex) for v in values):
                    raise ValueError("complex")
                result = compute(*values)
            except ERRORS:
                self._say("Check the numbers")
                return
            self.close()
            self.insert(format_value(result))

        def next_or_run(index):
            if index + 1 < len(entries):
                entries[index + 1].focus_set()
            else:
                run()

        for i, entry in enumerate(entries):
            entry.bind("<Return>", lambda e, i=i: next_or_run(i))
        SoftButton(inner, "Calculate", run, theme.EQUALS, theme.POPOVER,
                   radius=6, width=100, height=34).pack(pady=(10, 0))
        self._status = tk.Label(inner, text=" ", bg=theme.POPOVER, fg=theme.DIM, anchor="w",
                                font=(theme.FONT, -12))
        self._status.pack(fill="x", padx=12, pady=(4, 2))

    def _category(self, inner):
        self._row(inner, "←   " + self.page, self._back)
        self._separator(inner)
        if self.kind == "x":
            for symbol, description, value in CONSTANTS[self.page]:
                self._row(inner, f"{symbol}     {description}", lambda s=symbol: self._pick(s),
                          hint=f"{value:.6g}")
            return
        for symbol, description in EXTRA_SYMBOLS.get(self.page, []):
            self._row(inner, f"{symbol}     {description}", lambda s=symbol: self._pick(s))
        for name in FUNCTIONS[self.page]:
            self._row(inner, name, lambda n=name: self._pick(n + "("), hint=HINTS.get(name, ""))

    # ---------- actions ----------
    def _pick(self, text):
        self.close()
        self.insert(text)

    def _open(self, group):
        self.page = group
        self._render()

    def _back(self):
        self.page = None
        self._render()

    def _save_variable(self, name):
        error = self.calc.save_variable(name)
        if error:
            self._say(error)
        else:
            self.close()
            self.notify(f"{name} saved")

    def _define_function(self, text):
        error = self.calc.define_function(text)
        if error:
            self._say(error)
        else:
            self.page = None
            self._render()
            self._say("Function saved", error=False)

    def _say(self, message, error=True):
        if self._status is not None:
            self._status.configure(text=message, fg=theme.ERROR if error else theme.DIM)

    # ---------- placement ----------
    def reposition(self):
        """Float above the bottom row, always inside the window."""
        if self.panel is None:
            return
        host, panel = self.host, self.panel
        panel.place_forget()
        host.update_idletasks()
        width = min(WIDTH, host.winfo_width() - 20)
        if self.kind in finance.SPECS:            # forms need their full height: sit at the top
            top = 8
            height = min(panel.natural_height(), host.winfo_height() - 16)
        else:
            bottom = self.anchor.winfo_rooty() - host.winfo_rooty() - 6
            top = max(8, bottom - panel.natural_height())
            height = bottom - top
        x = (host.winfo_width() - width) // 2
        panel.set_corners(self._corner_colors(x, top, width, height))
        panel.place(x=x, y=top, width=width, height=height)
        panel.draw(width, height)
        tk.Misc.lift(panel)          # Canvas.lift() would raise a canvas item instead

    def _corner_colors(self, x, y, w, h):
        def color_at(px, py):
            widget = self.host.winfo_containing(self.host.winfo_rootx() + px,
                                                self.host.winfo_rooty() + py)
            while widget is not None:
                surface = getattr(widget, "surface", None)
                if surface:
                    return surface
                widget = getattr(widget, "master", None)
            return theme.BG
        i = 3
        return (color_at(x + i, y + i), color_at(x + w - i, y + i),
                color_at(x + i, y + h - i), color_at(x + w - i, y + h - i))

    # ---------- small widgets ----------
    def _row(self, parent, text, command, hint="", arrow=False):
        row = tk.Frame(parent, bg=theme.POPOVER, cursor="hand2")
        row.pack(fill="x")
        left = tk.Label(row, text=text, bg=theme.POPOVER, fg=theme.TEXT, anchor="w",
                        font=(theme.FONT, -14), pady=7)
        left.pack(side="left", padx=(10, 6))
        right = tk.Label(row, text="→" if arrow else hint, bg=theme.POPOVER, fg=theme.DIM,
                         anchor="e", font=(theme.FONT, -12))
        right.pack(side="right", padx=(6, 10))
        parts = (row, left, right)
        for part in parts:
            part.bind("<Enter>", lambda e: [p.configure(bg=theme.ROW_HOVER) for p in parts])
            part.bind("<Leave>", lambda e: [p.configure(bg=theme.POPOVER) for p in parts])
            part.bind("<ButtonRelease-1>", lambda e: command())

    def _separator(self, parent):
        tk.Frame(parent, bg=theme.POPOVER_BORDER, height=1).pack(fill="x", padx=6, pady=4)

    def _section(self, parent, text):
        tk.Label(parent, text=text, bg=theme.POPOVER, fg=theme.DIM, anchor="w",
                 font=(theme.FONT, -11)).pack(fill="x", padx=10, pady=(2, 0))

    def _entry_row(self, parent, placeholder, button_text, submit):
        frame = tk.Frame(parent, bg=theme.POPOVER)
        frame.pack(fill="x", padx=4, pady=(4, 0))
        entry = tk.Entry(frame, bg=theme.ENTRY, fg=theme.DIM, insertbackground=theme.TEXT,
                         relief="flat", bd=0, font=(theme.FONT, -14), highlightthickness=1,
                         highlightbackground=theme.POPOVER_BORDER, highlightcolor=theme.EQUALS[0])
        entry.insert(0, placeholder)
        entry.placeholder = True

        def focus_in(_):
            if entry.placeholder:
                entry.delete(0, "end")
                entry.configure(fg=theme.TEXT)
                entry.placeholder = False

        def focus_out(_):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.configure(fg=theme.DIM)
                entry.placeholder = True

        def run(_=None):
            text = "" if entry.placeholder else entry.get().strip()
            if text:
                submit(text)

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)
        entry.bind("<Return>", run)
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(6, 6))
        button = SoftButton(frame, button_text, run, theme.EQUALS, theme.POPOVER,
                            radius=6, width=52, height=32)
        button.pack(side="right", padx=(0, 6))
        self._status = tk.Label(parent, text=" ", bg=theme.POPOVER, fg=theme.DIM, anchor="w",
                                font=(theme.FONT, -12))
        self._status.pack(fill="x", padx=12, pady=(4, 2))

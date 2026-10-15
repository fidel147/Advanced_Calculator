import tkinter as tk

from ui import theme
from ui.widgets import Panel


class ChoiceMenu:
    """A small dropdown list (radio style) that floats inside the window."""

    def __init__(self, host):
        self.host = host
        self.panel = self.anchor = None

    @property
    def is_open(self):
        return self.panel is not None

    def contains(self, widget):
        while widget is not None:
            if widget is self.panel:
                return True
            widget = getattr(widget, "master", None)
        return False

    def open(self, anchor, items, current, on_pick, below=True, center=False):
        """items = [(value, label, hint), ...]. Clicking the same anchor again closes the menu."""
        same = self.is_open and self.anchor is anchor
        self.close()
        if same:
            return
        self.anchor = anchor
        self.panel = Panel(self.host, theme.POPOVER, theme.POPOVER_BORDER)
        for value, label, hint in items:
            self._row(value == current, label, hint, lambda v=value: self._choose(v, on_pick))
        self._place(below, center)

    def close(self):
        if self.panel is not None:
            self.panel.destroy()
        self.panel = self.anchor = None

    def _choose(self, value, on_pick):
        self.close()
        on_pick(value)

    def _place(self, below, center):
        panel, host, anchor = self.panel, self.host, self.anchor
        host.update_idletasks()
        panel.inner.update_idletasks()
        width = max(anchor.winfo_width(), panel.inner.winfo_reqwidth() + 2 * panel.padding)
        width = min(width, host.winfo_width() - 16)
        height = min(panel.natural_height(), host.winfo_height() - 16)
        ax = anchor.winfo_rootx() - host.winfo_rootx()
        ay = anchor.winfo_rooty() - host.winfo_rooty()
        x = ax + (anchor.winfo_width() - width) // 2 if center else ax
        x = max(8, min(x, host.winfo_width() - width - 8))
        y = ay + anchor.winfo_height() + 4 if below else ay - height - 4
        y = max(8, min(y, host.winfo_height() - height - 8))
        panel.set_corners((theme.BG,) * 4)
        panel.place(x=x, y=y, width=width, height=height)
        panel.draw(width, height)
        tk.Misc.lift(panel)          # Canvas.lift() would raise a canvas item instead

    def _row(self, selected, text, hint, command):
        row = tk.Frame(self.panel.inner, bg=theme.POPOVER, cursor="hand2")
        row.pack(fill="x")
        mark = tk.Label(row, text="●" if selected else "○", bg=theme.POPOVER, fg=theme.TEXT,
                        font=(theme.FONT, -13))
        mark.pack(side="left", padx=(10, 4))
        left = tk.Label(row, text=text, bg=theme.POPOVER, fg=theme.TEXT, anchor="w",
                        font=(theme.FONT, -14), pady=7)
        left.pack(side="left", padx=(0, 10))
        right = tk.Label(row, text=hint, bg=theme.POPOVER, fg=theme.DIM, anchor="e",
                         font=(theme.FONT, -12))
        right.pack(side="right", padx=(10, 10))
        parts = (row, mark, left, right)
        for part in parts:
            part.bind("<Enter>", lambda e: [p.configure(bg=theme.ROW_HOVER) for p in parts])
            part.bind("<Leave>", lambda e: [p.configure(bg=theme.POPOVER) for p in parts])
            part.bind("<ButtonRelease-1>", lambda e: command())

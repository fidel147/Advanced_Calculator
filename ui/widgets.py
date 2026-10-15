import tkinter as tk

from PIL import Image, ImageDraw, ImageTk

from ui import theme

SCALE = 4   # draw 4x bigger, then shrink: smooth corners on any Tk


def rounded_image(width, height, radius, fill, corners, border=None):
    """Rounded rectangle. `corners` = colors behind (top-left, top-right, bottom-left, bottom-right)."""
    w, h, r = max(width, 2), max(height, 2), radius
    big = (w * SCALE, h * SCALE)

    def mask(inset):
        m = Image.new("L", big, 0)
        box = (inset * SCALE, inset * SCALE, big[0] - 1 - inset * SCALE, big[1] - 1 - inset * SCALE)
        ImageDraw.Draw(m).rounded_rectangle(box, max(r - inset, 0) * SCALE, fill=255)
        return m.resize((w, h), Image.LANCZOS)

    tl, tr, bl, br = corners
    image = Image.new("RGB", (w, h), tl)
    image.paste(tr, (w - r, 0, w, r))
    image.paste(bl, (0, h - r, r, h))
    image.paste(br, (w - r, h - r, w, h))
    if border:
        image.paste(border, mask=mask(0))
        image.paste(fill, mask=mask(1))
    else:
        image.paste(fill, mask=mask(0))
    return ImageTk.PhotoImage(image)


class SoftButton(tk.Canvas):
    """Button with smooth rounded corners and hover / pressed colors."""

    def __init__(self, parent, text, command, colors, background=theme.BG,
                 text_color=theme.TEXT, radius=8, width=40, height=44, align="center"):
        super().__init__(parent, bd=0, highlightthickness=0, bg=background,
                         width=width, height=height, cursor="hand2")
        self.text, self.command, self.colors = text, command, colors
        self.background, self.text_color, self.radius = background, text_color, radius
        self.align = align            # "center" or "w" (left)
        self.enabled = True
        self.state = 0                # 0 normal, 1 hover, 2 pressed
        self._images, self._size = {}, (0, 0)
        self.bind("<Configure>", self._on_configure)
        self.bind("<Enter>", lambda e: self._set(1))
        self.bind("<Leave>", lambda e: self._set(0))
        self.bind("<ButtonPress-1>", lambda e: self._set(2))
        self.bind("<ButtonRelease-1>", self._release)

    @property
    def surface(self):                # color under a corner of a popup placed over this button
        return self.colors[0]

    def set_text(self, text):
        if text != self.text:
            self.text = text
            self._draw()

    def set_colors(self, colors):
        if colors != self.colors:
            self.colors = colors
            self._images.clear()
            self._draw()

    def set_enabled(self, enabled):
        if enabled != self.enabled:
            self.enabled = enabled
            self.configure(cursor="hand2" if enabled else "arrow")
            self._draw()

    def _set(self, state):
        if state != self.state:
            self.state = state
            self._draw()

    def _release(self, event):
        inside = 0 <= event.x < self.winfo_width() and 0 <= event.y < self.winfo_height()
        self._set(1 if inside else 0)
        if inside and self.enabled and self.command:
            self.command()

    def _on_configure(self, event):
        if (event.width, event.height) != self._size:
            self._size = (event.width, event.height)
            self._images.clear()
        self._draw()

    def _draw(self):
        w, h = self._size
        if w < 6 or h < 6:
            return
        state = self.state if self.enabled else 0
        key = (w, h, state)
        if key not in self._images:
            self._images[key] = rounded_image(
                w, h, self.radius, self.colors[state], (self.background,) * 4)
        self.delete("all")
        self.create_image(0, 0, anchor="nw", image=self._images[key])
        color = self.text_color if self.enabled else theme.DIM
        font = (theme.FONT, -max(11, int(h * 0.38)))
        if self.align == "w":
            self.create_text(12, h / 2, anchor="w", text=self.text, fill=color, font=font)
        else:
            self.create_text(w / 2, h / 2, text=self.text, fill=color, font=font)


class Panel(tk.Canvas):
    """Rounded popup. Put widgets in panel.inner."""

    def __init__(self, parent, fill, border, radius=10, padding=6):
        super().__init__(parent, bd=0, highlightthickness=0, bg=fill)
        self.fill, self.border, self.radius, self.padding = fill, border, radius, padding
        self.corners = (theme.BG,) * 4
        self.inner = tk.Frame(self, bg=fill)
        self._window = self.create_window(padding, padding, window=self.inner, anchor="nw")
        self._image, self._size = None, (0, 0)
        self.bind("<Configure>", lambda e: self.draw(e.width, e.height))

    def natural_height(self):
        self.inner.update_idletasks()
        return self.inner.winfo_reqheight() + 2 * self.padding

    def set_corners(self, corners):
        self.corners = corners
        self._size = (0, 0)           # force a redraw

    def draw(self, w, h):
        if (w, h) == self._size or w < 4 or h < 4:
            return
        self._size = (w, h)
        self._image = rounded_image(w, h, self.radius, self.fill, self.corners, self.border)
        self.delete("bg")
        self.create_image(0, 0, anchor="nw", image=self._image, tags="bg")
        self.tag_lower("bg")
        p = self.padding
        self.itemconfigure(self._window, width=max(w - 2 * p, 1), height=max(h - 2 * p, 1))

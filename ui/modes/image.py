import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from PIL import Image, ImageTk

from engine import image as image_engine
from ui import theme
from ui.widgets import SoftButton


class ImageMode(ctk.CTkFrame):
    """A focused image workspace with real crop and Pillow-based editing."""

    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.image = None
        self.preview = None
        self.photo = None
        self.display_scale = 1.0
        self.display_origin = (0, 0)
        self.selection_start = None
        self.selection_box = None
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        toolbar = tk.Frame(self, bg=theme.HEADER, height=50)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)
        for label, command in (("Open", self.open_image), ("Save as", self.save_image),
                               ("Reset", self.reset_image), ("Crop selection", self.crop_selection)):
            SoftButton(toolbar, label, command, theme.HEADER_BTN, theme.HEADER,
                       width=112, height=34).pack(side="left", padx=(8 if label == "Open" else 2, 2), pady=8)

        workspace = tk.Frame(self, bg=theme.BG)
        workspace.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(workspace, bg="#171717", highlightthickness=1,
                                highlightbackground=theme.POPOVER_BORDER, cursor="crosshair")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<ButtonPress-1>", self._start_selection)
        self.canvas.bind("<B1-Motion>", self._drag_selection)
        self.canvas.bind("<ButtonRelease-1>", self._finish_selection)
        self.canvas.bind("<Configure>", lambda _event: self._render())

        controls = tk.Frame(workspace, bg=theme.HISTORY, width=250)
        controls.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        controls.grid_propagate(False)
        controls.grid_columnconfigure(0, weight=1)
        tk.Label(controls, text="Edit image", bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 12))
        for row, text, command in ((1, "Rotate left", lambda: self._rotate(-90)),
                                   (2, "Rotate right", lambda: self._rotate(90)),
                                   (3, "Flip horizontal", lambda: self._flip("horizontal")),
                                   (4, "Flip vertical", lambda: self._flip("vertical"))):
            SoftButton(controls, text, command, theme.OPERATOR, theme.HISTORY,
                       width=210, height=32).grid(row=row, column=0, sticky="ew", padx=14, pady=3)
        tk.Label(controls, text="Brightness", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=5, column=0, sticky="ew", padx=14, pady=(14, 0))
        self.brightness = tk.DoubleVar(value=1.0)
        tk.Scale(controls, from_=0.1, to=2.0, resolution=0.05, orient="horizontal",
                 variable=self.brightness, command=lambda _value: self._apply_adjustments(),
                 bg=theme.HISTORY, fg=theme.TEXT, troughcolor=theme.INPUT,
                 highlightthickness=0).grid(row=6, column=0, sticky="ew", padx=10)
        tk.Label(controls, text="Contrast", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=7, column=0, sticky="ew", padx=14, pady=(8, 0))
        self.contrast = tk.DoubleVar(value=1.0)
        tk.Scale(controls, from_=0.1, to=2.0, resolution=0.05, orient="horizontal",
                 variable=self.contrast, command=lambda _value: self._apply_adjustments(),
                 bg=theme.HISTORY, fg=theme.TEXT, troughcolor=theme.INPUT,
                 highlightthickness=0).grid(row=8, column=0, sticky="ew", padx=10)
        self.grayscale = tk.BooleanVar()
        tk.Checkbutton(controls, text="Grayscale", variable=self.grayscale,
                       command=self._apply_adjustments, bg=theme.HISTORY, fg=theme.TEXT,
                       selectcolor=theme.INPUT, activebackground=theme.HISTORY,
                       activeforeground=theme.TEXT, anchor="w").grid(row=9, column=0, sticky="ew", padx=10, pady=5)
        tk.Label(controls, text="Resize", bg=theme.HISTORY, fg=theme.DIM,
                 anchor="w", font=(theme.FONT, -11)).grid(row=10, column=0, sticky="ew", padx=14, pady=(12, 0))
        size_bar = tk.Frame(controls, bg=theme.HISTORY)
        size_bar.grid(row=11, column=0, sticky="ew", padx=10, pady=4)
        self.width_entry = tk.Entry(size_bar, bg=theme.INPUT, fg=theme.TEXT, insertbackground=theme.TEXT, width=8)
        self.width_entry.pack(side="left", padx=(0, 4))
        self.height_entry = tk.Entry(size_bar, bg=theme.INPUT, fg=theme.TEXT, insertbackground=theme.TEXT, width=8)
        self.height_entry.pack(side="left", padx=(4, 0))
        SoftButton(controls, "Apply resize", self.resize_image, theme.OPERATOR, theme.HISTORY,
                   width=210, height=32).grid(row=12, column=0, sticky="ew", padx=14, pady=4)
        self.status = tk.Label(controls, text="Open an image, then drag on it to select a crop region.",
                               bg=theme.HISTORY, fg=theme.DIM, anchor="nw", justify="left",
                               wraplength=220, font=(theme.FONT, -10))
        self.status.grid(row=13, column=0, sticky="new", padx=14, pady=12)

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"), ("All files", "*")])
        if not path:
            return
        try:
            self.image = Image.open(path).convert("RGB")
            self._reset_adjustments()
            self._fill_size_entries()
            self._set_status(f"Loaded {self.image.width} x {self.image.height}. Drag to select a crop region.")
            self._render()
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not open image", str(error))

    def save_image(self):
        if self.image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("WebP", "*.webp")])
        if path:
            self.preview.save(path)
            self._set_status(f"Saved edited image to {path}")

    def reset_image(self):
        if self.image is None:
            return
        self._reset_adjustments()
        self._fill_size_entries()
        self.selection_box = None
        self._render()
        self._set_status("Reset edits for the current image")

    def crop_selection(self):
        if self.image is None or self.selection_box is None:
            self._set_status("Drag across the image before choosing Crop selection")
            return
        left, top, right, bottom = self.selection_box
        self.image = image_engine.crop(self.image, (
            left / self.display_scale, top / self.display_scale,
            right / self.display_scale, bottom / self.display_scale))
        self._reset_adjustments()
        self._fill_size_entries()
        self.selection_box = None
        self._render()
        self._set_status(f"Cropped image to {self.image.width} x {self.image.height}")

    def resize_image(self):
        if self.image is None:
            return
        try:
            self.image = image_engine.resize(self.image, self.width_entry.get(), self.height_entry.get())
            self._reset_adjustments()
            self._render()
            self._set_status(f"Resized image to {self.image.width} x {self.image.height}")
        except (TypeError, ValueError) as error:
            messagebox.showerror("Could not resize image", str(error))

    def _rotate(self, angle):
        if self.image is not None:
            self.image = image_engine.rotate(self.image, angle)
            self._reset_adjustments()
            self._fill_size_entries()
            self._render()

    def _flip(self, direction):
        if self.image is not None:
            self.image = image_engine.flip(self.image, direction)
            self._render()

    def _apply_adjustments(self):
        if self.image is not None:
            self.preview = image_engine.adjust(self.image, self.brightness.get(), self.contrast.get(), self.grayscale.get())
            self._render_preview()

    def _reset_adjustments(self):
        self.brightness.set(1.0)
        self.contrast.set(1.0)
        self.grayscale.set(False)
        self.preview = self.image.copy() if self.image is not None else None

    def _fill_size_entries(self):
        if self.image is None:
            return
        for entry, value in ((self.width_entry, self.image.width), (self.height_entry, self.image.height)):
            entry.delete(0, "end")
            entry.insert(0, str(value))

    def _render(self):
        if self.preview is None:
            self.canvas.delete("all")
            return
        self._render_preview()

    def _render_preview(self):
        if self.preview is None:
            return
        self.canvas.delete("all")
        available_width = max(self.canvas.winfo_width() - 20, 200)
        available_height = max(self.canvas.winfo_height() - 20, 200)
        self.display_scale = min(available_width / self.preview.width, available_height / self.preview.height, 1.0)
        display = self.preview.resize((max(1, int(self.preview.width * self.display_scale)),
                                       max(1, int(self.preview.height * self.display_scale))), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(display)
        origin_x = (self.canvas.winfo_width() - display.width) // 2
        origin_y = (self.canvas.winfo_height() - display.height) // 2
        self.display_origin = (origin_x, origin_y)
        self.canvas.create_image(origin_x, origin_y, image=self.photo, anchor="nw", tags="image")
        if self.selection_box is not None:
            left, top, right, bottom = self.selection_box
            self.canvas.create_rectangle(origin_x + left, origin_y + top, origin_x + right, origin_y + bottom,
                                         outline="#d8a84e", width=2, dash=(6, 3), tags="selection")

    def _start_selection(self, event):
        if self.preview is None:
            return
        origin_x, origin_y = self.display_origin
        self.selection_start = (event.x - origin_x, event.y - origin_y)
        self.selection_box = (*self.selection_start, *self.selection_start)
        self._render_preview()

    def _drag_selection(self, event):
        if self.selection_start is None:
            return
        start_x, start_y = self.selection_start
        self.selection_box = (min(start_x, event.x - self.display_origin[0]),
                              min(start_y, event.y - self.display_origin[1]),
                              max(start_x, event.x - self.display_origin[0]),
                              max(start_y, event.y - self.display_origin[1]))
        self._render_preview()

    def _finish_selection(self, _event):
        self.selection_start = None

    def _set_status(self, text):
        self.status.configure(text=text)

    def on_show(self):
        self.canvas.focus_set()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def handle_key(self, event):
        if event.keysym == "Escape":
            self.selection_box = None
            self._render_preview()

    def handle_click(self, _event):
        pass

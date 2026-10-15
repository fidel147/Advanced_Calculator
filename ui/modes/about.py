import threading
import tkinter as tk
import webbrowser
from datetime import datetime, timezone
from io import BytesIO
from urllib.request import Request, urlopen

import customtkinter as ctk
from PIL import Image, ImageTk, UnidentifiedImageError

from ui import theme
from ui.widgets import SoftButton


GITHUB = "https://github.com/fidel147"
LINKS = (
    ("GitHub", GITHUB),
)
BIOGRAPHY = (
    "Fidèle Togbédji ZOGBE is a computer engineering student and Python developer "
    "based in Benin, with interests in artificial intelligence, data science, "
    "software engineering, and scientific computing.\n\n"
    "His technical interests include object-oriented programming, web development, "
    "machine learning, and building practical digital applications. He has also "
    "learned HTML, CSS, C++, C, and cybersecurity fundamentals.\n\n"
    "Through projects involving Python programming, data analysis, game development, "
    "and web platform design, he explores ways to transform technical knowledge into "
    "useful software.\n\n"
    "He created this scientific calculator with the vision of bringing mathematical "
    "computation, data analysis, scientific visualization, and other essential tools "
    "together in one accessible platform.\n\n"
    "His goal is to continue learning, experimenting, and developing technology that "
    "supports students, researchers, and everyday users."
)
PROJECTS = (
    ("Club_Financial", "Python data analysis of football-club financial data and relationships between variables.", "Public repository"),
    ("Space-Shooter", "Public Python project related to game development.", "Public repository"),
    ("5games", "Fork of a Python game-development learning repository.", "Fork"),
    ("Fidele-ZOGBE", "Public repository associated with the GitHub identity; no further description is inferred here.", "Public repository"),
    ("introduction-to-github", "GitHub Education learning repository and template fork.", "Learning repository / fork"),
    ("skills-introduction-to-github", "Repository associated with learning GitHub workflows.", "Learning repository"),
)


class AboutMode(ctk.CTkFrame):
    """Verified creator profile and application credits."""

    supports_undo = False

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.avatar = None
        self.avatar_photo = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()
        self.after(100, self._load_avatar)

    def _build(self):
        canvas = tk.Canvas(self, bg=theme.BG, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_columnconfigure(1, weight=0)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda _event: self._layout(canvas))
        canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-int(event.delta / 120), "units"))
        canvas.bind("<Button-4>", lambda _event: canvas.yview_scroll(-3, "units"))
        canvas.bind("<Button-5>", lambda _event: canvas.yview_scroll(3, "units"))
        self.content = tk.Frame(canvas, bg=theme.BG)
        self.window = canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        self._canvas = canvas

        self.hero = tk.Frame(self.content, bg=theme.HISTORY)
        self.hero.pack(fill="x", padx=20, pady=20)
        self.avatar_label = tk.Label(self.hero, text="FZ", bg=theme.EQUALS[0], fg=theme.TEXT,
                                     width=8, height=4, font=(theme.FONT, -22, "bold"))
        self.avatar_label.pack(side="left", padx=20, pady=20)
        identity = tk.Frame(self.hero, bg=theme.HISTORY)
        identity.pack(side="left", fill="both", expand=True, pady=20)
        tk.Label(identity, text="Fidèle Togbédji ZOGBE", bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -22, "bold"), anchor="w").pack(anchor="w")
        tk.Label(identity, text="Computer Engineering Student | Python Developer | Benin",
                 bg=theme.HISTORY, fg=theme.DIM, font=(theme.FONT, -12), anchor="w").pack(anchor="w", pady=(5, 12))
        SoftButton(identity, "Open GitHub profile", lambda: webbrowser.open(GITHUB),
                   theme.EQUALS, theme.HISTORY, width=170, height=34).pack(anchor="w")

        self._section("About the creator", BIOGRAPHY)
        interests = ("Python\nHTML and CSS\nC and C++\nCybersecurity fundamentals\nData Science\n"
                 "Artificial Intelligence\nMachine Learning\nWeb Development\nScientific Computing\n"
                 "Software Engineering\nMathematical Computing\nEducational Technology")
        self._section("Technical interests", interests)
        projects = tk.Frame(self.content, bg=theme.BG)
        projects.pack(fill="x", padx=20, pady=(8, 10))
        tk.Label(projects, text="Public projects and concepts", bg=theme.BG, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold"), anchor="w").pack(anchor="w", pady=(0, 8))
        for name, description, status in PROJECTS:
            card = tk.Frame(projects, bg=theme.HISTORY)
            card.pack(fill="x", pady=3)
            tk.Label(card, text=name, bg=theme.HISTORY, fg=theme.TEXT,
                     font=(theme.FONT, -12, "bold"), anchor="w").pack(side="left", padx=12, pady=10)
            tk.Label(card, text=f"{description} [{status}]", bg=theme.HISTORY, fg=theme.DIM,
                     anchor="w", justify="left", wraplength=620).pack(side="left", fill="x", expand=True, padx=8, pady=10)
        links = tk.Frame(self.content, bg=theme.BG)
        links.pack(fill="x", padx=20, pady=8)
        tk.Label(links, text="Connect", bg=theme.BG, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold"), anchor="w").pack(anchor="w")
        for label, url in LINKS:
            SoftButton(links, label, lambda target=url: webbrowser.open(target),
                       theme.OPERATOR, theme.BG, width=120, height=32).pack(side="left", padx=(0, 6), pady=8)
        footer = tk.Label(self.content, text=f"© {datetime.now(timezone.utc).year} Fidèle Togbédji ZOGBE | Calculator development build",
                          bg=theme.BG, fg=theme.DIM, font=(theme.FONT, -10))
        footer.pack(pady=(8, 20))

    def _section(self, title, text):
        section = tk.Frame(self.content, bg=theme.BG)
        section.pack(fill="x", padx=20, pady=8)
        tk.Label(section, text=title, bg=theme.BG, fg=theme.TEXT,
                 font=(theme.FONT, -16, "bold"), anchor="w").pack(anchor="w", pady=(0, 5))
        tk.Label(section, text=text, bg=theme.HISTORY, fg=theme.TEXT,
                 justify="left", anchor="nw", wraplength=760, padx=14, pady=12).pack(fill="x")

    def _layout(self, canvas):
        canvas.itemconfigure(self.window, width=max(canvas.winfo_width(), 760))

    def _load_avatar(self):
        def fetch():
            try:
                request = Request("https://github.com/fidel147.png?size=256", headers={"User-Agent": "AdvancedCal"})
                with urlopen(request, timeout=3) as response:
                    image = Image.open(BytesIO(response.read())).convert("RGB")
                    image.thumbnail((96, 96))
                try:
                    self.after(0, lambda: self._set_avatar(image))
                except tk.TclError:
                    return
            except (OSError, ValueError, UnidentifiedImageError):
                return
        threading.Thread(target=fetch, daemon=True).start()

    def _set_avatar(self, image):
        self.avatar = image
        self.avatar_photo = ImageTk.PhotoImage(image)
        self.avatar_label.configure(image=self.avatar_photo, text="", width=96, height=96)

    def on_show(self):
        self._canvas.focus_set()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def handle_key(self, _event):
        pass

    def handle_click(self, _event):
        pass

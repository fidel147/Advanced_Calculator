import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg", force=True)
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from engine import data, statistics
from ui import theme
from ui.widgets import SoftButton


class DataMode(ctk.CTkFrame):
    """A compact data workbench for inspection, cleaning, plotting, and export."""

    supports_undo = True

    def __init__(self, parent, app=None):
        super().__init__(parent, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.frame = None
        self.original_frame = None
        self.source_path = ""
        self.last_model_metrics = None
        self._undo = []
        self._redo = []
        self.filtered_frame = None
        self._build()

    def _build(self):
        self._configure_styles()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        toolbar = tk.Frame(self, bg=theme.HEADER, height=48)
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.grid_propagate(False)
        for label, command in (
            ("Open CSV", self.open_csv),
            ("Export CSV", self.export_csv),
            ("Export Report", self.export_report),
            ("Export HTML", self.export_html),
            ("Save Plot", self.save_plot),
        ):
            SoftButton(toolbar, label, command, theme.HEADER_BTN, theme.HEADER,
                       width=105, height=32).pack(side="left", padx=(8 if label == "Open CSV" else 2, 2), pady=8)

        body = tk.Frame(self, bg=theme.BG)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        body.grid_columnconfigure(0, weight=0, minsize=280)
        body.grid_columnconfigure(1, weight=1, minsize=680)
        body.grid_rowconfigure(1, weight=3)
        body.grid_rowconfigure(3, weight=2, minsize=250)

        self.status = tk.Label(body, text="Open a dataset to begin", anchor="w",
                               bg=theme.HISTORY, fg=theme.TEXT, padx=10, pady=8,
                               font=(theme.FONT, -13))
        self.status.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        controls = tk.Frame(body, bg=theme.BG)
        controls.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        controls.configure(width=280)
        controls.grid_propagate(False)
        controls.grid_columnconfigure(0, weight=1)
        self._label(controls, "Analysis", 0)
        self.analysis = ttk.Combobox(controls, style="Data.TCombobox", state="readonly",
                         values=("Summary", "Profile", "Describe", "Numeric statistics", "Automated EDA", "Value counts", "Group by", "One-sample t-test",
                             "Normality (Shapiro-Wilk)", "Correlation significance", "Independent t-test", "Mean",
                             "Heatmap", "Histogram", "Boxplot", "Scatter", "Line"))
        self.analysis.current(0)
        self.analysis.grid(row=1, column=0, sticky="ew", pady=(2, 8))
        self.analysis.bind("<<ComboboxSelected>>", lambda _event: self._refresh_plot())
        self._label(controls, "X column", 2)
        self.x_column = ttk.Combobox(controls, style="Data.TCombobox", state="readonly")
        self.x_column.grid(row=3, column=0, sticky="ew", pady=(2, 6))
        self._label(controls, "Y column", 4)
        self.y_column = ttk.Combobox(controls, style="Data.TCombobox", state="readonly")
        self.y_column.grid(row=5, column=0, sticky="ew", pady=(2, 8))
        SoftButton(controls, "Render selected view", self._refresh_plot, theme.EQUALS, theme.BG,
                   width=140, height=36).grid(row=6, column=0, sticky="ew", pady=(0, 12))
        self._label(controls, "Clean data", 7)
        self.drop_missing = tk.BooleanVar()
        self.fill_numeric = tk.BooleanVar()
        self.drop_duplicates = tk.BooleanVar()
        self.fill_categorical = tk.BooleanVar()
        self.strip_text = tk.BooleanVar()
        for row, text, variable in (
            (8, "Drop missing rows", self.drop_missing),
            (9, "Fill numeric with median", self.fill_numeric),
            (10, "Drop duplicate rows", self.drop_duplicates),
            (11, "Fill categories with mode", self.fill_categorical),
            (12, "Trim text whitespace", self.strip_text),
        ):
            tk.Checkbutton(controls, text=text, variable=variable, command=self.clean,
                           bg=theme.BG, fg=theme.TEXT, selectcolor=theme.HISTORY,
                           activebackground=theme.BG, activeforeground=theme.TEXT,
                           anchor="w").grid(row=row, column=0, sticky="ew")
            self._build_advanced_controls(controls) if row == 12 else None

        table_box = tk.Frame(body, bg=theme.BG)
        table_box.grid(row=1, column=1, sticky="nsew")
        table_box.grid_columnconfigure(0, weight=1)
        table_box.grid_rowconfigure(1, weight=1)
        search_bar = tk.Frame(table_box, bg=theme.BG)
        search_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        search_bar.grid_columnconfigure(0, weight=1)
        self.search_entry = tk.Entry(search_bar, bg=theme.INPUT, fg=theme.TEXT,
                         insertbackground=theme.TEXT, relief="flat", bd=0,
                         font=(theme.FONT, -11))
        self.search_entry.grid(row=0, column=0, sticky="ew", ipady=5)
        self.search_entry.bind("<Return>", lambda _event: self.search_rows())
        SoftButton(search_bar, "Search", self.search_rows, theme.OPERATOR, theme.BG,
               width=80, height=30).grid(row=0, column=1, padx=(5, 2))
        SoftButton(search_bar, "Clear", self.clear_search, theme.FLAT, theme.BG,
               width=70, height=30).grid(row=0, column=2, padx=(2, 0))
        self.table = ttk.Treeview(table_box, style="Data.Treeview", show="headings")
        self.table.bind("<Double-Button-1>", self._edit_cell)
        y_scroll = ttk.Scrollbar(table_box, orient="vertical", command=self.table.yview)
        x_scroll = ttk.Scrollbar(table_box, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.table.grid(row=1, column=0, sticky="nsew")
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll.grid(row=2, column=0, sticky="ew")

        self.figure_box = tk.Frame(body, bg=theme.HISTORY)
        self.figure_box.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.figure_box.grid_columnconfigure(0, weight=1)
        self.figure_box.grid_rowconfigure(0, weight=1)
        self.figure = None
        self.canvas = None
        self.result_box = None

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Data.TCombobox", fieldbackground=theme.INPUT, background=theme.INPUT,
                        foreground=theme.TEXT, arrowcolor=theme.TEXT, bordercolor=theme.POPOVER_BORDER,
                        lightcolor=theme.POPOVER_BORDER, darkcolor=theme.POPOVER_BORDER,
                        padding=5, font=(theme.FONT, -11))
        style.map("Data.TCombobox", fieldbackground=[("readonly", theme.INPUT)],
                  foreground=[("readonly", theme.TEXT)])
        style.configure("Data.Treeview", background=theme.INPUT, fieldbackground=theme.INPUT,
                        foreground=theme.TEXT, rowheight=27, borderwidth=0,
                        font=(theme.FONT, -10))
        style.configure("Data.Treeview.Heading", background=theme.POPOVER,
                        foreground=theme.TEXT, relief="flat", padding=6,
                        font=(theme.FONT, -10, "bold"))
        style.map("Data.Treeview", background=[("selected", theme.EQUALS[0])],
                  foreground=[("selected", theme.TEXT)])

    @staticmethod
    def _label(parent, text, row):
        tk.Label(parent, text=text, bg=theme.BG, fg=theme.DIM, anchor="w",
                 font=(theme.FONT, -11)).grid(row=row, column=0, sticky="ew")

    def _build_advanced_controls(self, controls):
        self._label(controls, "Feature engineering", 14)
        self.transform = ttk.Combobox(controls, style="Data.TCombobox", state="readonly",
                                      values=("Normalize numeric", "Standardize numeric",
                                              "One-hot encode categories", "Remove numeric outliers"))
        self.transform.current(0)
        self.transform.grid(row=15, column=0, sticky="ew", pady=(2, 4))
        transform_bar = tk.Frame(controls, bg=theme.BG)
        transform_bar.grid(row=16, column=0, sticky="ew", pady=(0, 10))
        transform_bar.grid_columnconfigure(0, weight=1)
        transform_bar.grid_columnconfigure(1, weight=1)
        SoftButton(transform_bar, "Apply", self.apply_transform, theme.OPERATOR, theme.BG,
                   width=70, height=32).grid(row=0, column=0, sticky="ew", padx=(0, 2))
        SoftButton(transform_bar, "Reset", self.reset_data, theme.FLAT, theme.BG,
                   width=70, height=32).grid(row=0, column=1, sticky="ew", padx=(2, 0))
        self._label(controls, "Baseline model", 17)
        self.target_column = ttk.Combobox(controls, style="Data.TCombobox", state="readonly")
        self.target_column.grid(row=18, column=0, sticky="ew", pady=(2, 4))
        self.model = ttk.Combobox(controls, style="Data.TCombobox", state="readonly",
                                  values=("Linear regression", "Random forest", "Logistic regression",
                                          "Random forest classifier"))
        self.model.current(1)
        self.model.grid(row=19, column=0, sticky="ew", pady=(0, 5))
        SoftButton(controls, "Train / Evaluate", self.train_model, theme.EQUALS, theme.BG,
                   width=140, height=34).grid(row=20, column=0, sticky="ew")
        self.metrics = tk.Label(controls, text="", bg=theme.BG, fg=theme.DIM, anchor="nw",
                                justify="left", wraplength=220, font=(theme.FONT, -10))
        self.metrics.grid(row=21, column=0, sticky="new", pady=(7, 0))

    def _set_status(self, text):
        self.status.configure(text=text)

    def open_csv(self):
        path = filedialog.askopenfilename(filetypes=[
            ("Data tables", "*.csv *.tsv *.txt *.xlsx *.xls *.json *.parquet"),
            ("All files", "*"),
        ])
        if not path:
            return
        try:
            self.frame = data.read_table(path)
            self.original_frame = self.frame.copy()
            self.source_path = path
            self.last_model_metrics = None
            self._update_columns()
            numeric_count = len(self.frame.select_dtypes(include="number").columns)
            self.analysis.set("Scatter" if numeric_count >= 2 else
                              "Histogram" if numeric_count == 1 else "Profile")
            self._refresh_table()
            self._set_status(f"{path}  |  {len(self.frame):,} rows x {len(self.frame.columns)} columns")
            self._refresh_plot()
        except (OSError, ValueError, pd.errors.ParserError) as error:
            messagebox.showerror("Could not open table", str(error))

    def clean(self):
        if self.frame is None:
            return
        before = self.frame.copy()
        self.frame = data.clean_table(
            self.frame, self.drop_missing.get(), self.fill_numeric.get(), self.drop_duplicates.get(),
            self.fill_categorical.get(), self.strip_text.get())
        self._record_change(before)
        self.filtered_frame = None
        self._update_columns()
        self._refresh_table()
        self._set_status(f"Cleaned table  |  {len(self.frame):,} rows x {len(self.frame.columns)} columns")
        self._refresh_plot()

    def apply_transform(self):
        if self.frame is None:
            return
        try:
            before = self.frame.copy()
            self.frame = data.transform_table(self.frame, self.transform.get())
            self._record_change(before)
            self.filtered_frame = None
            self._update_columns()
            self._refresh_table()
            self._set_status(f"Applied {self.transform.get()}  |  {len(self.frame):,} rows x {len(self.frame.columns)} columns")
            self._refresh_plot()
        except ValueError as error:
            messagebox.showerror("Could not transform data", str(error))

    def reset_data(self):
        if self.original_frame is None:
            return
        self.frame = self.original_frame.copy()
        self.filtered_frame = None
        self._update_columns()
        self._refresh_table()
        self._set_status("Reset to the original loaded table")
        self._refresh_plot()

    def train_model(self):
        if self.frame is None:
            return
        try:
            result = data.train_baseline(self.frame, self.target_column.get(), self.model.get())
            self.last_model_metrics = result["metrics"]
            lines = [f"{name}: {value:.4g}" for name, value in result["metrics"].items()
                     if name != "feature_importance"]
            importance = result["metrics"].get("feature_importance", {})
            if importance:
                lines.append("Top features:")
                lines.extend(f"  {name}: {value:.4g}" for name, value in list(importance.items())[:5])
            self.metrics.configure(text="\n".join(lines), fg=theme.TEXT)
            self._set_status(f"{self.model.get()} evaluated on {self.target_column.get()}")
        except (TypeError, ValueError) as error:
            self.metrics.configure(text=str(error), fg=theme.ERROR)

    def _update_columns(self):
        columns = [str(column) for column in self.frame.columns] if self.frame is not None else []
        numeric = [str(column) for column in self.frame.select_dtypes(include="number").columns] if self.frame is not None else []
        self.x_column["values"] = columns
        self.y_column["values"] = columns
        self.target_column["values"] = columns
        if columns:
            self.x_column.set((numeric or columns)[0])
            self.y_column.set((numeric or columns)[-1])
            self.target_column.set(columns[-1])

    def _clear_table(self):
        self.table.delete(*self.table.get_children())
        self.table["columns"] = ()

    def _refresh_table(self):
        self._clear_table()
        if self.frame is None:
            return
        columns = [str(column) for column in self.frame.columns]
        self.table["columns"] = columns
        for column in columns:
            self.table.heading(column, text=column)
            self.table.column(column, width=120, minwidth=70, stretch=False)
        view = self.filtered_frame if self.filtered_frame is not None else self.frame
        for index, values in view.head(500).iterrows():
            self.table.insert("", "end", iid=str(index), values=tuple(str(value)[:80] for value in values))

    def search_rows(self):
        if self.frame is None:
            return
        self.filtered_frame = data.search_rows(self.frame, self.search_entry.get())
        self._refresh_table()
        self._set_status(f"Showing {len(self.filtered_frame):,} matching rows of {len(self.frame):,}")

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.filtered_frame = None
        self._refresh_table()
        if self.frame is not None:
            self._set_status(f"Showing {len(self.frame):,} rows")

    def _edit_cell(self, event):
        if self.frame is None:
            return
        row_id = self.table.identify_row(event.y)
        column_id = self.table.identify_column(event.x)
        if not row_id or not column_id:
            return
        column_index = int(column_id[1:]) - 1
        column = self.frame.columns[column_index]
        row_index = int(row_id)
        bbox = self.table.bbox(row_id, column_id)
        if not bbox:
            return
        editor = tk.Entry(self.table, bg=theme.INPUT, fg=theme.TEXT,
                          insertbackground=theme.TEXT, relief="solid", bd=1)
        editor.insert(0, str(self.frame.loc[row_index, column]))
        editor.select_range(0, "end")
        editor.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        editor.focus_set()

        def commit(_event=None):
            if not editor.winfo_exists():
                return
            before = self.frame.copy()
            try:
                self.frame.loc[row_index, column] = self._coerce_value(editor.get(), self.frame[column])
            except (TypeError, ValueError) as error:
                self._set_status(f"Cell error: {error}")
            else:
                self._record_change(before)
                self._refresh_table()
                self._set_status(f"Edited {column} at row {row_index}")
            editor.destroy()

        editor.bind("<Return>", commit)
        editor.bind("<FocusOut>", commit)

    @staticmethod
    def _coerce_value(value, series):
        if value.strip() == "":
            return pd.NA
        if pd.api.types.is_numeric_dtype(series):
            return pd.to_numeric(value)
        if pd.api.types.is_bool_dtype(series):
            lowered = value.strip().lower()
            if lowered not in ("true", "false"):
                raise ValueError("Boolean values must be true or false")
            return lowered == "true"
        return value

    def _record_change(self, before):
        self._undo.append(before)
        del self._undo[:-50]
        self._redo.clear()

    def undo(self):
        if self._undo:
            self._redo.append(self.frame.copy())
            self.frame = self._undo.pop()
            self.filtered_frame = None
            self._refresh_table()
            self._set_status("Undid the last dataset change")

    def redo(self):
        if self._redo:
            self._undo.append(self.frame.copy())
            self.frame = self._redo.pop()
            self.filtered_frame = None
            self._refresh_table()
            self._set_status("Redid the dataset change")

    def _clear_output(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure is not None:
            plt.close(self.figure)
            self.figure = None
        if self.result_box is not None:
            self.result_box.destroy()
            self.result_box = None

    def _show_result_table(self, result, title):
        self.result_box = tk.Frame(self.figure_box, bg=theme.HISTORY)
        self.result_box.grid(row=0, column=0, sticky="nsew")
        self.result_box.grid_columnconfigure(0, weight=1)
        self.result_box.grid_rowconfigure(1, weight=1)
        tk.Label(self.result_box, text=title, bg=theme.HISTORY, fg=theme.TEXT,
                 font=(theme.FONT, -16), anchor="w").grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        table_frame = tk.Frame(self.result_box, bg=theme.HISTORY)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        result_tree = ttk.Treeview(table_frame, style="Data.Treeview", show="headings")
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=result_tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=result_tree.xview)
        result_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        result_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        columns = [str(column) for column in result.columns]
        result_tree["columns"] = columns
        for column in columns:
            result_tree.heading(column, text=column)
            result_tree.column(column, width=145, minwidth=90, stretch=False)
        for values in result.head(500).itertuples(index=False, name=None):
            result_tree.insert("", "end", values=tuple(str(value)[:60] for value in values))
        self._set_status(f"{title}  |  {len(result):,} result rows")

    def _refresh_plot(self):
        self._clear_output()
        mode = self.analysis.get()
        if self.frame is not None:
            try:
                if mode == "Describe":
                    self._show_result_table(data.describe_frame(self.frame), "Dataframe describe()")
                    return
                if mode == "Numeric statistics":
                    self._show_result_table(data.descriptive_statistics(self.frame), "Numeric descriptive statistics")
                    return
                if mode == "Automated EDA":
                    report = data.automated_eda(self.frame, self.source_path)
                    summary = report["summary"]
                    result = pd.DataFrame([{"metric": key, "value": value} for key, value in summary.items()
                                           if key not in ("column_types", "constant_columns")])
                    self._show_result_table(result, "Automated exploratory data analysis")
                    return
                if mode == "Value counts":
                    column = self.y_column.get()
                    self._show_result_table(data.value_counts(self.frame, column), f"Value counts: {column}")
                    return
                if mode == "Group by":
                    group_column = self.x_column.get()
                    value_column = self.y_column.get()
                    result = data.group_summary(self.frame, group_column, value_column, "count")
                    self._show_result_table(result, f"Group counts: {group_column}")
                    return
                if mode in ("One-sample t-test", "Normality (Shapiro-Wilk)",
                            "Correlation significance", "Independent t-test"):
                    value_column = self.y_column.get()
                    group_column = self.x_column.get()
                    if mode == "Independent t-test":
                        categorical = [str(column) for column in self.frame.columns
                                       if not pd.api.types.is_numeric_dtype(self.frame[column])]
                        if categorical:
                            group_column = categorical[0]
                    elif mode == "Correlation significance":
                        numeric = [str(column) for column in self.frame.select_dtypes(include="number").columns]
                        if len(numeric) >= 2:
                            value_column, group_column = numeric[:2]
                    result = statistics.run_test(self.frame, mode, value_column, group_column)
                    self._show_result_table(result, mode)
                    return
            except (KeyError, TypeError, ValueError) as error:
                self._set_status(f"Analysis error: {error}")
                return
        self.figure = plt.Figure(figsize=(8, 3.2), dpi=100, facecolor="#474747")
        axis = self.figure.add_subplot(111)
        axis.set_facecolor("#474747")
        try:
            sns.set_theme(style="darkgrid")
            if self.frame is not None:
                if mode == "Summary":
                    axis.axis("off")
                    summary = data.describe_table(self.frame, self.source_path)
                    axis.text(0.02, 0.85, json.dumps(summary, indent=2), color="white", va="top", family="monospace")
                elif mode == "Profile":
                    axis.axis("off")
                    profile = data.profile_table(self.frame)
                    axis.text(0.02, 0.98, json.dumps(profile, indent=2), color="white", va="top", family="monospace")
                elif mode == "Mean":
                    means = self.frame.select_dtypes(include="number").mean().sort_values()
                    means.plot.barh(ax=axis, color="#d8a84e")
                    axis.set_title("Column means", color="white")
                elif mode == "Heatmap":
                    numeric = self.frame.select_dtypes(include="number")
                    if numeric.shape[1] < 2:
                        raise ValueError("Heatmap needs at least two numeric columns")
                    sns.heatmap(numeric.corr(), annot=True, cmap="mako", ax=axis, cbar=False)
                    axis.set_title("Correlation heatmap", color="white")
                elif mode == "Histogram":
                    self.frame[self.y_column.get()].dropna().plot.hist(ax=axis, bins=24, color="#d8a84e")
                    axis.set_title(f"Distribution of {self.y_column.get()}", color="white")
                elif mode == "Scatter":
                    axis.scatter(self.frame[self.x_column.get()], self.frame[self.y_column.get()], color="#d8a84e", alpha=0.75)
                    axis.set_xlabel(self.x_column.get(), color="white")
                    axis.set_ylabel(self.y_column.get(), color="white")
                    axis.set_title("Scatter plot", color="white")
                elif mode == "Boxplot":
                    numeric = self.frame.select_dtypes(include="number")
                    if numeric.empty:
                        raise ValueError("Boxplot needs numeric columns")
                    sns.boxplot(data=numeric, ax=axis, color="#d8a84e")
                    axis.tick_params(axis="x", rotation=35)
                    axis.set_title("Numeric distributions and outliers", color="white")
                elif mode == "Line":
                    values = pd.to_numeric(self.frame[self.y_column.get()], errors="coerce")
                    axis.plot(values.index, values, color="#d8a84e")
                    axis.set_title(f"{self.y_column.get()} over rows", color="white")
            else:
                axis.text(0.5, 0.5, "Open a CSV or image", color="white", ha="center", va="center")
            axis.tick_params(colors="white")
            for spine in axis.spines.values():
                spine.set_color("#888888")
            if mode not in ("Summary", "Profile", "Describe", "Value counts", "Group by"):
                self.figure.tight_layout()
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_box)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        except (KeyError, TypeError, ValueError, RuntimeError, ImportError) as error:
            axis.axis("off")
            axis.text(0.02, 0.85, str(error), color="#f0a040", va="top")
            self._set_status(f"Plot error: {error}")
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_box)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    def export_csv(self):
        if self.frame is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            self.frame.to_csv(path, index=False)
            self._set_status(f"Exported cleaned table to {path}")

    def save_plot(self):
        if self.figure is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png"), ("PDF", "*.pdf")])
        if path:
            self.figure.savefig(path, facecolor=self.figure.get_facecolor(), bbox_inches="tight")
            self._set_status(f"Saved plot to {path}")

    def export_report(self):
        if self.frame is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON report", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as report_file:
                report = data.describe_table(self.frame, self.source_path)
                if self.last_model_metrics:
                    report["model_metrics"] = self.last_model_metrics
                json.dump(report, report_file, indent=2)
            self._set_status(f"Exported data report to {path}")

    def export_html(self):
        if self.frame is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML report", "*.html")])
        if path:
            with open(path, "w", encoding="utf-8") as report_file:
                report_file.write(data.html_report(self.frame, self.source_path))
            self._set_status(f"Exported HTML EDA report to {path}")

    def on_show(self):
        self._refresh_plot()

    def close_popups(self):
        if self.app:
            self.app.menu.close()

    def handle_key(self, _event):
        pass

    def handle_click(self, _event):
        pass
# AdvancedCal Scientific Platform Roadmap

## Existing architecture audit

- Framework: Python desktop application using Tkinter and customtkinter.
- Entry point: `main.py` creates `CalculatorApp`.
- UI routing: `ui/app.py` lazy-loads modes from one registry and shares an `engine.evaluator.Evaluator`.
- Mathematical engine: `engine/evaluator.py` uses AST parsing and never calls unrestricted `eval`; `engine/basic.py` provides expression editing and undo/redo.
- Existing modes: Basic, Advanced, Financial, Programming, Keyboard, Conversion, and Data Lab.
- Data Lab: pandas import/cleaning, dataframe preview, profiling, describe/value-count/group analysis, Matplotlib/Seaborn plots, image pixel visualization, baseline scikit-learn models, and CSV/JSON/plot export.
- Existing strengths to preserve: calculator state sharing, keyboard shortcuts, mode lazy-loading, safe expression evaluation, undo/redo, financial forms, programming bit grid, and unit conversion.
- Tests before this roadmap: no test files were present.

## Main gaps against the platform specification

1. Symbolic algebra, calculus, equation solving, matrices, and numerical methods are not exposed through the UI.
2. Data Lab needs richer statistical tests, time series, spreadsheet editing, joins, pivot tables, and report generation.
3. Visualization is embedded Matplotlib rather than a full chart workspace with 3D and interactive exports.
4. Image support currently provides pixel-intensity viewing only; there is no non-destructive editor or scientific image-processing pipeline.
5. Machine learning currently has two regression and two classification baselines; clustering, cross-validation, model persistence, and predictions are pending.
6. There is no notebook, project persistence, preferences, collaboration, OCR, AI integration, or automated test suite.
7. File format support is currently CSV-like text and common raster images; XLSX, JSON, Parquet, SQL, PDF, and safe code execution are pending.

## Modular architecture direction

Keep the current mode registry and add independently lazy-loaded workspaces. Put deterministic computation in `engine/` services and keep Tk widgets in `ui/modes/`. Add shared result-table, error, export, and project-state helpers only when at least two modes need them. Do not replace the existing calculator evaluator.

## Prioritized implementation roadmap

1. Scientific foundation: symbolic math, matrices, calculus, numerical methods, and tests. Symbolic math, matrices, numerical methods, number theory, and reciprocal trigonometry are now implemented and tested.
2. Data Science Studio: richer descriptive/inferential statistics, spreadsheet editing, joins, pivots, EDA reports, and time series. Multi-format import, dataset quality metadata and score, editable/searchable tables with undo/redo, numeric descriptive statistics, describe/value counts/group summaries, cleaning controls, inferential tests, automated EDA, and HTML export are now implemented and tested.
3. Visualization Studio: function plotting, chart configuration, 3D plots, and export controls.
4. Scientific Image Processing: RGB/HSV inspection, histograms, filters, edges, segmentation, FFT, measurements, and OCR interfaces. A functional Image Studio foundation now owns image import, crop, resize, rotate, flips, brightness, contrast, grayscale, reset, and export; Data Lab is intentionally dataset-only.
5. Machine Learning Laboratory: preprocessing pipelines, clustering, PCA, cross-validation, predictions, experiment metadata, and safe model persistence.
6. Image Studio: layered non-destructive editing, masks, crop/resize, color adjustments, frames, undo/redo, and export.
7. Probability, physics, chemistry, notebooks, documents, productivity, projects, settings, accessibility, and performance hardening.

## Creator and credits

The verified creator profile is available in the About workspace and identifies Fidèle Togbédji ZOGBE, GitHub `fidel147`, as a computer engineering student and Python developer from Benin. The About workspace is intentionally limited to the supplied GitHub profile, GitHub-associated public repositories, attribution, and the GitHub avatar fallback.

## Dependencies

Already available in the selected environment: customtkinter, numpy, pandas, matplotlib, seaborn, Pillow, scikit-learn, scipy, statsmodels, SymPy, openpyxl, pyarrow, and pytest. The project dependency manifest now needs SymPy and SciPy declared for the scientific foundation.

## First implementation slice

The first slice adds a Symbolic mode backed by SymPy for simplify, expand, factor, differentiate, integrate, solve, and limits, plus a Matrix mode backed by NumPy for matrix/vector operations and linear systems. Both are deliberately isolated from the existing AST evaluator and covered by deterministic engine tests.

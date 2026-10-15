# AdvancedCal

AdvancedCal is a Python desktop scientific calculator and learning workspace. It combines everyday calculations with symbolic mathematics, numerical methods, matrices, number theory, data analysis, image editing, and a creator profile.

Created by **Fidèle Togbédji ZOGBE**, a computer engineering student and Python developer from Benin.

GitHub: [@fidel147](https://github.com/fidel147)

## Features

### Calculator workspaces

- Basic and advanced scientific calculations
- Trigonometric, hyperbolic, logarithmic, complex, statistical, and programming functions
- Degree, radian, and gradian angle modes
- Variables, custom functions, history, undo, and redo
- Financial calculations
- Unit conversion
- Binary, octal, decimal, and hexadecimal programming calculator

### Scientific computing

- Symbolic simplification, expansion, factorization, differentiation, integration, limits, and equation solving
- Matrix arithmetic, determinant, inverse, rank, trace, eigenvalues, linear systems, dot products, cross products, and norms
- Numerical bisection, Newton-Raphson, secant, Brent, integration, differentiation, and interpolation
- Prime testing, factorization, GCD, LCM, modular arithmetic, Fibonacci, divisors, and Euler's totient

### Data Lab

- CSV, TSV, TXT, XLSX/XLS, JSON, and Parquet import
- Dataset preview with editable cells
- Search and filtered row preview
- Dataset quality metadata and quality score
- Missing-value and duplicate handling
- Numeric median and categorical mode imputation
- Text whitespace cleanup
- Normalization, standardization, one-hot encoding, and IQR outlier removal
- Describe, numeric descriptive statistics, value counts, group counts, correlations, and inferential tests
- Histograms, scatter plots, line charts, boxplots, and Seaborn heatmaps
- Baseline regression and classification models
- CSV, JSON, plot, and HTML EDA report export
- Dataset edit undo and redo

### Image Studio

Image editing is intentionally separate from Data Lab.

- Open PNG, JPEG, WebP, BMP, and TIFF images
- Canvas preview with drag-to-select crop
- Resize, rotate, horizontal flip, and vertical flip
- Brightness and contrast adjustments
- Grayscale conversion
- Reset edits
- Export edited PNG, JPEG, or WebP images

### About

The About workspace contains the verified creator profile, GitHub profile link, GitHub-associated public projects, avatar fallback, and application credits.

## Requirements

- Python 3.12 or a compatible modern Python version
- Tkinter
- Packages listed in [requirements.txt](requirements.txt)

The selected development environment uses pandas, NumPy, Matplotlib, Seaborn, Pillow, scikit-learn, SciPy, SymPy, and customtkinter.

## Installation

Create and activate a virtual environment, then install the dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Debian or Ubuntu, Tkinter may need to be installed separately:

```sh
sudo apt install python3-tk
```

## Run

From the project directory:

```sh
python main.py
```

The application uses a mode picker in the header. Useful shortcuts include:

- `Ctrl+Alt+B` Basic
- `Ctrl+Alt+A` Advanced
- `Ctrl+Alt+D` Data Lab
- `Ctrl+Alt+I` Image Studio
- `Ctrl+Alt+M` Matrix
- `Ctrl+Alt+N` Numerical
- `Ctrl+Alt+S` Scientific
- `Ctrl+Alt+T` Number Theory
- `Ctrl+Alt+H` About

## Data Lab quick workflow

1. Open **Data Lab**.
2. Choose **Open CSV** or another supported table format.
3. Inspect the preview and quality metadata.
4. Search or double-click cells to edit values.
5. Use the cleaning controls and feature transformations.
6. Select `Describe`, `Numeric statistics`, `Automated EDA`, `Value counts`, or `Group by`.
7. Choose a chart or statistical test when appropriate.
8. Export the cleaned dataset, JSON report, HTML EDA report, or plot.

## Image Studio quick workflow

1. Open **Image Studio** with `Ctrl+Alt+I`.
2. Click **Open** and select an image.
3. Drag over the canvas to select a crop region.
4. Click **Crop selection** or apply another edit.
5. Use brightness, contrast, rotate, flip, grayscale, or resize controls.
6. Click **Save as** to export the edited image.

## Tests

Run the test suite without creating bytecode or pytest cache files:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q
```

The tests cover calculator-related scientific services, symbolic mathematics, matrices, numerical methods, number theory, statistics, data operations, and image transformations.

## Project structure

```text
AdvancedCal/
├── engine/       Mathematical, data, image, and statistical services
├── ui/           Tkinter/customtkinter application and workspaces
├── tests/        Automated regression tests
├── main.py       Application entry point
├── requirements.txt
├── ROADMAP.md
└── .gitignore
```

## Scope and limitations

AdvancedCal is a local desktop application. Advanced features such as OCR, cloud projects, external AI services, full layered image editing, database imports, and cross-platform packaging are not enabled by default. The roadmap records planned extensions without presenting them as implemented functionality.

External GitHub avatar loading and profile links require network access; local calculator, data, statistical, and image operations do not.

## License

No license has been selected yet. Add a license before distributing AdvancedCal publicly if you want to define reuse and contribution terms.

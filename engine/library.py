import cmath
import math
import statistics

# (symbol typed in the expression, description, value)
CONSTANTS = {
    "Mathematics": [
        ("π", "Pi", math.pi),
        ("e", "Euler's number", math.e),
        ("φ", "Golden ratio", (1 + math.sqrt(5)) / 2),
        ("τ", "Tau (2π)", math.tau),
    ],
    "Electromagnetism": [
        ("c", "Speed of light", 299792458),
        ("mu0", "Vacuum permeability", 1.25663706212e-6),
        ("eps0", "Vacuum permittivity", 8.8541878128e-12),
        ("qe", "Elementary charge", 1.602176634e-19),
    ],
    "Atomic & Nuclear": [
        ("h", "Planck constant", 6.62607015e-34),
        ("hbar", "Reduced Planck constant", 1.054571817e-34),
        ("me", "Electron mass", 9.1093837015e-31),
        ("mp", "Proton mass", 1.67262192369e-27),
        ("mn", "Neutron mass", 1.67492749804e-27),
        ("u", "Atomic mass unit", 1.66053906660e-27),
    ],
    "Thermodynamics": [
        ("kB", "Boltzmann constant", 1.380649e-23),
        ("NA", "Avogadro constant", 6.02214076e23),
        ("R", "Gas constant", 8.314462618),
        ("sigma", "Stefan-Boltzmann constant", 5.670374419e-8),
    ],
    "Gravitation": [
        ("G", "Gravitational constant", 6.67430e-11),
        ("g", "Standard gravity", 9.80665),
    ],
}
CONSTANT_VALUES = {sym: val for group in CONSTANTS.values() for sym, _, val in group}
CONSTANT_VALUES["i"] = 1j                      # imaginary unit, listed on the Complex page
CONSTANT_VALUES.update(pi=math.pi, tau=math.tau, phi=(1 + math.sqrt(5)) / 2)   # typed names
EXTRA_SYMBOLS = {"Complex": [("i", "Imaginary unit")]}   # constants shown inside a function page

WORD = {"bits": 64}                            # programming functions work on words of this size


def mask():
    return (1 << WORD["bits"]) - 1


def _int(x):
    if float(x) != int(x):
        raise ValueError("whole number needed")
    n = int(x)
    if abs(n) > 10000:
        raise ValueError("number too large")
    return n


def _both(real, cplx):
    """Real function that falls back to its complex version (sqrt(-4) = 2i)."""
    def f(x):
        if isinstance(x, complex):
            return cplx(x)
        try:
            return real(x)
        except ValueError:          # outside the real domain
            return cplx(x)
    return f


def _whole(x):
    if isinstance(x, complex) or x != int(x):
        raise ValueError("whole number needed")
    return int(x)


def _word(x):
    return _whole(x) & mask()


def _swap_bytes(a):
    size = WORD["bits"] // 8
    return int.from_bytes(_word(a).to_bytes(size, "big"), "little")


def _shift_left(a, n):
    n = _whole(n)
    if not 0 <= n < WORD["bits"]:
        raise ValueError("shift too large")
    return (_word(a) << n) & mask()


def _shift_right(a, n):
    n = _whole(n)
    if not 0 <= n < WORD["bits"]:
        raise ValueError("shift too large")
    return _word(a) >> n


def _round(x, digits=0):
    factor = 10 ** _int(digits)
    return math.copysign(math.floor(abs(x) * factor + 0.5), x) / factor


FUNCTIONS = {
    "Complex": {
        "re": lambda z: complex(z).real,
        "im": lambda z: complex(z).imag,
        "conj": lambda z: complex(z).conjugate(),
        "arg": lambda z: cmath.phase(z),
    },
    "Programming": {
        "and": lambda a, b: _word(a) & _word(b),
        "or": lambda a, b: _word(a) | _word(b),
        "xor": lambda a, b: _word(a) ^ _word(b),
        "not": lambda a: ~_word(a) & mask(),
        "shl": _shift_left,
        "shr": _shift_right,
        "twos": lambda a: -_word(a) & mask(),
        "swap": _swap_bytes,
    },
    "Trigonometry": {
        "sin": _both(math.sin, cmath.sin), "cos": _both(math.cos, cmath.cos),
        "tan": _both(math.tan, cmath.tan),
        "cot": lambda x: 1 / _both(math.tan, cmath.tan)(x),
        "sec": lambda x: 1 / _both(math.cos, cmath.cos)(x),
        "csc": lambda x: 1 / _both(math.sin, cmath.sin)(x),
        "asin": _both(math.asin, cmath.asin), "acos": _both(math.acos, cmath.acos),
        "atan": _both(math.atan, cmath.atan),
        "atan2": math.atan2,
        "acot": lambda x: cmath.phase(complex(x) + 1j) if isinstance(x, complex) else math.atan2(1, x),
        "asec": lambda x: _both(math.acos, cmath.acos)(1 / x),
        "acsc": lambda x: _both(math.asin, cmath.asin)(1 / x),
        "sinh": _both(math.sinh, cmath.sinh), "cosh": _both(math.cosh, cmath.cosh),
        "tanh": _both(math.tanh, cmath.tanh),
        "coth": lambda x: 1 / _both(math.tanh, cmath.tanh)(x),
        "sech": lambda x: 1 / _both(math.cosh, cmath.cosh)(x),
        "csch": lambda x: 1 / _both(math.sinh, cmath.sinh)(x),
        "asinh": _both(math.asinh, cmath.asinh), "acosh": _both(math.acosh, cmath.acosh),
        "atanh": _both(math.atanh, cmath.atanh),
        "degrees": math.degrees, "radians": math.radians,
    },
    "Rounding": {
        "floor": math.floor, "ceil": math.ceil, "round": _round,
        "trunc": math.trunc, "frac": lambda x: x - math.trunc(x),
    },
    "Statistics": {
        "mean": lambda *a: statistics.fmean(a),
        "median": lambda *a: statistics.median(a),
        "stdev": lambda *a: statistics.stdev(a),
        "min": min, "max": max, "sum": lambda *a: sum(a),
        "nCr": lambda n, k: math.comb(_int(n), _int(k)),
        "nPr": lambda n, k: math.perm(_int(n), _int(k)),
    },
    "Sundry": {
        "sqrt": _both(math.sqrt, cmath.sqrt), "cbrt": math.cbrt,
        "root": lambda x, n: x ** (1 / n),
        "exp": _both(math.exp, cmath.exp),
        "ln": _both(math.log, cmath.log), "log": _both(math.log10, cmath.log10),
        "log₂": _both(math.log2, lambda z: cmath.log(z, 2)),   # evaluator turns log₂( into log_2(
        "abs": abs, "fact": lambda x: math.factorial(_int(x)),
        "gcd": lambda a, b: math.gcd(_int(a), _int(b)),
        "lcm": lambda a, b: math.lcm(_int(a), _int(b)),
        "sgn": lambda x: (x > 0) - (x < 0),
    },
}
FUNCS = {name: fn for group in FUNCTIONS.values() for name, fn in group.items()}
# and / or / not are Python keywords, so the evaluator renames them bit_and( ...
FUNCS.update({f"bit_{n}": FUNCTIONS["Programming"][n] for n in ("and", "or", "not")})

HINTS = {
    "re": "real part", "im": "imaginary part", "conj": "conjugate", "arg": "angle",
    "and": "bitwise AND", "or": "bitwise OR", "xor": "bitwise XOR",
    "not": "bitwise NOT", "shl": "shift left", "shr": "shift right",
    "twos": "two's complement", "swap": "reverse byte order",
    "degrees": "radians → degrees", "radians": "degrees → radians",
    "cot": "cotangent", "sec": "secant", "csc": "cosecant", "atan2": "two-argument arctangent",
    "acot": "inverse cotangent", "asec": "inverse secant", "acsc": "inverse cosecant",
    "coth": "hyperbolic cotangent", "sech": "hyperbolic secant", "csch": "hyperbolic cosecant",
    "floor": "round down", "ceil": "round up", "round": "round(x, digits)",
    "trunc": "drop decimals", "frac": "decimals only",
    "mean": "average", "median": "middle value", "stdev": "sample std. dev.",
    "nCr": "combinations", "nPr": "permutations",
    "sqrt": "square root", "cbrt": "cube root", "root": "root(x, n)", "ln": "natural log",
    "log": "base-10 log", "log₂": "base-2 log", "fact": "factorial",
    "gcd": "greatest common divisor", "lcm": "least common multiple", "sgn": "sign",
}

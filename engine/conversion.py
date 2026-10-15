import math
import re

from engine.evaluator import format_value

DMS = "Degrees-Minutes-Seconds"

# unit -> how many base units it is (base: degree, metre, m², litre, kg, second)
FACTORS = {
    "Angle": {"Degrees (Decimal)": 1, DMS: 1, "Radians": 180 / math.pi, "Gradians": 0.9, "Turns": 360},
    "Length": {"Meters": 1, "Kilometers": 1000, "Centimeters": 0.01, "Millimeters": 0.001,
               "Miles": 1609.344, "Yards": 0.9144, "Feet": 0.3048, "Inches": 0.0254,
               "Nautical Miles": 1852},
    "Area": {"Square Meters": 1, "Square Kilometers": 1e6, "Hectares": 1e4,
             "Square Feet": 0.09290304, "Square Inches": 0.00064516,
             "Acres": 4046.8564224, "Square Miles": 2589988.110336},
    "Volume": {"Liters": 1, "Milliliters": 0.001, "Cubic Meters": 1000,
               "US Gallons": 3.785411784, "US Quarts": 0.946352946, "US Cups": 0.2365882365,
               "US Fluid Ounces": 0.0295735295625, "Cubic Feet": 28.316846592},
    "Weight": {"Kilograms": 1, "Grams": 0.001, "Milligrams": 1e-6, "Tonnes": 1000,
               "Pounds": 0.45359237, "Ounces": 0.028349523125, "Stone": 6.35029318},
    "Duration": {"Seconds": 1, "Milliseconds": 0.001, "Minutes": 60, "Hours": 3600,
                 "Days": 86400, "Weeks": 604800, "Years": 31557600},
}

# unit -> (to Celsius, from Celsius)
TEMPERATURE = {
    "Celsius": (lambda c: c, lambda c: c),
    "Fahrenheit": (lambda f: (f - 32) * 5 / 9, lambda c: c * 9 / 5 + 32),
    "Kelvin": (lambda k: k - 273.15, lambda c: c + 273.15),
}

# SAMPLE RATES - units per 1 US dollar. Replace with live rates (see README) before trusting them.
# The euro / CFA franc link is a real fixed peg: 1 EUR = 655.957 XOF.
_EUR = 0.86
RATES = {"US Dollar (USD)": 1.0, "Euro (EUR)": _EUR, "CFA Franc BCEAO (XOF)": _EUR * 655.957,
         "British Pound (GBP)": 0.75, "Chinese Yuan (CNY)": 7.10, "Nigerian Naira (NGN)": 1500.0,
         "Ghanaian Cedi (GHS)": 12.0, "Canadian Dollar (CAD)": 1.38}
FACTORS["Currency"] = {name: 1 / rate for name, rate in RATES.items()}

CATEGORIES = list(FACTORS) + ["Temperature"]
DEFAULTS = {"Angle": ("Degrees (Decimal)", "Radians"), "Length": ("Meters", "Feet"),
            "Area": ("Square Meters", "Square Feet"), "Volume": ("Liters", "US Gallons"),
            "Weight": ("Kilograms", "Pounds"), "Duration": ("Hours", "Minutes"),
            "Temperature": ("Celsius", "Fahrenheit"),
            "Currency": ("US Dollar (USD)", "Euro (EUR)")}


def units(category):
    return list(TEMPERATURE if category == "Temperature" else FACTORS[category])


def _number(text):
    text = text.strip()
    return 0.0 if text in ("", "-", ".", "-.") else float(text)


def parse(text):
    """'12.5', '1.', '-' (= 0) and 30°15′20″ all become a number (degrees for DMS)."""
    if not any(c in text for c in "°′″"):
        return _number(text)
    parts = re.split(r"[°′″]", text)
    parts += [""] * (3 - len(parts))
    degrees, minutes, seconds = (_number(p) for p in parts[:3])
    sign = -1 if text.strip().startswith("-") else 1
    return sign * (abs(degrees) + minutes / 60 + seconds / 3600)


def to_base(category, unit, text):
    value = parse(text)
    if category == "Temperature":
        return TEMPERATURE[unit][0](value)
    return value * FACTORS[category][unit]


def from_base(category, unit, value):
    if category == "Temperature":
        return format_value(_clean(TEMPERATURE[unit][1](value)))
    if unit == DMS:
        return _dms(value)
    return format_value(_clean(value / FACTORS[category][unit]))


def convert(category, source, target, text):
    return from_base(category, target, to_base(category, source, text))


def _clean(value):
    return 0.0 if abs(value) < 1e-12 else value        # 0 not 3e-16


def _dms(degrees):
    sign = "-" if degrees < 0 else ""
    total = round(abs(degrees) * 3600, 4)
    d, rest = divmod(total, 3600)
    m, s = divmod(rest, 60)
    return f"{sign}{int(d)}°{int(m)}′{format_value(round(s, 4))}″"

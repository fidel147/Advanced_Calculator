import ast
import cmath
import math
import operator
import random
import re

from engine.library import CONSTANT_VALUES, FUNCS, FUNCTIONS

BINARY = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
BITWISE = {   # & | ^ << >> work on whole words (see library.WORD)
    ast.BitAnd: FUNCTIONS["Programming"]["and"], ast.BitOr: FUNCTIONS["Programming"]["or"],
    ast.BitXor: FUNCTIONS["Programming"]["xor"], ast.LShift: FUNCTIONS["Programming"]["shl"],
    ast.RShift: FUNCTIONS["Programming"]["shr"],
}
ANGLE_UNIT = {"deg": math.pi / 180, "rad": 1.0, "grad": math.pi / 200}   # radians per unit
ANGLE_IN = {"sin", "cos", "tan"}          # take an angle
ANGLE_OUT = {"asin", "acos", "atan"}      # give an angle
SUBS_TO_DIGITS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
NAME = r"[A-Za-z_][A-Za-z_0-9]*"
RESERVED = set(CONSTANT_VALUES) | set(FUNCS) | {"ans", "rand"}


def expand_factorials(text):
    """5! -> fact(5), (2+3)! -> fact((2+3)), sin(1)! -> fact(sin(1))."""
    while "!" in text:
        end = text.index("!")
        start = end
        if end > 0 and text[end - 1] == ")":
            depth, start = 0, end - 1
            while start >= 0:
                depth += (text[start] == ")") - (text[start] == "(")
                if depth == 0:
                    break
                start -= 1
            if start < 0:
                raise ValueError("unbalanced brackets")
            while start > 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
                start -= 1                                   # keep a function name
        else:
            while start > 0 and (text[start - 1].isalnum() or text[start - 1] in "._"):
                start -= 1
            if start == end:
                raise ValueError("nothing before !")
        text = text[:start] + "fact(" + text[start:end] + ")" + text[end + 1:]
    return text


def simplify(value):
    """Drop rounding noise: 1e-16+2i -> 2i, and (-1+0j) -> -1."""
    if isinstance(value, complex):
        scale = max(abs(value.real), abs(value.imag))
        re_ = 0.0 if abs(value.real) < scale * 1e-12 else value.real
        im_ = 0.0 if abs(value.imag) < scale * 1e-12 else value.imag
        return re_ if im_ == 0 else complex(re_, im_)
    return value


def _real(x):
    if isinstance(x, int):
        return str(x) if abs(x) < 10**20 else f"{x:.10g}"
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return f"{x:.10g}"


def format_value(value):
    """Number -> display text. Complex numbers look like 3+4i, -2i, i."""
    if not isinstance(value, complex):
        return _real(value)
    text = _real(value.real) if value.real != 0 else ""
    if value.imag != 0 or not text:
        size = abs(value.imag)
        sign = "-" if value.imag < 0 else ("+" if text else "")
        text += f"{sign}{'' if size == 1 else _real(size)}i"
    return text


class Evaluator:
    """Turns an expression string into a number, safely (no eval)."""

    def __init__(self):
        self.variables = {}   # name -> value (includes "ans")
        self.functions = {}   # name -> (parameter names, expression tree)
        self.angle = "deg"    # "deg", "rad" or "grad": used by sin, cos, tan, asin, acos, atan

    # ---------- text -> python syntax ----------
    @staticmethod
    def prepare(text):
        text = expand_factorials(text)
        text = re.sub(r"(\d+(?:\.\d+)?)%", r"(\1/100)", text)          # 50% -> (50/100)
        text = re.sub(r"([A-Za-z]+)([₀-₉]+)(?=\()",                    # log₂( -> log_2(
                      lambda m: f"{m.group(1)}_{m.group(2).translate(SUBS_TO_DIGITS)}", text)

        def number_in_base(m):                                          # 101₂ -> 5
            base = int(m.group(2).translate(SUBS_TO_DIGITS))
            if not 2 <= base <= 36:
                raise ValueError("bad base")
            return str(int(m.group(1), base))

        text = re.sub(r"(\d+)([₀-₉]+)", number_in_base, text)
        text = re.sub(r"\b(and|or|not)(?=\()", r"bit_\1", text)          # Python keywords
        text = re.sub(r"(?<![\w.])(\d+\.?\d*|\.\d+)i(?!\w)", r"\1j", text)  # 4i -> 4j
        text = (text.replace("×", "*").replace("÷", "/")
                    .replace("^", "**").replace(" mod ", "%"))
        # programming symbols (after ^ became **, so XOR can use ^)
        for symbol, python in (("∧", "&"), ("∨", "|"), ("⊻", "^"), ("¬", "~"), ("≪", "<<"), ("≫", ">>")):
            text = text.replace(symbol, python)
        return text

    # ---------- evaluation ----------
    def evaluate(self, text):
        tree = ast.parse(self.prepare(text), mode="eval")
        return simplify(self._eval(tree.body, {}, 0))

    def _eval(self, node, local, depth):
        if depth > 50:
            raise ValueError("too deep")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float, complex):
            return node.value
        if isinstance(node, ast.Name):
            return self._lookup(node.id, local)
        if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.USub, ast.UAdd):
            value = self._eval(node.operand, local, depth + 1)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            return FUNCTIONS["Programming"]["not"](self._eval(node.operand, local, depth + 1))
        if isinstance(node, ast.BinOp) and type(node.op) in BITWISE:
            left = self._eval(node.left, local, depth + 1)
            right = self._eval(node.right, local, depth + 1)
            return BITWISE[type(node.op)](left, right)
        if isinstance(node, ast.BinOp) and type(node.op) in BINARY:
            left = self._eval(node.left, local, depth + 1)
            right = self._eval(node.right, local, depth + 1)
            if isinstance(node.op, ast.Pow):
                if abs(right) > 1000:
                    raise ValueError("exponent too large")
                if isinstance(left, int) and abs(left).bit_length() * abs(right) > 100_000:
                    raise ValueError("result too large")
            return BINARY[type(node.op)](left, right)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            args = [self._eval(a, local, depth + 1) for a in node.args]
            return self._call(node.func.id, args, depth)
        raise ValueError("unsupported")

    def _lookup(self, name, local):
        if name in local:
            return local[name]
        if name == "rand":
            return random.random()
        if name in self.variables:
            return self.variables[name]
        if name in CONSTANT_VALUES:
            return CONSTANT_VALUES[name]
        raise ValueError(f"unknown name {name}")

    def _call(self, name, args, depth):
        if name in self.functions:
            params, body = self.functions[name]
            if len(args) != len(params):
                raise ValueError("wrong number of arguments")
            return self._eval(body, dict(zip(params, args)), depth + 1)
        log_base = re.fullmatch(r"log_(\d+)", name)
        if log_base:
            if len(args) != 1:
                raise ValueError("log takes one argument")
            base = int(log_base.group(1))
            try:
                return math.log(args[0], base)
            except (ValueError, TypeError):      # negative or complex argument
                return cmath.log(args[0], base)
        if name in FUNCS:
            if name in ANGLE_IN and args and not isinstance(args[0], complex):
                args = [args[0] * ANGLE_UNIT[self.angle]] + list(args[1:])
            result = FUNCS[name](*args)
            if not isinstance(result, complex):
                if name in ANGLE_OUT:
                    result = result / ANGLE_UNIT[self.angle]
                elif name in ANGLE_IN:
                    if name == "tan" and abs(result) > 1e14:
                        raise ValueError("undefined")
                    if abs(result) < 1e-15:
                        result = 0.0                       # sin(180°) is 0, not 1.2e-16
            return result
        raise ValueError(f"unknown function {name}")

    # ---------- user variables and functions ----------
    def save_variable(self, name, value):
        if not re.fullmatch(NAME, name):
            return "Use letters, digits and _ only"
        if name in RESERVED or name in self.functions:
            return f"'{name}' is already used"
        self.variables[name] = value
        return None

    def define_function(self, text):
        m = re.fullmatch(rf"\s*({NAME})\s*\(([^)]*)\)\s*=\s*(.+)", text)
        if not m:
            return "Use the form: f(x) = x^2 + 1"
        name, params, body = m.groups()
        params = [p.strip() for p in params.split(",") if p.strip()]
        if name in FUNCS or re.fullmatch(r"log_\d+", name):
            return f"'{name}' is already a built-in function"
        if not all(re.fullmatch(NAME, p) for p in params):
            return "Bad parameter name"
        try:
            tree = ast.parse(self.prepare(body), mode="eval")
        except (SyntaxError, ValueError):
            return "Can't read the formula (write 2*x, not 2x)"
        self.functions[name] = (params, tree.body)
        return None

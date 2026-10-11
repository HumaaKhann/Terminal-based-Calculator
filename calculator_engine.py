"""
Calculation
Stack-based RPN evaluation, arithmetic operations, scientific functions, constants, and mathematical domain checks.
"""

import math
from typing import Any, Callable, Dict, List, Optional

from expression_parser import (
    CalculatorError,
    FunctionCall,
    LexerError,
    ParseError,
    Token,
    TokenType,
    parse_expression,
)
from history_manager import HistoryManager


# ============================================================================
# Math Evaluation Exception
# ============================================================================

class MathEvaluationError(CalculatorError):
    """Raised during arithmetic or mathematical evaluation (division by zero, domain errors, overflow)."""
    pass


# ============================================================================
# Safe Scientific Functions & Domain Validation
# ============================================================================

def _safe_sqrt(x: float) -> float:
    if x < 0:
        raise MathEvaluationError(f"Cannot compute square root of negative number: sqrt({x})")
    return math.sqrt(x)


def _safe_cbrt(x: float) -> float:
    return math.cbrt(x) if hasattr(math, "cbrt") else (-(abs(x) ** (1 / 3)) if x < 0 else x ** (1 / 3))


def _safe_log(x: float, base: Optional[float] = None) -> float:
    if x <= 0:
        raise MathEvaluationError(f"Logarithm domain error: argument must be positive (got {x})")
    if base is not None:
        if base <= 0:
            raise MathEvaluationError(f"Logarithm base must be positive (got {base})")
        if math.isclose(base, 1.0):
            raise MathEvaluationError("Logarithm base cannot be 1")
        return math.log(x, base)
    return math.log10(x)


def _safe_ln(x: float) -> float:
    if x <= 0:
        raise MathEvaluationError(f"Natural logarithm domain error: argument must be positive (got {x})")
    return math.log(x)


def _safe_log10(x: float) -> float:
    if x <= 0:
        raise MathEvaluationError(f"log10 domain error: argument must be positive (got {x})")
    return math.log10(x)


def _safe_log2(x: float) -> float:
    if x <= 0:
        raise MathEvaluationError(f"log2 domain error: argument must be positive (got {x})")
    return math.log2(x)


def _safe_tan(x: float) -> float:
    cos_val = math.cos(x)
    if math.isclose(cos_val, 0.0, abs_tol=1e-12):
        raise MathEvaluationError(f"tan({x}) is undefined (division by zero)")
    return math.tan(x)


def _safe_asin(x: float) -> float:
    if x < -1.0 or x > 1.0:
        raise MathEvaluationError(f"asin argument must be between -1 and 1 (got {x})")
    return math.asin(x)


def _safe_acos(x: float) -> float:
    if x < -1.0 or x > 1.0:
        raise MathEvaluationError(f"acos argument must be between -1 and 1 (got {x})")
    return math.acos(x)


def _safe_acosh(x: float) -> float:
    if x < 1.0:
        raise MathEvaluationError(f"acosh argument must be >= 1 (got {x})")
    return math.acosh(x)


def _safe_atanh(x: float) -> float:
    if x <= -1.0 or x >= 1.0:
        raise MathEvaluationError(f"atanh argument must be strictly between -1 and 1 (got {x})")
    return math.atanh(x)


def _safe_factorial(x: float) -> float:
    if x < 0:
        raise MathEvaluationError(f"Factorial undefined for negative number ({x})")
    if not math.isclose(x, round(x), abs_tol=1e-9):
        raise MathEvaluationError(f"Factorial requires an integer (got {x})")
    int_x = int(round(x))
    if int_x > 1000:
        raise MathEvaluationError(f"Factorial input too large ({int_x} > 1000)")
    return float(math.factorial(int_x))


def _safe_comb(n: float, k: float) -> float:
    if n < 0 or k < 0:
        raise MathEvaluationError("comb arguments must be non-negative")
    if not (math.isclose(n, round(n)) and math.isclose(k, round(k))):
        raise MathEvaluationError("comb arguments must be integers")
    int_n, int_k = int(round(n)), int(round(k))
    if int_k > int_n:
        return 0.0
    return float(math.comb(int_n, int_k))


def _safe_perm(n: float, k: float) -> float:
    if n < 0 or k < 0:
        raise MathEvaluationError("perm arguments must be non-negative")
    if not (math.isclose(n, round(n)) and math.isclose(k, round(k))):
        raise MathEvaluationError("perm arguments must be integers")
    int_n, int_k = int(round(n)), int(round(k))
    if int_k > int_n:
        return 0.0
    return float(math.perm(int_n, int_k))


def _safe_round(x: float, n: Optional[float] = None) -> float:
    if n is None:
        return float(round(x))
    return float(round(x, int(round(n))))


def _safe_root(x: float, n: float) -> float:
    if math.isclose(n, 0.0):
        raise MathEvaluationError("Root degree cannot be 0")
    if x < 0:
        if math.isclose(n % 2, 1.0):
            return -((-x) ** (1 / n))
        raise MathEvaluationError(f"Cannot compute even root of negative number: root({x}, {n})")
    return x ** (1 / n)


DEFAULT_FUNCTIONS: Dict[str, Dict[str, Any]] = {
    # Trigonometry
    "sin": {"fn": math.sin, "min_args": 1, "max_args": 1, "desc": "Sine of angle (radians)"},
    "cos": {"fn": math.cos, "min_args": 1, "max_args": 1, "desc": "Cosine of angle (radians)"},
    "tan": {"fn": _safe_tan, "min_args": 1, "max_args": 1, "desc": "Tangent of angle (radians)"},
    "asin": {"fn": _safe_asin, "min_args": 1, "max_args": 1, "desc": "Arcsine (radians), -1 <= x <= 1"},
    "acos": {"fn": _safe_acos, "min_args": 1, "max_args": 1, "desc": "Arccosine (radians), -1 <= x <= 1"},
    "atan": {"fn": math.atan, "min_args": 1, "max_args": 1, "desc": "Arctangent (radians)"},
    "atan2": {"fn": math.atan2, "min_args": 2, "max_args": 2, "desc": "Two-argument arctangent atan2(y, x)"},
    # Hyperbolic
    "sinh": {"fn": math.sinh, "min_args": 1, "max_args": 1, "desc": "Hyperbolic sine"},
    "cosh": {"fn": math.cosh, "min_args": 1, "max_args": 1, "desc": "Hyperbolic cosine"},
    "tanh": {"fn": math.tanh, "min_args": 1, "max_args": 1, "desc": "Hyperbolic tangent"},
    "asinh": {"fn": math.asinh, "min_args": 1, "max_args": 1, "desc": "Inverse hyperbolic sine"},
    "acosh": {"fn": _safe_acosh, "min_args": 1, "max_args": 1, "desc": "Inverse hyperbolic cosine (x >= 1)"},
    "atanh": {"fn": _safe_atanh, "min_args": 1, "max_args": 1, "desc": "Inverse hyperbolic tangent (-1 < x < 1)"},
    # Angle conversions
    "deg": {"fn": math.degrees, "min_args": 1, "max_args": 1, "desc": "Convert radians to degrees"},
    "rad": {"fn": math.radians, "min_args": 1, "max_args": 1, "desc": "Convert degrees to radians"},
    # Exponentials and Logarithms
    "exp": {"fn": math.exp, "min_args": 1, "max_args": 1, "desc": "Exponential e^x"},
    "ln": {"fn": _safe_ln, "min_args": 1, "max_args": 1, "desc": "Natural logarithm (base e)"},
    "log": {"fn": _safe_log, "min_args": 1, "max_args": 2, "desc": "log(x) base 10 or log(x, base)"},
    "log10": {"fn": _safe_log10, "min_args": 1, "max_args": 1, "desc": "Base-10 logarithm"},
    "log2": {"fn": _safe_log2, "min_args": 1, "max_args": 1, "desc": "Base-2 logarithm"},
    # Roots and Powers
    "sqrt": {"fn": _safe_sqrt, "min_args": 1, "max_args": 1, "desc": "Square root (x >= 0)"},
    "cbrt": {"fn": _safe_cbrt, "min_args": 1, "max_args": 1, "desc": "Cube root"},
    "root": {"fn": _safe_root, "min_args": 2, "max_args": 2, "desc": "Nth root: root(x, n)"},
    "pow": {"fn": math.pow, "min_args": 2, "max_args": 2, "desc": "Power function pow(base, exp)"},
    # Rounding and Arithmetic
    "abs": {"fn": abs, "min_args": 1, "max_args": 1, "desc": "Absolute value"},
    "round": {"fn": _safe_round, "min_args": 1, "max_args": 2, "desc": "Round number round(x) or round(x, n)"},
    "floor": {"fn": math.floor, "min_args": 1, "max_args": 1, "desc": "Floor (largest integer <= x)"},
    "ceil": {"fn": math.ceil, "min_args": 1, "max_args": 1, "desc": "Ceiling (smallest integer >= x)"},
    "trunc": {"fn": math.trunc, "min_args": 1, "max_args": 1, "desc": "Truncate towards zero"},
    # Combinatorics & Number Theory
    "fact": {"fn": _safe_factorial, "min_args": 1, "max_args": 1, "desc": "Factorial of non-negative integer"},
    "factorial": {"fn": _safe_factorial, "min_args": 1, "max_args": 1, "desc": "Alias for fact(x)"},
    "comb": {"fn": _safe_comb, "min_args": 2, "max_args": 2, "desc": "Combinations comb(n, k)"},
    "perm": {"fn": _safe_perm, "min_args": 2, "max_args": 2, "desc": "Permutations perm(n, k)"},
    "hypot": {"fn": math.hypot, "min_args": 2, "max_args": 2, "desc": "Euclidean hypotenuse hypot(x, y)"},
    "gcd": {"fn": lambda a, b: float(math.gcd(int(round(a)), int(round(b)))), "min_args": 2, "max_args": 2, "desc": "Greatest common divisor"},
    "lcm": {"fn": lambda a, b: float(math.lcm(int(round(a)), int(round(b)))), "min_args": 2, "max_args": 2, "desc": "Least common multiple"},
}

DEFAULT_CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "phi": (1.0 + math.sqrt(5.0)) / 2.0,
    "ans": 0.0,
}


# ============================================================================
# Evaluator (Stack-based RPN evaluation without eval)
# ============================================================================

class Evaluator:
    """
    Evaluates Reverse Polish Notation (RPN) using an operand stack.
    Applies mathematical domain checks and operations without eval().
    """

    def __init__(self, functions: Dict[str, Any], constants: Dict[str, float]):
        self.functions = functions
        self.constants = constants

    def evaluate(self, rpn: List[Any]) -> float:
        stack: List[float] = []

        for item in rpn:
            if isinstance(item, (int, float)):
                stack.append(float(item))

            elif isinstance(item, FunctionCall):
                func_meta = self.functions[item.name]
                fn: Callable = func_meta["fn"]
                min_args: int = func_meta.get("min_args", 1)
                max_args: int = func_meta.get("max_args", 1)

                if item.arg_count < min_args or item.arg_count > max_args:
                    if min_args == max_args:
                        raise MathEvaluationError(
                            f"Function '{item.name}' expects {min_args} argument{'s' if min_args != 1 else ''}, got {item.arg_count}"
                        )
                    else:
                        raise MathEvaluationError(
                            f"Function '{item.name}' expects {min_args} to {max_args} arguments, got {item.arg_count}"
                        )

                if len(stack) < item.arg_count:
                    raise ParseError(f"Insufficient operands for function '{item.name}'")

                args = [stack.pop() for _ in range(item.arg_count)]
                args.reverse()

                try:
                    res = fn(*args)
                    stack.append(float(res))
                except MathEvaluationError:
                    raise
                except ZeroDivisionError:
                    raise MathEvaluationError(f"Math Error in '{item.name}': Division by zero")
                except OverflowError:
                    raise MathEvaluationError(f"Math Error in '{item.name}': Result too large to represent (overflow)")
                except ValueError as e:
                    raise MathEvaluationError(f"Math Error in '{item.name}': {e}")
                except Exception as e:
                    raise MathEvaluationError(f"Math Error in '{item.name}': {e}")

            elif isinstance(item, Token) and item.type == TokenType.UNARY_OP:
                if len(stack) < 1:
                    raise ParseError("Missing operand for unary operator")
                a = stack.pop()
                if item.value == "u-":
                    stack.append(-a)
                elif item.value == "u+":
                    stack.append(a)

            elif isinstance(item, Token) and item.type == TokenType.OPERATOR:
                if len(stack) < 2:
                    raise ParseError(f"Missing operand for operator '{item.value}'")
                b = stack.pop()
                a = stack.pop()
                op = item.value

                if op == "+":
                    res = a + b
                elif op == "-":
                    res = a - b
                elif op == "*":
                    res = a * b
                elif op == "/":
                    if b == 0:
                        raise MathEvaluationError("Math Error: Division by zero")
                    res = a / b
                elif op == "//":
                    if b == 0:
                        raise MathEvaluationError("Math Error: Integer division by zero")
                    res = a // b
                elif op == "%":
                    if b == 0:
                        raise MathEvaluationError("Math Error: Modulo by zero")
                    res = a % b
                elif op in ("^", "**"):
                    if a == 0 and b < 0:
                        raise MathEvaluationError("Math Error: Cannot raise zero to a negative power")
                    try:
                        res = a ** b
                        if isinstance(res, complex):
                            raise MathEvaluationError("Math Error: Negative base with fractional exponent produces complex number")
                    except OverflowError:
                        raise MathEvaluationError("Math Error: Exponentiation overflow (result too large)")
                else:
                    raise ParseError(f"Unknown operator '{op}'")

                stack.append(float(res))
            else:
                raise ParseError(f"Unexpected RPN element: {item}")

        if len(stack) != 1:
            raise ParseError("Invalid expression: unbalanced operators and operands")

        return stack[0]


# ============================================================================
# Calculator Engine Facade
# ============================================================================

class CalculatorEngine:
    """
    Coordinates expression parsing, stack-based RPN evaluation, and history logging.
    """

    def __init__(self, history_file: str = "history.json"):
        self.functions = dict(DEFAULT_FUNCTIONS)
        self.constants = dict(DEFAULT_CONSTANTS)
        self.history = HistoryManager(history_file)
        self.constants["ans"] = self.history.get_last_result()

    def evaluate(self, expression: str, record_history: bool = True) -> float:
        """
        Parses and evaluates an expression, updates 'ans', and records to history.
        """
        expr_clean = expression.strip()
        if not expr_clean:
            raise ParseError("Empty expression. Please enter a mathematical expression.")

        # 1. Parse expression to RPN using Shunting-yard algorithm
        rpn = parse_expression(expr_clean, self.functions, self.constants)

        # 2. Evaluate RPN
        evaluator = Evaluator(self.functions, self.constants)
        result = evaluator.evaluate(rpn)

        # 3. Update 'ans' and record history
        self.constants["ans"] = result
        if record_history:
            self.history.add(expr_clean, result)

        return result

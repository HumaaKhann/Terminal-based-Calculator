"""
terminal_ui.py - Shared terminal styling, ASCII art, colors, and display helpers.
"""

import math
import os
import sys

# Ensure UTF-8 output on Windows and all platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Colorama initialization with fallback
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class _DummyColor:
        def __getattr__(self, _):
            return ""
    Fore = _DummyColor()
    Style = _DummyColor()


def clear_screen() -> None:
    """Clears the terminal screen when interactive."""
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def format_result(val: float) -> str:
    """Formats float result for display (cleans trailing zeros, handles scientific notation)."""
    if math.isnan(val):
        return "NaN"
    if math.isinf(val):
        return "Infinity" if val > 0 else "-Infinity"

    # Integer check
    if math.isclose(val, round(val), abs_tol=1e-12) and abs(val) < 1e15:
        return str(int(round(val)))

    # Scientific notation for very large or tiny magnitudes
    abs_val = abs(val)
    if abs_val >= 1e12 or (0 < abs_val < 1e-6):
        return f"{val:.6e}"

    formatted = f"{val:.10f}".rstrip("0").rstrip(".")
    return formatted if formatted != "-0" else "0"


# ============================================================================
# Normal Calculator ASCII Visual UI
# ============================================================================

def print_normal_header() -> None:
    """Displays the original visual header."""
    print(Fore.WHITE + "╔══════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                       CALCULATOR                         " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                  NORMAL EDITION • v1.0                   " + Fore.WHITE + "║")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║  ──────────────────────────────────────────────────────  ║")
    print(Fore.WHITE + "║                                                          ║")


def print_normal_display(expression: str = "", result: str = "") -> None:
    """Displays the calculator screen with expression and result."""
    print(Fore.WHITE + "║  " + Fore.BLUE + "DISPLAY" + Fore.WHITE + "                                                 ║")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║  ┌────────────────────────────────────────────────────┐  ║")

    if expression != "":
        print(Fore.WHITE + "║  │" + Fore.YELLOW + expression.rjust(52) + Fore.WHITE + "│  ║")
    else:
        print(Fore.WHITE + "║  │                                                    │  ║")

    if result != "":
        print(Fore.WHITE + "║  │" + Fore.GREEN + str(result).rjust(52) + Fore.WHITE + "│  ║")
    else:
        print(Fore.WHITE + "║  │                                                    │  ║")

    print(Fore.WHITE + "║  └────────────────────────────────────────────────────┘  ║")
    print(Fore.WHITE + "║                                                          ║")


def print_normal_keypad() -> None:
    """Displays the 4x4 visual keypad grid."""
    print(Fore.WHITE + "║  ┌────────────┬────────────┬────────────┬────────────┐   ║")
    print(Fore.WHITE + "║  │     7      │     8      │     9      │" + Fore.YELLOW + "     ÷      " + Fore.WHITE + "│   ║")
    print(Fore.WHITE + "║  ├────────────┼────────────┼────────────┼────────────┤   ║")
    print(Fore.WHITE + "║  │     4      │     5      │     6      │" + Fore.YELLOW + "     ×      " + Fore.WHITE + "│   ║")
    print(Fore.WHITE + "║  ├────────────┼────────────┼────────────┼────────────┤   ║")
    print(Fore.WHITE + "║  │     1      │     2      │     3      │" + Fore.YELLOW + "     −      " + Fore.WHITE + "│   ║")
    print(Fore.WHITE + "║  ├────────────┼────────────┼────────────┼────────────┤   ║")
    print(Fore.WHITE + "║  │     0      │     %      │" + Fore.GREEN + "     =      " + Fore.WHITE + "│" + Fore.YELLOW + "     +      " + Fore.WHITE + "│   ║")
    print(Fore.WHITE + "║  └────────────┴────────────┴────────────┴────────────┘   ║")
    print(Fore.WHITE + "║                                                          ║")


def print_normal_footer() -> None:
    """Displays the bottom border of the visual box."""
    print(Fore.WHITE + "╚══════════════════════════════════════════════════════════╝")


# ============================================================================
# Advanced REPL & Menu UI
# ============================================================================

def print_advanced_header() -> None:
    """Displays the header banner for Advanced Calculator REPL."""
    print(Fore.WHITE + "╔════════════════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║                                                                    ║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                  ADVANCED EXPRESSION CALCULATOR                    " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                     OPERATOR PRECEDENCE & REPL                     " + Fore.WHITE + "║")
    print(Fore.WHITE + "║                                                                    ║")
    print(Fore.WHITE + "║  ────────────────────────────────────────────────────────────────  ║")
    print(Fore.WHITE + "║" + Fore.YELLOW + "  • Enter full math expressions: 2 + 3 * 4, sin(pi/2), sqrt(16)      " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.YELLOW + "  • Previous result saved in 'ans': ans * 10                        " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.GREEN +  "  • Commands: /help, /history, /vars, /clear, /menu, /quit           " + Fore.WHITE + "║")
    print(Fore.WHITE + "╚════════════════════════════════════════════════════════════════════╝")
    print()


def print_main_menu() -> None:
    """Displays the main menu box."""
    print(Fore.WHITE + "╔══════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                 TERMINAL-BASED CALCULATOR                " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                       EDITION • v2.0                     " + Fore.WHITE + "║")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║  ──────────────────────────────────────────────────────  ║")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║" + Fore.YELLOW + "   [1] Normal Calculator (Visual UI & Keypad)             " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.YELLOW + "   [2] Advanced Expression Calculator (REPL)              " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.YELLOW + "   [3] View Calculation History (JSON)                    " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.YELLOW + "   [4] Help & Scientific Reference Guide                  " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.RED +    "   [5] Exit                                               " + Fore.WHITE + "║")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "╚══════════════════════════════════════════════════════════╝")
    print()


def print_history_table(history_entries: list) -> None:
    """Displays calculation history as a formatted table."""
    if not history_entries:
        print(Fore.YELLOW + "\n[ History is empty. Perform calculations to record history. ]\n")
        return

    print(Fore.WHITE + "\n╔════════════════════════════════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║" + Fore.CYAN + "                               CALCULATION HISTORY                                  " + Fore.WHITE + "║")
    print(Fore.WHITE + "╠═════╦═════════════════════╦═════════════════════════════════════╦══════════════════════╣")
    print(Fore.WHITE + "║  #  ║ Timestamp           ║ Expression                          ║ Result               ║")
    print(Fore.WHITE + "╠═════╬═════════════════════╬═════════════════════════════════════╬══════════════════════╣")

    for item in history_entries:
        item_id = str(item.get("id", "")).center(3)
        ts = str(item.get("timestamp", "")).ljust(19)
        raw_expr = str(item.get("expression", ""))
        expr = (raw_expr[:32] + "...") if len(raw_expr) > 35 else raw_expr.ljust(35)
        raw_res = format_result(item.get("result", 0.0))
        res = (raw_res[:19] + "...") if len(raw_res) > 20 else raw_res.rjust(20)

        print(Fore.WHITE + f"║ {item_id} ║ {ts} ║ " + Fore.YELLOW + f"{expr}" + Fore.WHITE + " ║ " + Fore.GREEN + f"{res}" + Fore.WHITE + " ║")

    print(Fore.WHITE + "╚═════╩═════════════════════╩═════════════════════════════════════╩══════════════════════╝\n")


def print_variables(constants: dict) -> None:
    """Displays current values of constants and 'ans'."""
    descriptions = {
        "ans": "Previous calculation result",
        "pi": "Archimedes' constant (circle ratio)",
        "e": "Euler's number (base of natural log)",
        "tau": "Circle constant (2 * pi)",
        "phi": "Golden ratio",
    }
    print(Fore.WHITE + "\n╔════════════════════════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║" + Fore.CYAN + "                           CONSTANTS & VARIABLES                            " + Fore.WHITE + "║")
    print(Fore.WHITE + "╠═════════════╦══════════════════════╦═══════════════════════════════════════╣")
    print(Fore.WHITE + "║ Identifier  ║ Value                ║ Description                           ║")
    print(Fore.WHITE + "╠═════════════╬══════════════════════╬═══════════════════════════════════════╣")

    for k in sorted(constants.keys()):
        val_str = format_result(constants[k]).rjust(20)
        desc = descriptions.get(k, "User variable").ljust(37)
        k_str = k.ljust(11)
        print(Fore.WHITE + f"║ " + Fore.CYAN + f"{k_str}" + Fore.WHITE + f" ║ " + Fore.GREEN + f"{val_str}" + Fore.WHITE + f" ║ {desc} ║")

    print(Fore.WHITE + "╚═════════════╩══════════════════════╩═══════════════════════════════════════╝\n")


def print_help() -> None:
    """Displays comprehensive help and function guide."""
    print(Fore.CYAN + "\n=== CALCULATOR REFERENCE GUIDE ===")

    print(Fore.YELLOW + "\n[ OPERATORS & PRECEDENCE ]" + Fore.WHITE)
    print("  1. Parentheses:     ( )")
    print("  2. Functions:       sin(), sqrt(), log(), fact(), etc.")
    print("  3. Exponentiation:  ^ or ** (Right-associative, e.g. 2^3^2 = 512)")
    print("  4. Unary Operators: + , - (e.g. -5 + 3 = -2, 2^-3 = 0.125)")
    print("  5. Multiplicative:  * , / , // (integer division) , % (modulo)")
    print("  6. Additive:        + , -")
    print(Fore.GREEN + "  * Implicit multiplication is supported: 2pi, 2(3+4), 3sqrt(16)")

    print(Fore.YELLOW + "\n[ SCIENTIFIC FUNCTIONS ]" + Fore.WHITE)
    print("  • Trigonometric:    sin(x), cos(x), tan(x), asin(x), acos(x), atan(x), atan2(y, x)")
    print("  • Hyperbolic:       sinh(x), cosh(x), tanh(x), asinh(x), acosh(x), atanh(x)")
    print("  • Angles:           deg(radians) [rad to deg], rad(degrees) [deg to rad]")
    print("  • Logs & Powers:    ln(x), log(x) [base 10], log(x, base), log2(x), exp(x), pow(x, y)")
    print("  • Roots:            sqrt(x), cbrt(x), root(x, n)")
    print("  • Combinatorics:    fact(n) or factorial(n), comb(n, k), perm(n, k)")
    print("  • Rounding/Misc:    abs(x), round(x) or round(x, n), floor(x), ceil(x), trunc(x)")
    print("  • Other:            hypot(x, y), gcd(a, b), lcm(a, b)")

    print(Fore.YELLOW + "\n[ CONSTANTS & VARIABLES ]" + Fore.WHITE)
    print("  • pi   ≈ 3.141592653589793")
    print("  • e    ≈ 2.718281828459045")
    print("  • tau  ≈ 6.283185307179586 (2 * pi)")
    print("  • phi  ≈ 1.618033988749895 (Golden ratio)")
    print("  • ans  = Result of the last successful calculation")

    print(Fore.YELLOW + "\n[ REPL COMMANDS ]" + Fore.WHITE)
    print("  • /help          Show this reference guide")
    print("  • /clear         Clear the terminal screen")
    print("  • /history       View recent calculation history from JSON")
    print("  • /history clear Clear saved calculation history")
    print("  • /vars          List all constants and current value of 'ans'")
    print("  • /menu          Return to Main Menu")
    print("  • /quit, /exit   Exit the calculator")
    print()
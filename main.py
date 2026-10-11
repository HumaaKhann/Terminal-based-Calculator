# Interface
# Main menu, ASCII keypad and display, advanced REPL, CLI arguments, and user interaction.

import math
import os
import sys
from typing import Optional

# Ensure terminal stdout/stderr uses UTF-8 encoding on Windows and all platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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

from expression_parser import CalculatorError, LexerError, ParseError
from calculator_engine import CalculatorEngine, MathEvaluationError
from history_manager import HistoryManager


# ============================================================================
# Utilities & Output Formatting
# ============================================================================

def clear_screen() -> None:
    """Clears the terminal screen when running interactively."""
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def format_result(val: float) -> str:
    """Formats float result for display (cleans trailing zeros, uses scientific notation if extreme)."""
    if math.isnan(val):
        return "NaN"
    if math.isinf(val):
        return "Infinity" if val > 0 else "-Infinity"

    # Integer check
    if math.isclose(val, round(val), abs_tol=1e-12) and abs(val) < 1e15:
        return str(int(round(val)))

    # Scientific notation for very large or very small magnitudes
    abs_val = abs(val)
    if abs_val >= 1e12 or (0 < abs_val < 1e-6):
        return f"{val:.6e}"

    # General float formatting (strip trailing zeros)
    formatted = f"{val:.10f}".rstrip("0").rstrip(".")
    return formatted if formatted != "-0" else "0"


# ============================================================================
# NORMAL CALCULATOR (Visual ASCII UI & Step-by-Step Keypad)
# ============================================================================

def get_number(prompt_num: int) -> float:
    """Prompts the user for a valid number with validation."""
    while True:
        operand = input(f"Enter number {prompt_num}: ")
        try:
            return float(operand)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a valid number.")


def print_normal_header() -> None:
    """Displays the visual ASCII header for Normal Calculator."""
    print(Fore.WHITE + "╔══════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                       CALCULATOR                         " + Fore.WHITE + "║")
    print(Fore.WHITE + "║" + Fore.CYAN + "                  NORMAL EDITION • v1.0                   " + Fore.WHITE + "║")
    print(Fore.WHITE + "║                                                          ║")
    print(Fore.WHITE + "║  ──────────────────────────────────────────────────────  ║")
    print(Fore.WHITE + "║                                                          ║")


def print_normal_display(expression: str = "", result: str = "") -> None:
    """Displays the mock calculator screen with expression and result."""
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
    """Displays the visual 4x4 keypad grid."""
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
    """Displays the bottom border of the calculator interface."""
    print(Fore.WHITE + "╚══════════════════════════════════════════════════════════╝")


def run_normal_calculator(engine: Optional[CalculatorEngine] = None) -> None:
    """Runs the original step-by-step calculator with the visual ASCII interface."""
    while True:
        clear_screen()
        print_normal_header()
        operand1 = get_number(1)

        clear_screen()
        print_normal_header()
        print_normal_display(str(operand1))
        print_normal_keypad()
        print_normal_footer()

        operator = input("Enter operator (+, -, *, /, %, **): ").strip()

        clear_screen()
        print_normal_header()
        expression_prompt = str(operand1) + " " + operator
        print_normal_display(expression_prompt)
        print_normal_keypad()
        print_normal_footer()

        operand2 = get_number(2)

        result = 0.0
        calculation_done = False

        if operator == "+":
            result = operand1 + operand2
            calculation_done = True
        elif operator == "-":
            result = operand1 - operand2
            calculation_done = True
        elif operator == "*":
            result = operand1 * operand2
            calculation_done = True
        elif operator == "%":
            if operand2 != 0:
                result = operand1 % operand2
                calculation_done = True
            else:
                clear_screen()
                print_normal_header()
                print(Fore.RED + "║  Error: Cannot divide by zero.                          ║")
                print(Fore.WHITE + "║                                                          ║")
                print_normal_footer()
        elif operator == "**":
            try:
                result = operand1 ** operand2
                calculation_done = True
            except OverflowError:
                clear_screen()
                print_normal_header()
                print(Fore.RED + "║  Error: Number too large (overflow).                    ║")
                print(Fore.WHITE + "║                                                          ║")
                print_normal_footer()
        elif operator == "/":
            if operand2 != 0:
                result = operand1 / operand2
                calculation_done = True
            else:
                clear_screen()
                print_normal_header()
                print(Fore.RED + "║  Error: Division by zero.                              ║")
                print(Fore.WHITE + "║                                                          ║")
                print_normal_footer()
        else:
            clear_screen()
            print_normal_header()
            print(Fore.WHITE + "║  " + Fore.RED + "Error: Invalid operator." + Fore.WHITE + "                                ║")
            print(Fore.WHITE + "║                                                          ║")
            print_normal_footer()

        if calculation_done:
            clear_screen()
            print_normal_header()

            if operator == "*":
                display_op = "×"
            elif operator == "/":
                display_op = "÷"
            elif operator == "-":
                display_op = "−"
            elif operator == "**":
                display_op = "^"
            else:
                display_op = operator

            display_expr = f"{operand1} {display_op} {operand2} ="
            display_res = round(result, 4) if not math.isclose(result, round(result)) else int(round(result))
            print_normal_display(display_expr, str(display_res))
            print_normal_keypad()
            print_normal_footer()

            # Record to JSON history and update 'ans'
            if engine:
                history_expr = f"{operand1} {operator} {operand2}"
                engine.history.add(history_expr, float(result))
                engine.constants["ans"] = float(result)

        print()
        again = input("Do you want to calculate again? (yes/no): ").strip().lower()
        if again in ("no", "n"):
            break


# ============================================================================
# ADVANCED EXPRESSION CALCULATOR (REPL)
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


def run_advanced_repl(engine: CalculatorEngine) -> None:
    """Runs the interactive Read-Eval-Print Loop for full mathematical expressions."""
    clear_screen()
    print_advanced_header()

    step = len(engine.history.history) + 1

    while True:
        try:
            prompt = Fore.WHITE + f"calc [{step}] > " + Fore.CYAN
            user_input = input(prompt).strip()
            print(Style.RESET_ALL, end="")

            if not user_input:
                continue

            lower_input = user_input.lower()

            if lower_input in ("/quit", "/exit", "quit", "exit", "q"):
                print(Fore.GREEN + "\nReturning to Main Menu...\n")
                break

            if lower_input in ("/menu", "menu", "/back", "back"):
                break

            if lower_input in ("/clear", "clear", "cls"):
                clear_screen()
                print_advanced_header()
                continue

            if lower_input in ("/help", "help", "?"):
                print_help()
                continue

            if lower_input in ("/vars", "vars"):
                print_variables(engine)
                continue

            if lower_input in ("/history", "history"):
                print_history_table(engine)
                continue

            if lower_input in ("/history clear", "history clear"):
                engine.history.clear()
                print(Fore.GREEN + "[ Calculation history cleared. ]\n")
                continue

            # Evaluate Expression
            result = engine.evaluate(user_input, record_history=True)
            formatted = format_result(result)
            print(Fore.GREEN + f"  = {formatted}\n")
            step += 1

        except (LexerError, ParseError) as e:
            print(Fore.RED + f"Syntax Error: {e}\n")
        except MathEvaluationError as e:
            print(Fore.RED + f"{e}\n")
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n[ Type /menu to return to menu or /quit to exit. ]\n")
        except EOFError:
            break
        except Exception as e:
            print(Fore.RED + f"Unexpected Error: {e}\n")


# ============================================================================
# HISTORY & HELP VIEWS
# ============================================================================

def print_history_table(engine: CalculatorEngine) -> None:
    """Displays calculation history as a formatted table."""
    entries = engine.history.get_recent(15)
    if not entries:
        print(Fore.YELLOW + "\n[ History is empty. Perform calculations to record history. ]\n")
        return

    print(Fore.WHITE + "\n╔════════════════════════════════════════════════════════════════════════════════════╗")
    print(Fore.WHITE + "║" + Fore.CYAN + "                               CALCULATION HISTORY                                  " + Fore.WHITE + "║")
    print(Fore.WHITE + "╠═════╦═════════════════════╦═════════════════════════════════════╦══════════════════════╣")
    print(Fore.WHITE + "║  #  ║ Timestamp           ║ Expression                          ║ Result               ║")
    print(Fore.WHITE + "╠═════╬═════════════════════╬═════════════════════════════════════╬══════════════════════╣")

    for item in entries:
        item_id = str(item.get("id", "")).center(3)
        ts = str(item.get("timestamp", "")).ljust(19)
        raw_expr = str(item.get("expression", ""))
        expr = (raw_expr[:32] + "...") if len(raw_expr) > 35 else raw_expr.ljust(35)
        raw_res = format_result(item.get("result", 0.0))
        res = (raw_res[:19] + "...") if len(raw_res) > 20 else raw_res.rjust(20)

        print(Fore.WHITE + f"║ {item_id} ║ {ts} ║ " + Fore.YELLOW + f"{expr}" + Fore.WHITE + " ║ " + Fore.GREEN + f"{res}" + Fore.WHITE + " ║")

    print(Fore.WHITE + "╚═════╩═════════════════════╩═════════════════════════════════════╩══════════════════════╝\n")


def print_variables(engine: CalculatorEngine) -> None:
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

    for k in sorted(engine.constants.keys()):
        val_str = format_result(engine.constants[k]).rjust(20)
        desc = descriptions.get(k, "User variable").ljust(37)
        k_str = k.ljust(11)
        print(Fore.WHITE + f"║ " + Fore.CYAN + f"{k_str}" + Fore.WHITE + f" ║ " + Fore.GREEN + f"{val_str}" + Fore.WHITE + f" ║ {desc} ║")

    print(Fore.WHITE + "╚═════════════╩══════════════════════╩═══════════════════════════════════════╝\n")


def print_help() -> None:
    """Displays comprehensive help, syntax guide, functions, and commands."""
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
    print("  • /clear         Clear the terminal screen and redisplay header")
    print("  • /history       View recent calculation history from JSON")
    print("  • /history clear Clear saved calculation history")
    print("  • /vars          List all constants and current value of 'ans'")
    print("  • /menu          Return to Main Menu")
    print("  • /quit, /exit   Exit the calculator")
    print()


# ============================================================================
# MAIN APPLICATION MENU
# ============================================================================

def show_main_menu(engine: CalculatorEngine) -> None:
    """Displays the main menu and routes to selected mode."""
    while True:
        clear_screen()
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

        try:
            choice = input(Fore.WHITE + "Select an option (1-5): " + Fore.CYAN).strip()
            print(Style.RESET_ALL, end="")

            if choice in ("1", "normal", "basic"):
                run_normal_calculator(engine)

            elif choice in ("2", "advanced", "repl"):
                run_advanced_repl(engine)

            elif choice in ("3", "history"):
                clear_screen()
                print_history_table(engine)
                input(Fore.WHITE + "\nPress Enter to return to menu...")

            elif choice in ("4", "help"):
                clear_screen()
                print_help()
                input(Fore.WHITE + "\nPress Enter to return to menu...")

            elif choice in ("5", "exit", "quit", "q"):
                print(Fore.GREEN + "\nThank you for using Terminal Calculator. Goodbye!\n")
                break

            else:
                print(Fore.RED + "\nInvalid selection. Please choose an option between 1 and 5.")
                input(Fore.WHITE + "Press Enter to try again...")

        except (KeyboardInterrupt, EOFError):
            print(Fore.GREEN + "\n\nGoodbye!\n")
            break


# ============================================================================
# Entry Point
# ============================================================================

def main() -> None:
    """Entry point: processes CLI arguments or launches interactive menu."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    history_file = os.path.join(script_dir, "history.json")
    engine = CalculatorEngine(history_file=history_file)

    # CLI one-shot evaluation mode
    if len(sys.argv) > 1:
        arg = " ".join(sys.argv[1:]).strip()

        if arg in ("-h", "--help", "help"):
            print("Usage:")
            print("  python project2.py                     Launch interactive calculator menu")
            print("  python project2.py \"<expression>\"      Evaluate expression directly and exit")
            print("  python project2.py --help              Show command-line options")
            print("\nExamples:")
            print("  python project2.py \"2 + 3 * 4\"")
            print("  python project2.py \"sin(pi / 2) + sqrt(16)\"")
            print("  python project2.py \"2 ^ 3 ^ 2\"")
            sys.exit(0)

        try:
            result = engine.evaluate(arg, record_history=True)
            print(format_result(result))
            sys.exit(0)
        except CalculatorError as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"Unexpected Error: {e}\n")
            sys.exit(1)

    # Launch Main Interactive Menu
    show_main_menu(engine)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
main.py - Main menu and application navigation.
Connects terminal_ui, calculator_engine, and expression_parser.
"""

import math
import os
import sys

from terminal import (
    Fore,
    Style,
    clear_screen,
    format_result,
    print_advanced_header,
    print_help,
    print_history_table,
    print_main_menu,
    print_normal_display,
    print_normal_footer,
    print_normal_header,
    print_normal_keypad,
    print_variables,
)
from calculator_engine import CalculatorEngine, MathEvaluationError, CalculatorError
from expression_parser import LexerError, ParseError


def get_number(prompt_num: int) -> float:
    """Prompts the user for a valid number with validation."""
    while True:
        operand = input(f"Enter number {prompt_num}: ")
        try:
            return float(operand)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a valid number.")


# ============================================================================
# Mode 1: Normal Calculator (Visual UI & Keypad)
# ============================================================================

def run_normal_calculator(engine: CalculatorEngine) -> None:
    """Runs the step-by-step calculator with the visual ASCII interface."""
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
            history_expr = f"{operand1} {operator} {operand2}"
            engine.history.add(history_expr, float(result))
            engine.constants["ans"] = float(result)

        print()
        again = input("Do you want to calculate again? (yes/no): ").strip().lower()
        if again in ("no", "n"):
            break


# ============================================================================
# Mode 2: Advanced Expression Calculator (REPL)
# ============================================================================

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
                print_variables(engine.constants)
                continue

            if lower_input in ("/history", "history"):
                print_history_table(engine.history.get_recent(15))
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
# Main Menu & CLI Entry Point
# ============================================================================

def show_main_menu(engine: CalculatorEngine) -> None:
    """Displays the main menu and routes to selected mode."""
    while True:
        clear_screen()
        print_main_menu()

        try:
            choice = input(Fore.WHITE + "Select an option (1-5): " + Fore.CYAN).strip()
            print(Style.RESET_ALL, end="")

            if choice in ("1", "normal", "basic"):
                run_normal_calculator(engine)

            elif choice in ("2", "advanced", "repl"):
                run_advanced_repl(engine)

            elif choice in ("3", "history"):
                clear_screen()
                print_history_table(engine.history.get_recent(15))
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
            print("  python main.py                     Launch interactive calculator menu")
            print("  python main.py \"<expression>\"      Evaluate expression directly and exit")
            print("  python main.py --help              Show command-line options")
            print("\nExamples:")
            print("  python main.py \"2 + 3 * 4\"")
            print("  python main.py \"sin(pi / 2) + sqrt(16)\"")
            print("  python main.py \"2 ^ 3 ^ 2\"")
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

    show_main_menu(engine)


if __name__ == "__main__":
    main()
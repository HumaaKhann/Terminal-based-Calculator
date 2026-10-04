# Text-based calculator
# Beautify the calculator in the terminal using ASCII art and colors.
# Use the colorama library to add colors to the output.
# ASCII art is used to create the calculator interface.

import os
from colorama import Fore, init
init(autoreset=True)


def get_number(number):

    while True:
        operand = input("Enter number " + str(number) + ": ")
        try:
            return float(operand)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a valid number.")


def clear_screen():
    os.system("cls")


def print_header():

    print(Fore.WHITE +"╔══════════════════════════════════════════════════════════╗")
    print(Fore.WHITE +"║                                                          ║")
    print(Fore.WHITE +"║" + Fore.CYAN + "                       CALCULATOR                         " + Fore.WHITE + "║")
    print(Fore.WHITE +"║" + Fore.CYAN + "                  TERMINAL EDITION • v1.0                 " + Fore.WHITE + "║")
    print(Fore.WHITE +"║                                                          ║")
    print(Fore.WHITE +"║  ──────────────────────────────────────────────────────  ║")
    print(Fore.WHITE +"║                                                          ║")


def print_display(expression="", result=""):

    print(Fore.WHITE +  "║  " + Fore.BLUE + "DISPLAY" + Fore.WHITE + "                                                 ║")
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


def print_keypad():

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


def print_footer():

    print(Fore.WHITE + "╚══════════════════════════════════════════════════════════╝")


while True:

    clear_screen()
    print_header()
    operand1 = get_number(1)
    clear_screen()
    print_header()
    print_display(str(operand1))
    print_keypad()
    print_footer()

    operator = input("Enter operator (+, -, *, /, %, **): ")
    clear_screen()
    print_header()
    expression = str(operand1) + " " + operator
    print_display(expression)
    print_keypad()
    print_footer()

    operand2 = get_number(2)


    result = 0
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
            print_header()
            print(Fore.RED + "║  Error: Cannot divide by zero.                          ║")
            print(Fore.WHITE+"║                                                         ║")

            print_footer()


    elif operator == "**":

        result = operand1 ** operand2
        calculation_done = True


    elif operator == "/":

        if operand2 != 0:

            result = operand1 / operand2
            calculation_done = True

        else:

            clear_screen()

            print_header()

            print(Fore.RED + "║  Error: Division by zero.                              ║")
            print(Fore.WHITE+"║                                                        ║")

            print_footer()


    else:

        clear_screen()

        print_header()

        print(Fore.WHITE+"║  " + Fore.RED + "Error: Invalid operator." + Fore.WHITE + "                                ║")
        print(Fore.WHITE+"║                                                          ║")

        print_footer()


    # Show final result

    if calculation_done:

        clear_screen()

        print_header()


        if operator == "*":

            display_operator = "×"

        elif operator == "/":

            display_operator = "÷"

        elif operator == "-":

            display_operator = "−"

        elif operator == "**":

            display_operator = "^"

        else:

            display_operator = operator


        expression = str(operand1) + " " + display_operator + " " + str(operand2) + " ="

        print_display(expression, round(result, 4))

        print_keypad()

        print_footer()


    print()

    again = input("Do you want to calculate again? (yes/no): ").lower()

    if again == "no":

        break
# Terminal-Based Calculator (v2.0)

A modular, terminal-based scientific calculator and command-line tool built in Python. Evolved from a simple two-operand script into a full-featured expression calculator featuring Dijkstra's Shunting-yard algorithm, safe evaluation without `eval()`, persistent JSON history, scientific functions, and an interactive REPL.

---

## Folder Structure

```text
Terminal-based-Calculator/
│
├── main.py                   # Interface: Main menu, ASCII keypad and display, advanced REPL, CLI arguments
│
├── expression_parser.py      # Parsing: Tokenizer, token validation, operator precedence, parentheses, Shunting-yard RPN
│
├── calculator_engine.py      # Calculation: Stack-based RPN evaluation, arithmetic, scientific functions, domain checks
│
├── history_manager.py        # Persistence: Records calculations, timestamps, results, JSON saving/loading
│
├── test_calculator.py        # Testing: Automated tests for parsing, calculations, scientific functions, errors, history
│
├── README.md                 # Documentation: Features, installation, usage, and architecture
│
├── .gitignore                # Excludes cache files, bytecode, and local runtime data
│
└── history.json              # (Generated at runtime) Stores calculation history
```

---

## Key Features & Architecture

### 1. `main.py` (Interface)
- **Main Menu (Options 1–5):**
  - **[1] Normal Calculator:** Your original step-by-step visual calculator featuring the styled ASCII header, dynamic DISPLAY box, full 4x4 KEYPAD grid, and calculation repeat prompt.
  - **[2] Advanced Expression Calculator:** Interactive REPL (`calc > `) parsing full mathematical expressions with precedence and scientific functions.
  - **[3] View Calculation History:** Formatted table displaying all past calculations.
  - **[4] Help & Scientific Reference Guide:** Categorized reference manual of operators and functions.
  - **[5] Exit:** Clean termination.
- **Direct CLI Mode:** Evaluate expressions directly from your terminal: `python project2.py "2 + 3 * 4"`.

### 2. `expression_parser.py` (Parsing)
- **Tokenizer:** Scans numbers, operators, identifiers, and distinguishes unary operators (`-5`, `2^-3`).
- **Implicit Multiplication:** Supports natural math syntax like `2pi`, `2(3+4)`, `3sqrt(16)`.
- **Dijkstra's Shunting-yard Algorithm:** Translates infix expressions into Reverse Polish Notation (RPN).
- **Precedence & Associativity:** Right-associative powers (`2 ^ 3 ^ 2 = 512`), multi-level precedence, parentheses nesting.
- **Syntax Error Handling:** Catches unmatched parentheses, consecutive operators, misplaced commas, and invalid tokens.

### 3. `calculator_engine.py` (Calculation)
- **Stack-based Evaluator:** Safely evaluates RPN without Python's `eval()` or `exec()`.
- **Scientific Functions:**
  - *Trigonometric & Hyperbolic:* `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`.
  - *Angle conversions:* `deg`, `rad`.
  - *Logarithms & Powers:* `ln`, `log`, `log10`, `log2`, `exp`, `pow`.
  - *Roots:* `sqrt`, `cbrt`, `root(x, n)`.
  - *Combinatorics & Integers:* `fact`/`factorial`, `comb`, `perm`, `gcd`, `lcm`.
  - *Rounding & Misc:* `abs`, `round`, `floor`, `ceil`, `trunc`, `hypot`.
- **Constants:** `pi`, `e`, `tau`, `phi`, and `ans` (previous calculation result).
- **Mathematical Domain Checks:** Division-by-zero, log of non-positive numbers, negative square roots, and overflow constraints.

### 4. `history_manager.py` (Persistence)
- Records timestamped calculations to `history.json`.
- Restores the last result into variable `ans` across program restarts.
- Provides functions to add, retrieve, view, and clear history.

### 5. `test_calculator.py` (Testing)
- Comprehensive test suite (24 automated tests) verifying all parsing rules, precedence, mathematical functions, domain errors, and JSON persistence.

---

## How to Run

### Prerequisites
Make sure Python 3.8+ is installed:
```bash
pip install colorama
```

### 1. Interactive Menu Mode
```bash
python main.py
```
Select `1` for the original Visual Keypad Calculator, or `2` for the Advanced Expression Calculator!

### 2. Direct CLI Evaluation Mode
```bash
python project2.py "2 + 3 * 4"
# Output: 14

python project2.py "sin(pi / 2) + sqrt(16)"
# Output: 5

python project2.py "2 ^ 3 ^ 2"
# Output: 512
```

---

## Running the Unit Tests

Execute the automated test suite:
```bash
python -m unittest test_calculator.py
```
All 24 unit tests pass cleanly.

"""
Automated unit tests for Terminal-Based Calculator.
Tests parsing, tokenization, Shunting-yard RPN conversion, operator precedence,
calculations, scientific functions, error handling, and history persistence.
"""

import math
import os
import tempfile
import unittest

from expression_parser import (
    CalculatorError,
    Lexer,
    LexerError,
    ParseError,
    ShuntingYardParser,
    Token,
    TokenType,
    parse_expression,
)
from calculator_engine import (
    CalculatorEngine,
    Evaluator,
    MathEvaluationError,
    DEFAULT_CONSTANTS,
    DEFAULT_FUNCTIONS,
)
from history_manager import HistoryManager


class TestTokenizerAndParser(unittest.TestCase):
    """Tests expression tokenization and Shunting-yard parsing."""

    def test_tokenization_numbers_and_operators(self):
        lexer = Lexer("2 + 3.14 * 10", set(DEFAULT_FUNCTIONS.keys()), set(DEFAULT_CONSTANTS.keys()))
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        self.assertEqual(types, [
            TokenType.NUMBER,
            TokenType.OPERATOR,
            TokenType.NUMBER,
            TokenType.OPERATOR,
            TokenType.NUMBER
        ])

    def test_unary_vs_binary_operators(self):
        lexer = Lexer("-5 + 3 * -2", set(DEFAULT_FUNCTIONS.keys()), set(DEFAULT_CONSTANTS.keys()))
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, TokenType.UNARY_OP)
        self.assertEqual(tokens[0].value, "u-")
        self.assertEqual(tokens[2].type, TokenType.OPERATOR)
        self.assertEqual(tokens[2].value, "+")
        self.assertEqual(tokens[5].type, TokenType.UNARY_OP)
        self.assertEqual(tokens[5].value, "u-")

    def test_implicit_multiplication(self):
        lexer = Lexer("2pi + 2(3 + 4)", set(DEFAULT_FUNCTIONS.keys()), set(DEFAULT_CONSTANTS.keys()))
        tokens = lexer.tokenize()
        # Verify '*' was inserted between 2 and pi, and between 2 and (
        values = [t.value for t in tokens]
        self.assertIn("*", values)

    def test_shunting_yard_rpn_order(self):
        # Infix: 2 + 3 * 4 -> RPN: 2 3 4 * +
        rpn = parse_expression("2 + 3 * 4", DEFAULT_FUNCTIONS, DEFAULT_CONSTANTS)
        self.assertEqual(rpn[0], 2)
        self.assertEqual(rpn[1], 3)
        self.assertEqual(rpn[2], 4)
        self.assertEqual(rpn[3].value, "*")
        self.assertEqual(rpn[4].value, "+")


class TestCalculatorPrecedenceAndBasicMath(unittest.TestCase):
    """Tests arithmetic evaluation and operator precedence."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.engine = CalculatorEngine(history_file=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_basic_arithmetic(self):
        self.assertEqual(self.engine.evaluate("2 + 3"), 5.0)
        self.assertEqual(self.engine.evaluate("10 - 4"), 6.0)
        self.assertEqual(self.engine.evaluate("6 * 7"), 42.0)
        self.assertEqual(self.engine.evaluate("15 / 3"), 5.0)
        self.assertEqual(self.engine.evaluate("17 // 5"), 3.0)
        self.assertEqual(self.engine.evaluate("17 % 5"), 2.0)

    def test_operator_precedence(self):
        self.assertEqual(self.engine.evaluate("2 + 3 * 4"), 14.0)
        self.assertEqual(self.engine.evaluate("(2 + 3) * 4"), 20.0)
        self.assertEqual(self.engine.evaluate("10 - 2 * 3"), 4.0)
        self.assertEqual(self.engine.evaluate("100 / 5 / 2"), 10.0)
        self.assertEqual(self.engine.evaluate("2 * 3 ^ 2"), 18.0)
        self.assertEqual(self.engine.evaluate("2 * 3 ** 2"), 18.0)

    def test_right_associative_power(self):
        # 2 ^ (3 ^ 2) = 2 ^ 9 = 512, NOT 64
        self.assertEqual(self.engine.evaluate("2 ^ 3 ^ 2"), 512.0)
        self.assertEqual(self.engine.evaluate("2 ** 3 ** 2"), 512.0)

    def test_unary_operators(self):
        self.assertEqual(self.engine.evaluate("-5 + 3"), -2.0)
        self.assertEqual(self.engine.evaluate("3 * -2"), -6.0)
        self.assertEqual(self.engine.evaluate("-(2 + 3)"), -5.0)
        self.assertEqual(self.engine.evaluate("+5"), 5.0)
        self.assertEqual(self.engine.evaluate("--5"), 5.0)
        self.assertEqual(self.engine.evaluate("2 * +3"), 6.0)
        self.assertEqual(self.engine.evaluate("-2 ^ 2"), -4.0)
        self.assertEqual(self.engine.evaluate("(-2) ^ 2"), 4.0)
        self.assertEqual(self.engine.evaluate("2 ^ -3"), 0.125)

    def test_nested_parentheses(self):
        self.assertEqual(self.engine.evaluate("((2 + 3) * (4 + 1)) / 5"), 5.0)
        self.assertEqual(self.engine.evaluate("(((10)))"), 10.0)
        self.assertEqual(self.engine.evaluate("(5 + (3 - (1 + 1)))"), 6.0)
        self.assertEqual(self.engine.evaluate("1 + 2 * (3 + 4 * (5 + 6))"), 95.0)

    def test_scientific_notation_inputs(self):
        self.assertEqual(self.engine.evaluate("1e3 + 2.5e2"), 1250.0)
        self.assertEqual(self.engine.evaluate("2E2 * 3"), 600.0)
        self.assertEqual(self.engine.evaluate("1e-3"), 0.001)

    def test_implicit_multiplication(self):
        self.assertAlmostEqual(self.engine.evaluate("2pi"), 2 * math.pi)
        self.assertEqual(self.engine.evaluate("2(3 + 4)"), 14.0)
        self.assertEqual(self.engine.evaluate("(2 + 3)(4 + 5)"), 45.0)
        self.assertEqual(self.engine.evaluate("3sqrt(16)"), 12.0)


class TestScientificFunctionsAndConstants(unittest.TestCase):
    """Tests scientific functions and mathematical constants."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.engine = CalculatorEngine(history_file=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_trigonometry(self):
        self.assertAlmostEqual(self.engine.evaluate("sin(0)"), 0.0)
        self.assertAlmostEqual(self.engine.evaluate("sin(pi / 2)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("cos(0)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("cos(pi)"), -1.0)
        self.assertAlmostEqual(self.engine.evaluate("tan(0)"), 0.0)
        self.assertAlmostEqual(self.engine.evaluate("asin(1)"), math.pi / 2)
        self.assertAlmostEqual(self.engine.evaluate("acos(1)"), 0.0)
        self.assertAlmostEqual(self.engine.evaluate("atan(1)"), math.pi / 4)
        self.assertAlmostEqual(self.engine.evaluate("atan2(1, 1)"), math.pi / 4)

    def test_hyperbolic(self):
        self.assertAlmostEqual(self.engine.evaluate("sinh(0)"), 0.0)
        self.assertAlmostEqual(self.engine.evaluate("cosh(0)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("tanh(0)"), 0.0)

    def test_angle_conversions(self):
        self.assertAlmostEqual(self.engine.evaluate("deg(pi)"), 180.0)
        self.assertAlmostEqual(self.engine.evaluate("rad(180)"), math.pi)

    def test_exponential_and_logarithms(self):
        self.assertAlmostEqual(self.engine.evaluate("exp(0)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("exp(1)"), math.e)
        self.assertAlmostEqual(self.engine.evaluate("ln(e)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("log10(100)"), 2.0)
        self.assertAlmostEqual(self.engine.evaluate("log(100)"), 2.0)
        self.assertAlmostEqual(self.engine.evaluate("log(8, 2)"), 3.0)
        self.assertAlmostEqual(self.engine.evaluate("log2(16)"), 4.0)

    def test_roots_and_powers(self):
        self.assertEqual(self.engine.evaluate("sqrt(16)"), 4.0)
        self.assertEqual(self.engine.evaluate("cbrt(27)"), 3.0)
        self.assertEqual(self.engine.evaluate("cbrt(-27)"), -3.0)
        self.assertEqual(self.engine.evaluate("root(27, 3)"), 3.0)
        self.assertEqual(self.engine.evaluate("pow(2, 4)"), 16.0)

    def test_combinatorics_and_integers(self):
        self.assertEqual(self.engine.evaluate("fact(0)"), 1.0)
        self.assertEqual(self.engine.evaluate("fact(5)"), 120.0)
        self.assertEqual(self.engine.evaluate("factorial(4)"), 24.0)
        self.assertEqual(self.engine.evaluate("comb(5, 2)"), 10.0)
        self.assertEqual(self.engine.evaluate("perm(5, 2)"), 20.0)
        self.assertEqual(self.engine.evaluate("gcd(12, 18)"), 6.0)
        self.assertEqual(self.engine.evaluate("lcm(4, 6)"), 12.0)

    def test_rounding_and_misc(self):
        self.assertEqual(self.engine.evaluate("abs(-7.5)"), 7.5)
        self.assertEqual(self.engine.evaluate("floor(3.8)"), 3.0)
        self.assertEqual(self.engine.evaluate("ceil(3.2)"), 4.0)
        self.assertEqual(self.engine.evaluate("trunc(-3.8)"), -3.0)
        self.assertEqual(self.engine.evaluate("round(3.14159, 2)"), 3.14)
        self.assertEqual(self.engine.evaluate("hypot(3, 4)"), 5.0)

    def test_constants_and_ans(self):
        self.assertAlmostEqual(self.engine.evaluate("pi"), math.pi)
        self.assertAlmostEqual(self.engine.evaluate("e"), math.e)
        self.assertAlmostEqual(self.engine.evaluate("tau"), math.tau)
        self.assertAlmostEqual(self.engine.evaluate("phi"), (1 + math.sqrt(5)) / 2)

        # Test 'ans' persistence
        self.assertEqual(self.engine.evaluate("10 + 5"), 15.0)
        self.assertEqual(self.engine.evaluate("ans * 2"), 30.0)
        self.assertEqual(self.engine.evaluate("ans / 3"), 10.0)


class TestErrorHandling(unittest.TestCase):
    """Tests syntax, lexer, and arithmetic error handling."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.engine = CalculatorEngine(history_file=self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_arithmetic_errors(self):
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("5 / 0")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("5 // 0")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("5 % 0")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("0 ^ -2")

    def test_domain_errors(self):
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("sqrt(-4)")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("log(0)")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("ln(-1)")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("asin(2)")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("acos(-1.5)")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("fact(-3)")
        with self.assertRaises(MathEvaluationError):
            self.engine.evaluate("fact(2.5)")

    def test_syntax_and_parser_errors(self):
        with self.assertRaises(ParseError):
            self.engine.evaluate("")
        with self.assertRaises(ParseError):
            self.engine.evaluate("   ")
        with self.assertRaises(ParseError):
            self.engine.evaluate("(2 + 3")
        with self.assertRaises(ParseError):
            self.engine.evaluate("2 + 3)")
        with self.assertRaises(ParseError):
            self.engine.evaluate("2 + * 3")
        with self.assertRaises(ParseError):
            self.engine.evaluate("2 +")
        with self.assertRaises(ParseError):
            self.engine.evaluate("* 5")
        with self.assertRaises(ParseError):
            self.engine.evaluate("()")
        with self.assertRaises(ParseError):
            self.engine.evaluate("sin()")
        with self.assertRaises(ParseError):
            self.engine.evaluate("unknown_func(5)")
        with self.assertRaises(ParseError):
            self.engine.evaluate("var_x + 1")

    def test_lexer_errors(self):
        with self.assertRaises(LexerError):
            self.engine.evaluate("2 @ 3")
        with self.assertRaises(LexerError):
            self.engine.evaluate("3.14.15 + 2")


class TestHistoryPersistence(unittest.TestCase):
    """Tests JSON persistence via HistoryManager."""

    def test_json_history_lifecycle(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tf:
            path = tf.name

        try:
            # Create HistoryManager with temporary JSON file
            hm = HistoryManager(filepath=path)
            self.assertEqual(len(hm.history), 0)

            # Add entries
            hm.add("2 + 3", 5.0)
            hm.add("4 * 5", 20.0)

            # Check history entries
            history_entries = hm.get_recent(10)
            self.assertEqual(len(history_entries), 2)
            self.assertEqual(history_entries[0]["expression"], "2 + 3")
            self.assertEqual(history_entries[0]["result"], 5.0)
            self.assertEqual(history_entries[1]["expression"], "4 * 5")
            self.assertEqual(history_entries[1]["result"], 20.0)

            # Create a new HistoryManager with the same file - verifies loading
            hm2 = HistoryManager(filepath=path)
            self.assertEqual(len(hm2.history), 2)
            self.assertEqual(hm2.get_last_result(), 20.0)

            # Clear history
            hm2.clear()
            self.assertEqual(len(hm2.history), 0)

            # Re-read
            hm3 = HistoryManager(filepath=path)
            self.assertEqual(len(hm3.history), 0)
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    unittest.main()

#Parsing
#Tokenizer, token validation, operator precedence, parentheses, and the Shunting-yard algorithm to convert expressions into RPN.

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Union


# ============================================================================
# Exception Hierarchy for Parsing
# ============================================================================

class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""
    pass


class LexerError(CalculatorError):
    """Raised when tokenization fails (invalid characters, malformed numbers)."""
    pass


class ParseError(CalculatorError):
    """Raised when expression grammar or structure is invalid."""
    pass


# ============================================================================
# Token Definitions
# ============================================================================

class TokenType(Enum):
    NUMBER = auto()
    IDENT = auto()       # Function name or constant/variable identifier
    OPERATOR = auto()    # Binary operators: +, -, *, /, //, %, ^, **
    UNARY_OP = auto()    # Unary operators: u+, u-
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # , (argument separator)


@dataclass
class Token:
    type: TokenType
    value: Any
    pos: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.pos})"


@dataclass
class FunctionCall:
    name: str
    arg_count: int

    def __repr__(self) -> str:
        return f"FunctionCall({self.name}, args={self.arg_count})"


# Operator specifications: precedence, associativity, and arity
OPERATORS: Dict[str, Dict[str, Any]] = {
    "+": {"prec": 1, "assoc": "L", "arity": 2},
    "-": {"prec": 1, "assoc": "L", "arity": 2},
    "*": {"prec": 2, "assoc": "L", "arity": 2},
    "/": {"prec": 2, "assoc": "L", "arity": 2},
    "//": {"prec": 2, "assoc": "L", "arity": 2},
    "%": {"prec": 2, "assoc": "L", "arity": 2},
    "u+": {"prec": 3, "assoc": "R", "arity": 1},
    "u-": {"prec": 3, "assoc": "R", "arity": 1},
    "^": {"prec": 4, "assoc": "R", "arity": 2},
    "**": {"prec": 4, "assoc": "R", "arity": 2},
}


# ============================================================================
# Tokenizer / Lexer
# ============================================================================

class Lexer:
    """
    Tokenizes raw mathematical strings into a stream of tokens.
    Handles numbers (ints, floats, scientific notation), operators,
    unary +/- differentiation, identifiers, parentheses, and implicit multiplication.
    """

    def __init__(self, text: str, functions: Set[str], constants: Set[str]):
        self.text = text
        self.pos = 0
        self.functions = functions
        self.constants = constants

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        n = len(self.text)

        while self.pos < n:
            ch = self.text[self.pos]

            if ch.isspace():
                self.pos += 1
                continue

            start_pos = self.pos

            # Numbers: digits or leading decimal dot followed by digit
            if ch.isdigit() or (ch == '.' and self.pos + 1 < n and self.text[self.pos + 1].isdigit()):
                has_dot = (ch == '.')
                has_exp = False
                self.pos += 1
                while self.pos < n:
                    c = self.text[self.pos]
                    if c.isdigit():
                        self.pos += 1
                    elif c == '.' and not has_dot and not has_exp:
                        has_dot = True
                        self.pos += 1
                    elif c in 'eE' and not has_exp:
                        has_exp = True
                        self.pos += 1
                        if self.pos < n and self.text[self.pos] in '+-':
                            self.pos += 1
                    else:
                        break

                num_str = self.text[start_pos:self.pos]
                # Catch invalid number formats like '3.14.15'
                if self.pos < n and self.text[self.pos] == '.':
                    raise LexerError(f"Invalid number format '{num_str}.' at position {start_pos}")

                try:
                    val: Union[int, float] = float(num_str) if (has_dot or has_exp) else int(num_str)
                except ValueError:
                    raise LexerError(f"Invalid number '{num_str}' at position {start_pos}")

                # Check for implicit multiplication with previous token
                if tokens and self._needs_implicit_mul(tokens[-1], "NUMBER"):
                    tokens.append(Token(TokenType.OPERATOR, "*", start_pos))

                tokens.append(Token(TokenType.NUMBER, val, start_pos))
                continue

            # Identifiers: functions or constants (letters and underscores)
            if ch.isalpha() or ch == '_':
                while self.pos < n and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    self.pos += 1
                ident = self.text[start_pos:self.pos].lower()

                # Check for implicit multiplication (e.g. 2pi -> 2 * pi, 2sin(x) -> 2 * sin(x))
                if tokens and self._needs_implicit_mul(tokens[-1], "IDENT", ident):
                    tokens.append(Token(TokenType.OPERATOR, "*", start_pos))

                tokens.append(Token(TokenType.IDENT, ident, start_pos))
                continue

            # Parentheses
            if ch == '(':
                # Check for implicit multiplication (e.g. 2(3+4) -> 2 * (3+4), (2+3)(4+5) -> (2+3) * (4+5))
                if tokens and self._needs_implicit_mul(tokens[-1], "LPAREN"):
                    tokens.append(Token(TokenType.OPERATOR, "*", start_pos))
                tokens.append(Token(TokenType.LPAREN, '(', start_pos))
                self.pos += 1
                continue

            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ')', start_pos))
                self.pos += 1
                continue

            # Argument separator
            if ch == ',':
                tokens.append(Token(TokenType.COMMA, ',', start_pos))
                self.pos += 1
                continue

            # Multi-character operators
            if ch == '*' and self.pos + 1 < n and self.text[self.pos + 1] == '*':
                tokens.append(Token(TokenType.OPERATOR, "**", start_pos))
                self.pos += 2
                continue
            if ch == '/' and self.pos + 1 < n and self.text[self.pos + 1] == '/':
                tokens.append(Token(TokenType.OPERATOR, "//", start_pos))
                self.pos += 2
                continue

            # Plus and Minus: Determine unary vs binary
            if ch in "+-":
                is_unary = False
                if not tokens:
                    is_unary = True
                elif tokens[-1].type in (TokenType.OPERATOR, TokenType.UNARY_OP, TokenType.LPAREN, TokenType.COMMA):
                    is_unary = True

                if is_unary:
                    tokens.append(Token(TokenType.UNARY_OP, f"u{ch}", start_pos))
                else:
                    tokens.append(Token(TokenType.OPERATOR, ch, start_pos))
                self.pos += 1
                continue

            # Other binary operators: *, /, %, ^
            if ch in "*/%^":
                tokens.append(Token(TokenType.OPERATOR, ch, start_pos))
                self.pos += 1
                continue

            # Unrecognized character
            raise LexerError(f"Unexpected character '{ch}' at position {start_pos}")

        return tokens

    def _needs_implicit_mul(self, prev: Token, current_kind: str, current_val: str = "") -> bool:
        """Determines if implicit multiplication '*' should be inserted between tokens."""
        if prev.type == TokenType.NUMBER:
            return current_kind in ("LPAREN", "IDENT")
        if prev.type == TokenType.RPAREN:
            return current_kind in ("NUMBER", "LPAREN", "IDENT")
        if prev.type == TokenType.IDENT:
            if prev.value in self.constants:
                return current_kind in ("NUMBER", "LPAREN", "IDENT")
        return False


# ============================================================================
# Shunting-yard Parser (Infix to Reverse Polish Notation)
# ============================================================================

class ShuntingYardParser:
    """
    Parses a token stream into Reverse Polish Notation (RPN) using Dijkstra's Shunting-yard algorithm.
    Enforces operator precedence and right-associativity, handles multi-parameter functions,
    and performs strict syntax validation.
    """

    def __init__(self, tokens: List[Token], functions: Dict[str, Any], constants: Dict[str, float]):
        self.tokens = tokens
        self.functions = functions
        self.constants = constants

    def parse(self) -> List[Any]:
        if not self.tokens:
            raise ParseError("Empty expression. Please enter a mathematical expression.")

        # Validation for starting/ending tokens
        first_token = self.tokens[0]
        if first_token.type == TokenType.OPERATOR:
            raise ParseError(f"Expression cannot start with binary operator '{first_token.value}' at position {first_token.pos}")

        last_token = self.tokens[-1]
        if last_token.type in (TokenType.OPERATOR, TokenType.UNARY_OP):
            raise ParseError(f"Expression cannot end with incomplete operator '{last_token.value}' at position {last_token.pos}")
        if last_token.type == TokenType.COMMA:
            raise ParseError(f"Expression cannot end with a comma at position {last_token.pos}")

        output: List[Any] = []
        op_stack: List[Any] = []
        arg_count_stack: List[int] = []

        prev_token: Optional[Token] = None

        for i, token in enumerate(self.tokens):
            # Check consecutive binary operators
            if token.type == TokenType.OPERATOR and prev_token and prev_token.type == TokenType.OPERATOR:
                raise ParseError(f"Unexpected operator '{token.value}' immediately following '{prev_token.value}' at position {token.pos}")

            # Check binary operator right after '('
            if token.type == TokenType.OPERATOR and prev_token and prev_token.type == TokenType.LPAREN:
                raise ParseError(f"Unexpected operator '{token.value}' immediately following '(' at position {token.pos}")

            # Check operator right before ')'
            if token.type == TokenType.RPAREN and prev_token and prev_token.type in (TokenType.OPERATOR, TokenType.UNARY_OP):
                raise ParseError(f"Unexpected ')' after operator '{prev_token.value}' at position {token.pos}")

            # Process tokens
            if token.type == TokenType.NUMBER:
                output.append(token.value)

            elif token.type == TokenType.IDENT:
                ident = token.value
                is_followed_by_lparen = (i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.LPAREN)

                if is_followed_by_lparen:
                    if ident not in self.functions:
                        raise ParseError(f"Unknown function '{ident}' at position {token.pos}. Type /help for available functions.")
                    op_stack.append(token)
                else:
                    if ident in self.constants:
                        output.append(self.constants[ident])
                    elif ident in self.functions:
                        raise ParseError(f"Function '{ident}' must be followed by parentheses '()' at position {token.pos}")
                    else:
                        raise ParseError(f"Unknown identifier or constant '{ident}' at position {token.pos}. Available constants: {', '.join(sorted(self.constants.keys()))}")

            elif token.type == TokenType.LPAREN:
                # Check for empty parens '()'
                if i + 1 < len(self.tokens) and self.tokens[i + 1].type == TokenType.RPAREN:
                    if op_stack and isinstance(op_stack[-1], Token) and op_stack[-1].type == TokenType.IDENT:
                        arg_count_stack.append(0)
                    else:
                        raise ParseError(f"Empty parentheses '()' at position {token.pos}")
                else:
                    if op_stack and isinstance(op_stack[-1], Token) and op_stack[-1].type == TokenType.IDENT:
                        arg_count_stack.append(1)

                op_stack.append(token)

            elif token.type == TokenType.COMMA:
                if not arg_count_stack:
                    raise ParseError(f"Misplaced comma ',' outside of function call at position {token.pos}")
                while op_stack and (not isinstance(op_stack[-1], Token) or op_stack[-1].type != TokenType.LPAREN):
                    output.append(op_stack.pop())
                if not op_stack:
                    raise ParseError(f"Misplaced comma ',' or missing '(' at position {token.pos}")
                arg_count_stack[-1] += 1

            elif token.type == TokenType.RPAREN:
                while op_stack and (not isinstance(op_stack[-1], Token) or op_stack[-1].type != TokenType.LPAREN):
                    output.append(op_stack.pop())
                if not op_stack:
                    raise ParseError(f"Unmatched closing parenthesis ')' at position {token.pos}")
                # Pop '('
                op_stack.pop()

                # If a function is directly preceding the LPAREN on op_stack, pop it
                if op_stack and isinstance(op_stack[-1], Token) and op_stack[-1].type == TokenType.IDENT:
                    func_token = op_stack.pop()
                    arg_count = arg_count_stack.pop()

                    # Validate function arity during parsing
                    func_meta = self.functions.get(func_token.value)
                    if func_meta:
                        min_args = func_meta.get("min_args", 1)
                        max_args = func_meta.get("max_args", 1)
                        if arg_count < min_args or arg_count > max_args:
                            if min_args == max_args:
                                raise ParseError(
                                    f"Function '{func_token.value}' expects {min_args} argument{'s' if min_args != 1 else ''}, got {arg_count} at position {func_token.pos}"
                                )
                            else:
                                raise ParseError(
                                    f"Function '{func_token.value}' expects {min_args} to {max_args} arguments, got {arg_count} at position {func_token.pos}"
                                )

                    output.append(FunctionCall(func_token.value, arg_count))

            elif token.type in (TokenType.OPERATOR, TokenType.UNARY_OP):
                op = token.value
                info = OPERATORS[op]

                if token.type == TokenType.UNARY_OP:
                    # Unary operator is prefix: push directly without popping prior binary ops
                    op_stack.append(token)
                else:
                    prec2 = info["prec"]
                    assoc = info["assoc"]

                    while op_stack:
                        top = op_stack[-1]
                        if isinstance(top, Token) and top.type in (TokenType.OPERATOR, TokenType.UNARY_OP):
                            prec1 = OPERATORS[top.value]["prec"]
                            if (assoc == "L" and prec1 >= prec2) or (assoc == "R" and prec1 > prec2):
                                output.append(op_stack.pop())
                            else:
                                break
                        else:
                            break
                    op_stack.append(token)

            prev_token = token

        while op_stack:
            top = op_stack.pop()
            if isinstance(top, Token) and top.type == TokenType.LPAREN:
                raise ParseError("Unmatched opening parenthesis '(' - missing closing parenthesis")
            output.append(top)

        return output


def parse_expression(text: str, functions: Dict[str, Any], constants: Dict[str, float]) -> List[Any]:
    """Convenience helper to tokenize and parse an expression into an RPN list."""
    lexer = Lexer(text, set(functions.keys()), set(constants.keys()))
    tokens = lexer.tokenize()
    parser = ShuntingYardParser(tokens, functions, constants)
    return parser.parse()

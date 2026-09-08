"""
Module: expression_tree.py
Subject: INF310 - Data Structures II
Description: Expression Tree built from postfix tokens (mirrors the
             Java ExpressionTree), plus a Shunting Yard algorithm to
             convert infix expressions (e.g. "(((3 + 6) * (2 - 4)) +
             7)") into postfix tokens so the tree can be built and
             evaluated directly from a normal infix string.

Author: Vladimir
"""

from datastructures.bin_tree.binary_tree import BinaryNode, BinaryTree


class ExpressionNode(BinaryNode):
    """Node of an ExpressionTree: holds either an operand (float) or
    an operator (single-character string) as data.
    """

    def __init__(self, data, left_child=None, right_child=None):
        super().__init__(data)
        self.left_child = left_child
        self.right_child = right_child


class ExpressionTree(BinaryTree):
    """Binary tree that represents an arithmetic expression.

    Built from a list of postfix tokens (as the Java version does),
    or from an infix string via from_infix(), which uses the
    Shunting Yard algorithm to produce the postfix tokens first.
    """

    # Operator precedence (higher binds tighter).
    _PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    _RIGHT_ASSOCIATIVE = {'^'}
    _OPERATORS = "+-*/^"

    def __init__(self, expression):
        """Build the tree from a list of postfix tokens.

        expression: list of str tokens, e.g.
            ["7", "3", "+", "5", "2", "-", "*"]
        """
        super().__init__()
        nodes_stack = []
        for token in expression:
            if self.is_operator(token):
                if len(nodes_stack) < 2:
                    raise ValueError(
                        "Wrong done expression. Please verify"
                    )
                right_child = nodes_stack.pop()
                left_child = nodes_stack.pop()
                expression_node = ExpressionNode(
                    token, left_child, right_child
                )
                nodes_stack.append(expression_node)
            else:
                try:
                    num = float(token)
                except ValueError:
                    raise ValueError("Number token invalid!")
                num_node = ExpressionNode(num)
                nodes_stack.append(num_node)

        if len(nodes_stack) != 1:
            raise ValueError(
                "Wrong built expression. Operators remaining"
            )
        self.root = nodes_stack.pop()

    # ------------------------------------------------------------------
    # Alternate constructor: build directly from an infix string
    # ------------------------------------------------------------------
    @classmethod
    def from_infix(cls, infix_expression):
        """Build an ExpressionTree straight from an infix string,
        e.g. "(((3 + 6) * (2 - 4)) + 7)".
        e.g. "(((3 + 6) * (2 - 4)^3) + 7)".
        """
        tokens = cls.tokenize_infix(infix_expression)
        postfix_tokens = cls.infix_to_postfix(tokens)
        return cls(postfix_tokens)

    @staticmethod
    def tokenize_infix(infix_expression):
        """Split an infix expression string into a list of tokens:
        numbers (int/decimal), the four basic operators, '^', and
        parentheses. Whitespace is ignored. Unary minus is NOT
        supported (matches the Java version's scope, which only
        ever consumed already-built postfix tokens).
        """
        tokens = []
        i = 0
        length = len(infix_expression)
        while i < length:
            char = infix_expression[i]
            if char.isspace():
                i += 1
                continue
            if char in "()":
                tokens.append(char)
                i += 1
                continue
            if char in ExpressionTree._OPERATORS:
                tokens.append(char)
                i += 1
                continue
            if char.isdigit() or char == '.':
                start = i
                while i < length and (
                    infix_expression[i].isdigit()
                    or infix_expression[i] == '.'
                ):
                    i += 1
                tokens.append(infix_expression[start:i])
                continue
            raise ValueError(
                "Invalid character in expression: '" + char + "'"
            )
        return tokens

    @staticmethod
    def infix_to_postfix(tokens):
        """Shunting Yard algorithm: convert infix tokens to postfix
        tokens, respecting operator precedence and associativity.
        """
        output = []
        operator_stack = []
        precedence = ExpressionTree._PRECEDENCE
        right_associative = ExpressionTree._RIGHT_ASSOCIATIVE

        for token in tokens:
            if token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Mismatched parentheses")
                operator_stack.pop()  # discard the '('
            elif token in precedence:
                while (
                    operator_stack
                    and operator_stack[-1] != '('
                    and (
                        precedence[operator_stack[-1]] > precedence[token]
                        or (
                            precedence[operator_stack[-1]]
                            == precedence[token]
                            and token not in right_associative
                        )
                    )
                ):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            else:
                output.append(token)

        while operator_stack:
            top = operator_stack.pop()
            if top == '(':
                raise ValueError("Mismatched parentheses")
            output.append(top)

        return output

    # ------------------------------------------------------------------
    # Core behaviour
    # ------------------------------------------------------------------
    def is_operator(self, token):
        return len(token) == 1 and token in self._OPERATORS

    def evaluate(self):
        if self.is_empty_tree():
            print("evaluate tree is empty")
            return -1

        postfix = self.post_order()
        stack = []
        for token in postfix:
            if isinstance(token, float):
                stack.append(token)
            else:
                op = token
                b = stack.pop()
                a = stack.pop()
                if op == '+':
                    stack.append(a + b)
                elif op == '-':
                    stack.append(a - b)
                elif op == '*':
                    stack.append(a * b)
                elif op == '/':
                    stack.append(a / b)
                elif op == '^':
                    stack.append(a ** b)
                else:
                    raise ValueError("Unknown operator: " + str(op))
        return stack.pop()

    @staticmethod
    def list_to_string(token_list):
        return " ".join(str(token) for token in token_list)



from typing import Any, List
from pylox.expr import Expr, Literal, Grouping, Unary, Binary, Variable, Assign, Logical
from pylox.stmt import Stmt, Print, Expression, Var, Block, If, While
from pylox.token import TokenType, Token
from pylox.runtime_error import RuntimeError
from pylox.error_reporter import runtime_error
from pylox.environment import Environment


class Interpreter:
    def __init__(self):
        self.environment = Environment()

    # --- Public interface ---

    def interpret(self, statements: List[Stmt]):
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeError as e:
            runtime_error(e)

    # --- Private helpers ---

    def _execute(self, stmt: Stmt):
        stmt.accept(self)

    def _execute_block(self, statements: List[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def _stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(obj)

    def _is_truthy(self, obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    def _is_equal(self, a: Any, b: Any) -> bool:
        return a == b

    def _check_number_operand(self, operator: Token, operand: Any) -> None:
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number")

    def _check_number_operands(self, operator: Token, a: Any, b: Any) -> None:
        if isinstance(a, float) and isinstance(b, float):
            return
        raise RuntimeError(operator, "Operands must be numbers")

    # --- Statement visitors ---

    def visit_expression(self, stmt: Expression):
        self._evaluate(stmt.expression)

    def visit_if_stmt(self, stmt: If):
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)
        return None

    def visit_print(self, stmt: Print):
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_var_stmt(self, stmt: Var):
        value = None
        if stmt.initializer:
            value = self._evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return

    def visit_while_stmt(self, stmt: While):
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)
        return None

    def visit_var_expression(self, expr: Variable):
        return self.environment.get(expr.name)

    def visit_var_assignment(self, expr: Assign):
        value = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_block_stmt(self, stmt: Block):
        self._execute_block(stmt.statements, Environment(self.environment))
        return None

    # --- Expression visitors ---

    def visit_literal(self, expr: Literal) -> Any:
        return expr.value

    def visit_logical(self, expr: Logical) -> Any:
        left = self._evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left
        return self._evaluate(expr.right)

    def visit_grouping(self, expr: Grouping) -> Any:
        return self._evaluate(expr.expression)

    def visit_unary(self, expr: Unary) -> Any:
        right = self._evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                return -float(right)
            case TokenType.BANG:
                return not self._is_truthy(right)
        return None

    def visit_binary(self, expr: Binary) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise RuntimeError(expr.operator, "Cannot divide by 0")
                return float(left) / float(right)
            case TokenType.STAR:
                self._check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return str(left) + str(right)
                elif isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                raise RuntimeError(
                    expr.operator, "Operands must be two strings or two numbers"
                )
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
        return None

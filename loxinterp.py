# loxinterp.py
#
# Tree-walking interpreter

from collections import ChainMap
from loxast import NodeVisitor

# Lox truthiness.  See pg. 101. 
def _is_truthy(value):
    if value is None:
        return False
    elif isinstance(value, bool):
        return value
    else:
        return True

def _check_numeric_operands(op, left, right):
    if isinstance(left, float) and isinstance(right, float):
        return True
    else:
        raise RuntimeError(f"{op} operands must be numbers")

def _check_numeric_operand(op, value):
    if isinstance(value, float):
        return True
    else:
        raise RuntimeError(f"{op} operand must be a number")

class LoxInterpreter(NodeVisitor):
    def __init__(self):
        self.env = ChainMap()
        
    def visit_Statements(self, node):
        self.env = self.env.new_child()
        for stmt in node.statements:
            self.visit(stmt)
        self.env = self.env.parents

    def visit_Literal(self, node):
        return node.value

    def visit_Binary(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            (isinstance(left, str) and isinstance(right, str)) or _check_numeric_operands(node.op, left, right)
            return left + right
        elif node.op == '-':
            _check_numeric_operands(node.op, left, right)
            return left - right
        elif node.op == '*':
            _check_numeric_operands(node.op, left, right)            
            return left * right
        elif node.op == '/':
            _check_numeric_operands(node.op, left, right)            
            return left / right
        elif node.op == '==':
            return left == right
        elif node.op == '<':
            _check_numeric_operands(node.op, left, right)            
            return left < right
        elif node.op == '>':
            _check_numeric_operands(node.op, left, right)            
            return left > right
        elif node.op == '<=':
            _check_numeric_operands(node.op, left, right)            
            return left <= right
        elif node.op == '>=':
            _check_numeric_operands(node.op, left, right)            
            return left >= right
        else:
            raise NotImplementedError(f"Bad operator {node.op}")

    def visit_Logical(self, node):
        left = self.visit(node.left)
        if node.op == 'or':
            return left if _is_truthy(left) else self.visit(node.right)
        if node.op == 'and':
            return self.visit(node.right) if _is_truthy(left) else left
        raise NotImplementedError(f"Bad operator {node.op}")
        
    def visit_Unary(self, node):
        operand = self.visit(node.operand)
        if node.op == "-":
            _check_numeric_operand(node.op, operand)
            return -operand
        elif node.op == "!":
            return not _is_truthy(operand)
        else:
            raise NotImplementedError(f"Bad operator {node.op}")

    def visit_Grouping(self, node):
        return self.visit(node.value)

    def visit_Variable(self, node):
        if node.name in self.env:
            return self.env[node.name]
        else:
            raise RuntimeError(f'Variable {node.name} not defined')
    
    def visit_Print(self, node):
        print(self.visit(node.value))

    def visit_ExpressionStmt(self, node):
        self.visit(node.expr)
        
    def visit_VarDeclaration(self, node):
        if node.initializer:
            initializer = self.visit(node.initializer)
        else:
            initializer = None
        self.env[node.name] = initializer

    def visit_Assign(self, node):
        for env in self.env.maps:
            if node.name in env:
                env[node.name] = self.visit(node.value)
                break
        else:
            raise RuntimeError(f'Variable {node.name} not declared')
        
    def visit_IfStmt(self, node):
        test = self.visit(node.test)
        if _is_truthy(test):
            self.visit(node.consequence)
        elif node.alternative:
            self.visit(node.alternative)

    def visit_WhileStmt(self, node):
        while _is_truthy(self.visit(node.test)):
            self.visit(node.body)
            

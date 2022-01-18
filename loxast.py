# loxast.py

class Node:
    # Track define AST node-names for some later sanity checks
    _nodenames = set()
    @classmethod
    def __init_subclass__(cls):
        Node._nodenames.add(cls.__name__)
        
    def __repr__(self):
        args = ', '.join(f'{key}={value!r}' for key, value in vars(self).items())
        return f'{type(self).__name__}({args})'

    def __eq__(self, other):
        return type(self) == type(other) and vars(self) == vars(other)

class Expression(Node):
    pass

class Literal(Expression):
    def __init__(self, value):
        self.value = value

class Binary(Expression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Unary(Expression):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Grouping(Expression):
    def __init__(self, value):
        self.value = value

class Statement(Node):
    pass

class Print(Statement):
    def __init__(self, value):
        self.value = value

class ExpressionStmt(Statement):
    def __init__(self, expr):
        self.expr = expr

class Statements(Node):
    def __init__(self, statements):
        self.statements = statements

class NodeVisitor:
    @classmethod
    def __init_subclass__(cls):
        # Verify that any visit_* method actually corresponds to the name of an AST node.
        visitors = { key for key in cls.__dict__ if key.startswith('visit_') }
        assert all(key[6:] in Node._nodenames for key in visitors)
        
    def visit(self, node):
        method = f'visit_{type(node).__name__}'
        return getattr(self, method)(node)

# Debugging class for turning the AST into S-expressions

class ASTPrinter(NodeVisitor):
    def visit_Statements(self, node):
        return '(statements ' + '\n'.join(self.visit(stmt) for stmt in node.statements) + '\n)'

    def visit_Print(self, node):
        return f'(print {self.visit(node.value)})'

    def visit_ExpressionStmt(self, node):
        return f'(exprstmt {self.visit(node.expr)})'
    
    def visit_Literal(self, node):
        if node.value is None:
            return "nil"
        elif node.value is True:
            return "true"
        elif node.value is False:
            return "false"
        else:
            return repr(node.value)

    def visit_Binary(self, node):
        return f'({node.op} {self.visit(node.left)} {self.visit(node.right)})'

    def visit_Unary(self, node):
        return f'({node.op} {self.visit(node.operand)})'

    def visit_Grouping(self, node):
        return f'(group {self.visit(node.value)})'
    
        
    

    



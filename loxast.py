# loxast.py

class Node:
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

        



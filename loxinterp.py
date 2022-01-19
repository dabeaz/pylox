# loxinterp.py
#
# Tree-walking interpreter

from collections import ChainMap
from loxast import NodeVisitor
import loxresolve

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

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
        
class LoxFunction:
    def __init__(self, interp, parameters, statements, env):
        self.interp = interp
        self.parameters = parameters
        self.statements = statements
        self.env = env

    def __call__(self, *args):
        if len(args) != len(self.parameters):
            raise RuntimeError("Wrong # arguments")
        newenv = self.env.new_child()
        for name, arg in zip(self.parameters, args):
            newenv[name] = arg

        oldenv = self.interp.env
        self.interp.env = newenv
        try:
            self.interp.visit(self.statements)
            result = None
        except ReturnException as e:
            result = e.value
        finally:
            self.interp.env = oldenv
        return result

    def bind(self, instance):
        env = self.env.new_child()
        env['this'] = instance
        return LoxFunction(self.interp, self.parameters, self.statements, env)

class LoxClass:
    def __init__(self, name, superclass, methods):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self):
        return self.name

    def __call__(self, *args):
        this = LoxInstance(self)
        init = self.find_method('init')
        if init:
            init.bind(this)(*args)
        return this

    def find_method(self, name):
        return self.methods.get(name)

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.data = { }

    def __str__(self):
        return self.klass.name + " instance"
    
    def get(self, name):
        if name in self.data:
            return self.data[name]
        method = self.klass.find_method(name)
        if not method:
            raise RuntimeError(f'Undefined property {name}')
        return method.bind(self)

    def set(self, name, value):
        self.data[name] = value
        
class LoxInterpreter(NodeVisitor):
    def __init__(self):
        self.env = ChainMap()
        self.localmap = { }

    # High-level entry point
    def interpret(self, node):
        loxresolve.resolve(node, self.env, self.localmap)
        self.visit(node)
        
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
        return self.env.maps[self.localmap[id(node)]][node.name]
        
    def visit_Call(self, node):
        callee = self.visit(node.func)
        if not callable(callee):
            raise RuntimeError(f'{callee} is not callable')
        
        args = [ self.visit(arg) for arg in node.arguments ]
        return callee(*args)
        
    def visit_Print(self, node):
        print(self.visit(node.value))

    def visit_ExprStmt(self, node):
        self.visit(node.value)
        
    def visit_VarDeclaration(self, node):
        if node.initializer:
            initializer = self.visit(node.initializer)
        else:
            initializer = None
        self.env[node.name] = initializer

    def visit_FuncDeclaration(self, node):
        func = LoxFunction(self, node.parameters, node.statements, self.env)
        self.env[node.name] = func
        
    def visit_Assign(self, node):
        value = self.visit(node.value)
        self.env.maps[self.localmap[id(node)]][node.name] = value
        
    def visit_IfStmt(self, node):
        test = self.visit(node.test)
        if _is_truthy(test):
            self.visit(node.consequence)
        elif node.alternative:
            self.visit(node.alternative)

    def visit_WhileStmt(self, node):
        while _is_truthy(self.visit(node.test)):
            self.visit(node.body)

    def visit_Return(self, node):
        raise ReturnException(self.visit(node.value))

    def visit_ClassDeclaration(self, node):
        methods = { }
        for meth in node.methods:
            methods[meth.name] = LoxFunction(self, meth.parameters, meth.statements, self.env)
        cls = LoxClass(node.name, None, methods)
        self.env[node.name] = cls
        
    def visit_Get(self, node):
        obj = self.visit(node.object)
        if isinstance(obj, LoxInstance):
            return obj.get(node.name)
        else:
            raise RuntimeError("Only instances have properties")

    def visit_Set(self, node):
        obj = self.visit(node.object)
        val = self.visit(node.value)
        if isinstance(obj, LoxInstance):
            obj.set(node.name, val)
            return val
        else:
            raise RuntimeError("Only instances have fields")

    def visit_This(self, node):
        return self.env.maps[self.localmap[id(node)]]['this']
        

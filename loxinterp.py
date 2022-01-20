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

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class LoxExit(BaseException):
    pass

class LoxCallError(Exception):
    pass

class LoxAttributeError(Exception):
    pass

class LoxFunction:
    def __init__(self, node, env):
        self.node = node
        self.env = env

    def __call__(self, interp, *args):
        if len(args) != len(self.node.parameters):
            raise LoxCallError(f"Expected {len(self.node.parameters)} arguments")
        newenv = self.env.new_child()
        for name, arg in zip(self.node.parameters, args):
            newenv[name] = arg

        oldenv = interp.env
        interp.env = newenv
        try:
            interp.visit(self.node.statements)
            result = None
        except ReturnException as e:
            result = e.value
        finally:
            interp.env = oldenv
        return result

    def bind(self, instance):
        env = self.env.new_child()
        env['this'] = instance
        return LoxFunction(self.node, env)

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
        meth = self.methods.get(name)
        if meth is None and self.superclass:
            return self.superclass.find_method(name)
        return meth

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
            raise LoxAttributeError(f'Undefined property {name}')
        return method.bind(self)

    def set(self, name, value):
        self.data[name] = value
        
class LoxInterpreter(NodeVisitor):
    def __init__(self, context):
        self.context = context
        self.env = ChainMap()
        self.resolve_env = ChainMap()
        self.localmap = { }

    def error(self, position, message):
        self.context.error(position, message)
        raise LoxExit()
    
    def _check_numeric_operands(self, node, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return True
        else:
            self.error(node, f"{node.op} operands must be numbers")

    def _check_numeric_operand(self, node, value):
        if isinstance(value, float):
            return True
        else:
            self.error(node, f"{node.op} operand must be a number")
        
    # High-level entry point
    def interpret(self, node):
        try:
            loxresolve.resolve(node, self.resolve_env, self)
            if not self.context.have_errors:
                self.visit(node)
        except LoxExit as e:
            pass
        
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
            (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(node, left, right)
            return left + right
        elif node.op == '-':
            self._check_numeric_operands(node, left, right)
            return left - right
        elif node.op == '*':
            self._check_numeric_operands(node, left, right)            
            return left * right
        elif node.op == '/':
            self._check_numeric_operands(node, left, right)            
            return left / right
        elif node.op == '==':
            return left == right
        elif node.op == '<':
            self._check_numeric_operands(node, left, right)            
            return left < right
        elif node.op == '>':
            self._check_numeric_operands(node, left, right)            
            return left > right
        elif node.op == '<=':
            self._check_numeric_operands(node, left, right)            
            return left <= right
        elif node.op == '>=':
            self._check_numeric_operands(node, left, right)            
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
            self._check_numeric_operand(node, operand)
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
            self.error(node.func, f'{self.context.find_source(node.func)!r} is not callable')
        
        args = [ self.visit(arg) for arg in node.arguments ]
        try:
            return callee(self, *args)
        except LoxCallError as err:
            self.error(node.func, str(err))
        
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
        func = LoxFunction(node, self.env)
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
        if node.superclass:
            superclass = self.visit(node.superclass)
            env = self.env.new_child()
            env['super'] = superclass
        else:
            superclass = None
            env = self.env
        methods = { }
        for meth in node.methods:
            methods[meth.name] = LoxFunction(meth, env)
        cls = LoxClass(node.name, superclass, methods)
        self.env[node.name] = cls
        
    def visit_Get(self, node):
        obj = self.visit(node.object)
        if isinstance(obj, LoxInstance):
            try:
                return obj.get(node.name)
            except LoxAttributeError as err:
                self.error(node.object, str(err))
        else:
            self.error(node.object, f'{self.context.find_source(node.object)!r} is not an instance')

    def visit_Set(self, node):
        obj = self.visit(node.object)
        val = self.visit(node.value)
        if isinstance(obj, LoxInstance):
            obj.set(node.name, val)
            return val
        else:
            self.error(node.object, f'{self.context.find_source(node.object)!r} is not an instance')

    def visit_This(self, node):
        return self.env.maps[self.localmap[id(node)]]['this']

    def visit_Super(self, node):
        distance = self.localmap[id(node)]
        superclass = self.env.maps[distance]['super']
        this = self.env.maps[distance-1]['this']
        method = superclass.find_method(node.name)
        if not method:
            self.error(node.object, f'Undefined property {node.name!r}')
        return method.bind(this)

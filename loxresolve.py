# Variable resolver
#
# Walks the AST to determine the proper scope for each variable reference.
#
# TODO: Could add more error handling. Better handling of error messages.

from loxast import *
from collections import ChainMap

class ResolveError(Exception):
    pass

def _resolve_name(name, env:ChainMap):
    for n, e in enumerate(env.maps):
        if name in e:
            if not e[name]:
                raise ResolveError("Can't reference a variable in its own initialization")
            else:
                return n
    raise ResolveError(f'{name} is not defined')

def resolve(node, env:ChainMap, interp):
    if isinstance(node, Variable):
        try:
            interp.localmap[id(node)] = _resolve_name(node.name, env)
        except ResolveError as err:
            interp.context.error(node, str(err))
        
    elif isinstance(node, VarDeclaration):
        env[node.name] = False
        if node.initializer:
            resolve(node.initializer, env, interp)
        env[node.name] = True

    elif isinstance(node, Assign):
        resolve(node.value, env, interp)
        try:
            interp.localmap[id(node)] = _resolve_name(node.name, env)
        except ResolveError as err:
            interp.context.error(node, str(err))
        
    elif isinstance(node, FuncDeclaration):
        env[node.name] = True
        childenv = env.new_child()
        childenv['fun'] = True
        for p in node.parameters:
            childenv[p] = len(childenv)
        resolve(node.statements, childenv, interp)

    elif isinstance(node, ClassDeclaration):
        env[node.name] = True        
        if node.superclass:
            if node.superclass.name == node.name:
                interp.context.error(node, "A class can't inherit from itself")
            resolve(node.superclass, env, interp)
            env = env.new_child()
            env['super'] = True
        env = env.new_child()
        env['this'] = True
        for meth in node.methods:
            resolve(meth, env, interp)
        
    elif isinstance(node, Literal):
        pass

    elif isinstance(node, (Binary, Logical)):
        resolve(node.left, env, interp)
        resolve(node.right, env, interp)

    elif isinstance(node, Unary):
        resolve(node.operand, env, interp)

    elif isinstance(node, Call):
        resolve(node.func, env, interp)
        for arg in node.arguments:
            resolve(arg, env, interp)

    elif isinstance(node, (Grouping, Print, ExprStmt)):
        resolve(node.value, env, interp)

    elif isinstance(node, Return):
        resolve(node.value, env, interp)
        if 'fun' not in env:
            interp.context.error(node, 'return used outside of a function')
        
    elif isinstance(node, IfStmt):
        resolve(node.test, env, interp)
        resolve(node.consequence, env, interp)
        if (node.alternative):
            resolve(node.alternative, env, interp)

    elif isinstance(node, WhileStmt):
        resolve(node.test, env, interp)
        resolve(node.body, env, interp)

    elif isinstance(node, Statements):
        newenv = env.new_child()
        for stmt in node.statements:
            resolve(stmt, newenv, interp)

    elif isinstance(node, Get):
        resolve(node.object, env, interp)

    elif isinstance(node, Set):
        resolve(node.object, env, interp)
        resolve(node.value, env, interp)

    elif isinstance(node, This):
        if 'this' in env:
            interp.localmap[id(node)] = _resolve_name('this', env)
        else:
            interp.context.error(node, "'this' used outside of a class")

    elif isinstance(node, Super):
        if 'super' in env:
            interp.localmap[id(node)] = _resolve_name('super', env)
        else:
            interp.context.error(node, "'super' used outside of a class")

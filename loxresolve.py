# Variable resolver
#
# Walks the AST to determine the proper scope for each variable reference.
#
# TODO: Could add more error handling. Better handling of error messages.

from loxast import *
from collections import ChainMap

def _resolve_name(name, env:ChainMap):
    for n, e in enumerate(env.maps):
        if name in e:
            if not e[name]:
                raise TypeError("Can't reference a variable in its own initialization")
            else:
                return n
    raise RuntimeError(f'{name} is not defined')

def resolve(node, env:ChainMap, localmap:dict):
    if isinstance(node, Variable):
        localmap[id(node)] = _resolve_name(node.name, env)
        
    elif isinstance(node, VarDeclaration):
        env[node.name] = False
        if node.initializer:
            resolve(node.initializer, env, localmap)
        env[node.name] = True

    elif isinstance(node, Assign):
        resolve(node.value, env, localmap)
        localmap[id(node)] = _resolve_name(node.name, env)
        
    elif isinstance(node, FuncDeclaration):
        env[node.name] = True
        childenv = env.new_child()
        for p in node.parameters:
            childenv[p] = len(childenv)
        resolve(node.statements, childenv, localmap)

    elif isinstance(node, Literal):
        pass

    elif isinstance(node, (Binary, Logical)):
        resolve(node.left, env, localmap)
        resolve(node.right, env, localmap)

    elif isinstance(node, Unary):
        resolve(node.operand, env, localmap)

    elif isinstance(node, Call):
        resolve(node.func, env, localmap)
        for arg in node.arguments:
            resolve(arg, env, localmap)

    elif isinstance(node, (Grouping, Print, Return, ExprStmt)):
        resolve(node.value, env, localmap)

    elif isinstance(node, IfStmt):
        resolve(node.test, env, localmap)
        resolve(node.consequence, env, localmap)
        if (node.alternative):
            resolve(node.alternative, env, localmap)

    elif isinstance(node, WhileStmt):
        resolve(node.test, env, localmap)
        resolve(node.body, env, localmap)

    elif isinstance(node, Statements):
        newenv = env.new_child()
        for stmt in node.statements:
            resolve(stmt, newenv, localmap)

    
        

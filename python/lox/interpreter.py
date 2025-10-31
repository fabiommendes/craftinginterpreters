from functools import singledispatch

from lox.ast import *
from lox import env
from lox.tokens import LiteralValue
from lox.errors import LoxRuntimeError
from lox.runtime import LoxCallable, NativeFunction, LoxFunction, LoxReturn, LoxClass, LoxInstance

type Value = LiteralValue | NativeFunction | LoxFunction | LoxClass | LoxInstance

class Env(env.Env[Value]):
    ...

@singledispatch
def eval(expr: Expr, env: Env) -> Value:
    msg = f"cannot eval {expr.__class__.__name__} objects"
    raise TypeError(msg)

@eval.register
def _(expr: Literal, env: Env) -> Value:
    return expr.value

@eval.register
def _(expr: Grouping, env: Env) -> Value:
    return eval(expr.expression, env)

@eval.register
def _(expr: Unary, env: Env) -> Value:
    right = eval(expr.right, env)

    match expr.operator.type :
        case "MINUS":
            return -as_number_operand(expr.operator, right)
        case "BANG":
            return not is_truthy(right)
        case op:
            assert False, f"unhandled operator {op}"

@eval.register
def _(expr: Binary, env: Env) -> Value:
    left = eval(expr.left, env)
    right = eval(expr.right, env)

    match expr.operator.type :
        case "MINUS":
            check_number_operands(expr.operator, left, right)
            return left - right
        case "SLASH":
            check_number_operands(expr.operator, left, right)
            return divide(left, right)
        case "STAR":
            check_number_operands(expr.operator, left, right)
            return left * right
        case "PLUS":
            if type(left) == type(right) and type(left) in (float, str):
                return left + right
            msg = "Operands must be two numbers or two strings."
            raise LoxRuntimeError(msg, expr.operator)
        case "GREATER":
            check_number_operands(expr.operator, left, right)
            return left > right
        case "GREATER_EQUAL":
            check_number_operands(expr.operator, left, right)
            return left >= right
        case "LESS":
            check_number_operands(expr.operator, left, right)
            return left < right
        case "LESS_EQUAL":
            check_number_operands(expr.operator, left, right)
            return left <= right
        case "BANG_EQUAL":
            return not is_equal(left, right)
        case "EQUAL_EQUAL":
            return is_equal(left, right)
        case op:
            assert False, f"unhandled operator {op}"

@eval.register
def _(expr: Variable, env: Env) -> Value:
    try:
        return env.get_at(expr.depth, expr.name.lexeme)
    except NameError as error:
        raise LoxRuntimeError(f"Undefined variable '{error}'.", expr.name)

@eval.register
def _(expr: Assign, env: Env) -> Value:
    value = eval(expr.value, env)
    try:
        env.assign_at(expr.depth, expr.name.lexeme, value)
    except NameError as error:
        raise LoxRuntimeError(f"Undefined variable '{error}'.", expr.name)
    return value

@eval.register
def _(expr: Logical, env: Env) -> Value:
    left = eval(expr.left, env)
    match (expr.operator.type, is_truthy(left)):
        case ("OR", True) | ("AND", False):
            return left
    return eval(expr.right, env)

@eval.register
def _(expr: Call, env: Env) -> Value:
    callee = eval(expr.callee, env)
    arguments = [eval(arg, env) for arg in expr.arguments]
    if not isinstance(callee, LoxCallable):
        msg = "Can only call functions and classes."
        raise LoxRuntimeError(msg, expr.paren)
    if len(arguments) != callee.arity:
        msg = f"Expected {callee.arity} arguments but got {len(arguments)}."
        raise LoxRuntimeError(msg, expr.paren)
    return callee.call(env, arguments)

@eval.register
def _(expr: Get, env: Env) -> Value:
    obj = eval(expr.object, env)
    if isinstance(obj, LoxInstance):
        return obj.get(expr.name)
    raise LoxRuntimeError("Only instances have properties.", expr.name)

@eval.register
def _(expr: Set, env: Env) -> Value:
    obj = eval(expr.object, env)
    if not isinstance(obj, LoxInstance):
        raise LoxRuntimeError("Only instances have fields.", expr.name)
    value = eval(expr.value, env)
    obj.set(expr.name, value)
    return value

@eval.register
def _(expr: This, env: Env) -> Value:
    try:
        return env.get_at(expr.depth, "this")
    except NameError as error:
        raise LoxRuntimeError(f"Undefined variable '{error}'.", expr.keyword)

@eval.register
def _(expr: Super, env: Env) -> Value:
    superclass = env.get_at(expr.depth, "super")
    instance = env.get_at(expr.depth - 1, "this")
    method = superclass.find_method(expr.method.lexeme)
    if method is None:
        msg = f"Undefined property '{expr.method.lexeme}'."
        raise LoxRuntimeError(msg, expr.method)
    return method.bind(instance)

#
# Exec
#
@singledispatch
def exec(stmt: Stmt, env: Env) -> None:
    msg = f"exec not implemented for {type(stmt)}"
    raise TypeError(msg)

@exec.register
def _(stmt: Program, env: Env) -> None:
    for child in stmt.statements:
        exec(child, env)

@exec.register
def _(stmt: Expression, env: Env) -> None:
    eval(stmt.expression, env)

@exec.register
def _(stmt: Print, env: Env) -> None:
    value = eval(stmt.expression, env)
    print(stringify(value))

@exec.register
def _(stmt: Var, env: Env) -> None:
    value = eval(stmt.initializer, env)
    env[stmt.name.lexeme] = value

@exec.register
def _(stmt: Block, env: Env) -> None:
    inner_env = env.push()
    for statement in stmt.statements:
        exec(statement, inner_env)

@exec.register
def _(stmt: If, env: Env) -> None:
    condition = eval(stmt.condition, env)
    if is_truthy(condition):
        exec(stmt.then_branch, env)
    elif stmt.else_branch is not None:
        exec(stmt.else_branch, env)

@exec.register
def _(stmt: While, env: Env) -> None:
    while is_truthy(eval(stmt.condition, env)):
        exec(stmt.body, env)

@exec.register
def _(stmt: Function, env: Env):
    function = LoxFunction(stmt, env)
    env[stmt.name.lexeme] = function

@exec.register
def _(stmt: Return, env: Env):
    value = None
    if stmt.value is not None:
        value = eval(stmt.value, env)
    raise LoxReturn(value)

@exec.register
def _(stmt: Class, env: Env) -> None:
    superclass = None
    if stmt.superclass is not None:
        superclass = eval(stmt.superclass, env)
        if not isinstance(superclass, LoxClass):
            msg = "Superclass must be a class."
            raise LoxRuntimeError(msg, stmt.superclass.name)

    klass = LoxClass(stmt.name.lexeme, superclass)

    outer_env = env
    if superclass is not None:
        env = env.push()
        env["super"] = superclass
        
    for method in stmt.methods:
        is_initializer = method.name.lexeme == "init"
        function = LoxFunction(method, env, is_initializer)
        klass.methods[method.name.lexeme] = function
    outer_env[stmt.name.lexeme] = klass

#
# Utility functions
#
def is_truthy(obj: Value) -> bool:
    if obj is None or obj is False:
        return False
    return True

def is_equal(a, b):
    return type(a) == type(b) and a == b

def as_number_operand(operator: Token, operand: Value) -> float:
    if isinstance(operand, float):
        return operand
    raise LoxRuntimeError("Operand must be a number.", operator)

def check_number_operands(operator: Token, left: Value, right: Value) -> None:
    if isinstance(left, float) and isinstance(right, float):
        return
    raise LoxRuntimeError("Operands must be numbers.", operator)

def stringify(value: Value) -> str:
    if value is None:
        return "nil"
    elif isinstance(value, float):
        return str(value).removesuffix(".0")
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return str(value)
    
def divide(left: float, right: float) -> float:
    if right != 0:
        return left / right
    if left == 0:
        return float("nan")
    elif left > 0:
        return float("inf")
    else:
        return float("-inf")
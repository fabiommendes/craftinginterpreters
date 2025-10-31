> You are my creator, but I am your master; Obey!
>
> <cite>Mary Shelley, <em>Frankenstein</em></cite>

If you want to properly set the mood for this chapter, try to conjure up a
thunderstorm, one of those swirling tempests that likes to yank open shutters at
the climax of the story. Maybe toss in a few bolts of lightning. In this
chapter, our interpreter will take breath, open its eyes, and execute some code.

<span name="spooky"></span>

<img src="image/evaluating-expressions/lightning.png" alt="A bolt of lightning strikes a Victorian mansion. Spooky!" />

<aside name="spooky">

A decrepit Victorian mansion is optional, but adds to the ambiance.

</aside>

There are all manner of ways that language implementations make a computer do
what the user's source code commands. They can compile it to machine code,
translate it to another high-level language, or reduce it to some bytecode
format for a virtual machine to run. For our first interpreter, though, we are
going to take the simplest, shortest path and execute the syntax tree itself.

Right now, our parser only supports expressions. So, to "execute" code, we will
evaluate an expression and produce a value. For each kind of expression syntax
we can parse -- literal, operator, etc. -- we need a corresponding chunk of code
that knows how to evaluate that tree and produce a result. That raises two
questions:

1. What kinds of values do we produce?

2. How do we organize those chunks of code?

Taking them on one at a time...

## Representing Values

In Lox, <span name="value">values</span> are created by literals, computed by
expressions, and stored in variables. The user sees these as _Lox_ objects, but
they are implemented in the underlying language our interpreter is written in.
That means bridging the lands of Lox's and Python's types. Both languages have
dynamic and somewhat strict types, but this category is very broad and we often
need to adjust for small differences in behavior between both languages.

<aside name="value">

Here, I'm using "value" and "object" pretty much interchangeably.

Later in the C interpreter we'll make a slight distinction between them, but
that's mostly to have unique terms for two different corners of the
implementation -- in-place versus heap-allocated data. From the user's
perspective, the terms are synonymous.

</aside>

In places in the interpreter where we need to store a Lox value, we can use
Python's `Any` from the `typing` module as the type. `Any`, as the name implies,
declares a variable that can hold any type. There are many Python types that
cannot be produced by Lox code, and we could be more precise by declaring a
custom type that narrows exactly to the list of supported values. In this book,
however, I prefer to keep things simple and accessible and avoid more advanced
Python typing features.

<table>
<thead>
<tr>
  <td>Lox type</td>
  <td>Python representation</td>
</tr>
</thead>
<tbody>
<tr>
  <td>Any Lox value</td>
  <td>Any</td>
</tr>
<tr>
  <td><code>nil</code></td>
  <td><code>None</code></td>
</tr>
<tr>
  <td>Boolean</td>
  <td>bool</td>
</tr>
<tr>
  <td>number</td>
  <td>float</td>
</tr>
<tr>
  <td>string</td>
  <td>str</td>
</tr>
</tbody>
</table>

Given a value, we can determine if the runtime value is a number or a string or
whatever using Python's built-in `isinstance` function. In other words, the
<span name="python">Python</span>'s own object representation conveniently gives
us everything we need to implement Lox's built-in types. We'll have to do a
little more work later when we add Lox's notions of functions, classes, and
instances, but Python's own primitives are sufficient for the types we need
right now.

<aside name="python">

Another thing we need to do with values is manage their memory, and Python does
that too. A handy object representation and a really nice garbage collector are
the main reasons we're writing our first interpreter in Python.

</aside>

## Evaluating Expressions

Next, we need blobs of code to implement the evaluation logic for each kind of
expression we can parse. We could stuff that code into the syntax tree classes
in something like an `interpret()` method. In effect, we could tell each syntax
tree node, "Interpret thyself". This is the Gang of Four's [Interpreter design
pattern][]. It's a neat pattern, but like I mentioned earlier, it gets messy if
we jam all sorts of logic into the tree classes.

[interpreter design pattern]: https://en.wikipedia.org/wiki/Interpreter_pattern

Instead, we're going to reuse our groovy [Single dispatch][] pattern. In the
previous chapter, we created `pretty()` single dispatwch function. It took in a
syntax tree and recursively traversed it, building up a string which it
ultimately returned. That's almost exactly what a real interpreter does, except
instead of concatenating strings, it computes values.

[single dispatch]: representing-code.html#single-dispatch

We start declaring a new singledispatch function `eval()`.

```python
# lox/interpreter.py
from functools import singledispatch
from lox.ast import *
from lox.tokens import TokenType, LiteralValue

@singledispatch
def eval(expr: Expr, env: Env) -> Value:
    msg = f"cannot eval {expr.__class__.__name__} objects"
    raise TypeError(msg)
```

<aside name="eval">

We call it `eval` to honour a tradition in many dynamic languages (including
Python) that have a function named like so that dynamically interpret source
strings of that language.

</aside>

The function `eval` receive a second parameter, `env`, which represents the
_current execution environment_ -- which is an object that tracks the state of
our program as it runs. Right now, we don't have any state to track, so we can
just pass in an empty dict (or anything else) when we call `eval()`. Later, when
we add variables and functions, we'll define a proper `Env` class and pass in an
instance of that.

`Value` is a type alias that represents any Lox value. We will use Python
dynamism to represent Lox values directly using Python types. For now, we can
only produce literals, so `Value` is just `LiteralValue`.

We need to declare those types explicitly:

```python
# lox/interpreter.py after imports
Value = LiteralValue
Env = dict[str, Value]
```

The return type of the `eval` method will be `Value`, that represents the
acceptable Python representations of Lox values. We need to define
implementations for each of the four expression tree classes our parser
produces. We'll start with the simplest...

### Evaluating literals

The leaves of an expression tree -- the atomic bits of syntax that all other
expressions are composed of -- are <span name="leaf">literals</span>. Literals
are almost values already, but the distinction is important. A literal is a _bit
of syntax_ that produces a value. A literal always appears somewhere in the
user's source code. Lots of values are produced by computation and don't exist
anywhere in the code itself. Those aren't literals. A literal comes from the
parser's domain. Values are an interpreter concept, part of the runtime's world.

<aside name="leaf">

In the [next chapter][vars], when we implement variables, we'll add identifier
expressions, which are also leaf nodes.

[vars]: statements-and-state.html

</aside>

So, much like we converted a literal _token_ into a literal _syntax tree node_
in the parser, now we convert the literal tree node into a runtime value. That
turns out to be trivial.

```python
# lox/interpreter.py after eval()
@eval.register
def _(expr: Literal, env: Env) -> Value:
    return expr.value
```

We eagerly produced the runtime value way back during scanning and stuffed it in
the token. The parser took that value and stuck it in the literal tree node, so
to evaluate a literal, we simply pull it back out.

### Evaluating parentheses

The next simplest node to evaluate is grouping -- the node you get as a result
of using explicit parentheses in an expression.

```python
# lox/interpreter.py after eval()
@eval.register
def _(expr: Grouping, env: Env) -> Value:
    return eval(expr.expression, env)
```

A <span name="grouping">grouping</span> node has a reference to an inner node
for the expression contained inside the parentheses. To evaluate the grouping
expression itself, we recursively evaluate that subexpression and return it.

<aside name="grouping">

Some parsers don't define tree nodes for parentheses. Instead, when parsing a
parenthesized expression, they simply return the node for the inner expression.
We do create a node for parentheses in Lox because we'll need it later to
correctly handle the left-hand sides of assignment expressions.

</aside>

### Evaluating unary expressions

Like grouping, unary expressions have a single subexpression that we must
evaluate first. The difference is that the unary expression itself does a little
work afterwards.

```python
# lox/interpreter.py after eval()
@eval.register
def _(expr: Unary, env: Env) -> Value:
    right = eval(expr.right, env)
    match expr.operator.type :
        case "MINUS":
            return -right
        case op:
            assert False, f"unhandled operator {op}"
```

First, we evaluate the operand expression. Then we apply the unary operator
itself to the result of that. There are two different unary expressions,
identified by the type of the operator token.

The fallback case with the `assert` is a sanity check to ensure the interpreter
shouts loudly if we ever encounter an unexpected operator. This should not be
possible if the parser is working correctly, but we are humans and make
mistakes.

You can start to see how evaluation recursively traverses the tree. We can't
evaluate the unary operator itself until after we evaluate its operand
subexpression. That means our interpreter is doing a **post-order traversal** --
each node evaluates its children before doing its own work.

The other unary operator is logical not.

```python
# lox/interpreter.py at eval(Unary) match/case
    ...
    case "BANG":
        return not is_truthy(right)
    ...
```

The implementation is simple, but what is this "truthy" thing about? We need to
make a little side trip to one of the great questions of Western philosophy:
_What is truth?_

### Truthiness and falsiness

OK, maybe we're not going to really get into the universal question, but at
least inside the world of Lox, we need to decide what happens when you use
something other than `true` or `false` in a logic operation like `!` or any
other place where a Boolean is expected.

We _could_ just say it's an error because we don't roll with implicit
conversions, but most dynamically typed languages aren't that ascetic. Instead,
they take the universe of values of all types and partition them into two sets,
one of which they define to be "true", or "truthful", or (my favorite) "truthy",
and the rest which are "false" or "falsey". This partitioning is somewhat
arbitrary and gets <span name="weird">weird</span> in a few languages.

<aside name="weird" class="bottom">

In JavaScript, strings are truthy, but empty strings are not. Arrays are truthy
but empty arrays are... also truthy. The number `0` is falsey, but the _string_
`"0"` is truthy.

In Python, empty strings are falsey like in JS, but other empty sequences are
falsey too.

In PHP, both the number `0` and the string `"0"` are falsey. Most other
non-empty strings are truthy.

Get all that?

</aside>

Lox follows Ruby's simple rule: `false` and `nil` are falsey, and everything
else is truthy. We implement that like so:

```python
# lox/interpreter.py after all eval() implementations
def is_truthy(obj: Any) -> bool:
    if obj is None or obj is False:
        return False
    return True
```

### Evaluating binary operators

On to the last expression tree class, binary operators. There's a handful of
them, and we'll start with the arithmetic ones.

```python
# lox/interpreter.py after eval()
@eval.register
def _(expr: Binary, env: Env) -> Value:
    left = eval(expr.left, env)
    right = eval(expr.right, env)

    match expr.operator.type :
        case "PLUS":
            return left + right
        case "MINUS":
            return left - right
        case "SLASH":
            return divide(left, right)
        case "STAR":
            return left * right
        case op:
            assert False, f"unhandled operator {op}"
```

Division uses a helper function to handle division by zero consistently:

```python
def divide(left: float, right: float) -> float:
    if right != 0:
        return left / right
    if left == 0:
        return float("nan")
    elif left > 0:
        return float("inf")
    else:
        return float("-inf")
```

Did you notice we pinned down a subtle corner of the language semantics here? In
a binary expression, we evaluate the operands in left-to-right order. If those
operands have side effects, that choice is user visible, so this isn't simply an
implementation detail.

If we want our two interpreters to be consistent (hint: we do), we'll need to
make sure clox does the same thing.

</aside>

I think you can figure out what's going on here. The main difference from the
unary negation operator is that we have two operands to evaluate.

<aside name="plus">

Lox, just like Python, Java, JavaScript, and many other languages, uses the `+`
operator for both adding numbers and concatenating strings. That is why we
simply added to two operands in the Python implementation.

We could have defined an operator specifically for string concatenation. That's
what Perl (`.`), Lua (`..`), Smalltalk (`,`), Haskell (`++`), and others do.

I thought it would make Lox a little more approachable to use the same syntax as
Java, JavaScript, Python, and others. This means that the `+` operator is
**overloaded** to support both adding numbers and concatenating strings. Even in
languages that don't use `+` for strings, they still often overload it for
adding both integers and floating-point numbers.

</aside>

Next up are the comparison operators.

```python
# lox/interpreter.py at eval(Binary) match/case
    ...
    case "GREATER":
        return left > right
    case "GREATER_EQUAL":
        return left >= right
    case "LESS":
        return left < right
    case "LESS_EQUAL":
        return left <= right
    ...
```

They are basically the same as arithmetic. The only difference is that where the
arithmetic operators produce a value whose type is the same as the operands
(numbers or strings), the comparison operators always produce a Boolean.

The last pair of operators are equality.

```python
# lox/interpreter.py at eval(Binary) match/case
    ...
    case "BANG_EQUAL":
        return not is_equal(left, right)
    case "EQUAL_EQUAL":
        return is_equal(left, right)
    ...
```

Unlike the comparison operators which require numbers, the equality operators
support operands of any type, even mixed ones. You can't ask Lox if 3 is _less_
than `"three"`, but you can ask if it <span name="equal">_is_equal_</span> to
it.

<aside name="equal">

Spoiler alert: it's not.

</aside>

Like truthiness, the equality logic is hoisted out into a separate method.

```python
# lox/interpreter.py at top-level
def is_equal(a, b):
    return type(a) == type(b) and a == b
```

This is one of those corners where the details of how we represent Lox objects
in terms of Python matter. We need to correctly implement _Lox's_ notion of
equality, which may be different from Python's.

Fortunately, the two are pretty similar. Lox doesn't do implicit conversions in
equality and Python does not either. The only corner cases concerns with
comparisons between numbers and Booleans. Python's `bool` is a subclass of
`int`, which can compare with `float`, unlike in Lox.

<aside name="nan">

What do you expect this to evaluate to:

```lox
(0 / 0) == (0 / 0)
```

According to [IEEE 754][], which specifies the behavior of double-precision
numbers, dividing a zero by zero gives you the special **NaN** ("not a number")
value. Strangely enough, NaN is _not_ equal to itself.

In Python, the `==` operator on floats preserves that behavior, but division by
zero raises an exception. Lox original Java implementation Lox uses
Double.equal() for comparison which makes NaNs equal to themselves. The C
implementation, however, follows IEEE 754. These kinds of subtle
incompatibilities occupy a dismaying fraction of language implementers' lives.

[ieee 754]: https://en.wikipedia.org/wiki/IEEE_754

</aside>

And that's it! That's all the code we need to correctly interpret a valid Lox
expression. But what about an _invalid_ one? In particular, what happens when a
subexpression evaluates to an object of the wrong type for the operation being
performed?

## Runtime Errors

I was cavalier about jamming casts in whenever a subexpression produces an
Object and the operator requires it to be a number or a string. Those casts can
fail. Even though the user's code is erroneous, if we want to make a <span
name="fail">usable</span> language, we are responsible for handling that error
gracefully.

<aside name="fail">

We could simply not detect or report a type error at all. This is what C does if
you cast a pointer to some type that doesn't match the data that is actually
being pointed to. C gains flexibility and speed by allowing that, but is also
famously dangerous. Once you misinterpret bits in memory, all bets are off.

Few modern languages accept unsafe operations like that. Instead, most are
**memory safe** and ensure -- through a combination of static and runtime checks
-- that a program can never incorrectly interpret the value stored in a piece of
memory.

</aside>

It's time for us to talk about **runtime errors**. I spilled a lot of ink in the
previous chapters talking about error handling, but those were all _syntax_ or
_static_ errors. Those are detected and reported before _any_ code is executed.
Runtime errors are failures that the language semantics demand we detect and
report while the program is running (hence the name).

Right now, if an operand is the wrong type for the operation being performed,
the Python interpreter will raise some exception like ValueError or TypeError.
That unwinds the whole stack and exits the application, vomiting a Python stack
trace onto the user. That's probably not what we want. The fact that Lox is
implemented in Python should be a detail hidden from the user. Instead, we want
them to understand that a _Lox_ runtime error occurred, and give them an error
message relevant to our language and their program.

The Python behavior does have one thing going for it, though. It correctly stops
executing any code when the error occurs. Let's say the user enters some
expression like:

```lox
2 * (3 / -"muffin")
```

You can't negate a <span name="muffin">muffin</span>, so we need to report a
runtime error at that inner `-` expression. That in turn means we can't evaluate
the `/` expression since it has no meaningful right operand. Likewise for the
`*`. So when a runtime error occurs deep in some expression, we need to escape
all the way out.

<aside name="muffin">

I don't know, man, _can_ you negate a muffin?

<img src="image/evaluating-expressions/muffin.png" alt="A muffin, negated." />

</aside>

We could print a runtime error and then abort the process and exit the
application entirely. That has a certain melodramatic flair. Sort of the
programming language interpreter equivalent of a mic drop.

Tempting as that is, we should probably do something a little less cataclysmic.
While a runtime error needs to stop evaluating the _expression_, it shouldn't
kill the _interpreter_. If a user is running the REPL and has a typo in a line
of code, they should still be able to keep the session going and enter more code
after that.

### Detecting runtime errors

Our tree-walk interpreter evaluates nested expressions using recursive method
calls, and we need to unwind out of all of those. Raising an exception in Python
is a fine way to accomplish that. However, instead of using Python's own type
conversion machinery, we'll define a Lox-specific one so that we can handle it
how we want.

Before we perform some operation, we check the object's type ourselves. So, for
unary `-`, we change the implementation:

```python
# lox/interpreter.py at eval(Unary) match/case
    ...
    case "MINUS":
        return -as_number_operand(expr.operator, right)
    ...
```

The code to check the operand is:

```python
# lox/interpreter.py at top-level
def as_number_operand(operator: Token, operand: Value) -> float:
    if isinstance(operand, float):
        return operand
    raise LoxRuntimeError("Operand must be a number.", operator)
```

When the check fails, it produces a LoxRuntimeError using information stored in
the token object

```python
# lox/interpreter.py at the top-level
from lox.tokens import Token
from lox.errors import LoxRuntimeError
```

We also need to define that exception class. It goes in the `lox.errors` module:

```python
# lox/errors.py
from lox.tokens import Token

class LoxRuntimeError(Exception):
    def __init__(self, message: str, token: Token):
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self) -> str:
        prefix =  f"[line {self.token.line}] "
        prefix += f"Runtime error at '{self.token.lexeme}'"
        return f"{prefix}: {self.message}"
```

Unlike the Python RuntimeError exception, our class tracks the token that
identifies where in the user's code the runtime error came from. As with static
errors, this helps the user know where to fix their code. Some errors cannot be
directly tied to a specific token, so we make that parameter optional.

We need similar checking for the binary operators. Since I promised you every
single line of code needed to implement the interpreters, I'll run through them
all.

Following the same logic, we can reimplent the binary operators to check their
operands before each operation.

Comparison operators:

```python
# lox/interpreter.py at eval(Binary) match/case
    ...
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
    ...
```

Arithmetic operators:

```python
# lox/interpreter.py at eval(Binary) match/case
    ...
    case "MINUS":
        check_number_operands(expr.operator, left, right)
        return left - right
    case "SLASH":
        check_number_operands(expr.operator, left, right)
        return divide(left, right)
    case "STAR":
        check_number_operands(expr.operator, left, right)
        return left * right
    ...
```

All of those rely on this validator, which is virtually the same as the unary
one:

```python
# lox/eval.py at top-level
def check_number_operands(operator: Token,
                          left: Value,
                          right: Value):
    if isinstance(left, float) and isinstance(right, float):
        return
    raise LoxRuntimeError("Operands must be numbers.", operator)
```

<aside name="operand">

Another subtle semantic choice: We evaluate _both_ operands before checking the
type of _either_. Imagine we have a function `say()` that prints its argument
then returns it. Using that, we write:

```lox
say("left") - say("right");
```

Our interpreter prints "left" and "right" before reporting the runtime error. We
could have instead specified that the left operand is checked before even
evaluating the right.

</aside>

The last remaining operator, the odd one out, is addition. Since `+` is
overloaded for numbers and strings we cannot reuse the same logic as the other
operators.

```python
# lox/interpreter.py at eval(Binary) match/case
    ...
    case "PLUS":
        if (type(left) == type(right) and
            type(left) in (float, str)):
            return left + right
        msg = "Operands must be two numbers or two strings."
        raise LoxRuntimeError(msg, expr.operator)
    ...
```

That gets us detecting runtime errors deep in the innards of the evaluator. The
errors are getting thrown. The next step is to write the code that catches them.
For that, we need to wire up `eval()` into the main Lox class that uses it.

## Hooking Up the Interpreter

The `eval` implementations are sort of the guts of our interpreter module, where
the real work happens. We modify our main module to eventually call `eval` and
handle any runtime errors that occur.

```python
# lox/__main__.py Lox method
def interpret(self, expression: Expr):
    try:
        value = eval(expression, self.environment)
        print(stringify(value))
    except LoxRuntimeError as error:
        print(error)
```

We must import some necessary functions and classes at the top of the file:

```python
# lox/__main__.py at the top-level
from lox.interpreter import eval, stringify, Value, Env
from lox.errors import LoxRuntimeError, LoxSyntaxError
from lox.ast import *
```

This takes in a syntax tree for an expression and evaluates it. If that
succeeds, `eval()` returns an object for the result value. `interpret()`
converts that to a string and shows it to the user. To convert a Lox value to a
string, we rely on:

```python
# lox/interpreter.py at stringify
def stringify(value: Value) -> str:
    if value is None:
        return "nil"
    elif isinstance(value, float):
        return str(value).removesuffix(".0")
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return str(value)
```

This is another of those pieces of code like `is_truthy()` that crosses the
membrane between the user's view of Lox objects and their internal
representation in Python.

It's pretty straightforward. Since Lox was designed to be familiar to someone
coming from Python, things like Strings look the same in both languages. The two
edge cases are `nil`, which we represent using Python's `None`, numbers and
booleans, which are represented in lowercase in Lox.

Lox uses double-precision numbers even for integer values. In that case, they
should print without a decimal point. Since Python has both floating point and
integer types, it wants you to know which one you're using. It tells you by
adding an explicit `.0` to integer-valued doubles. We don't care about that, so
we <span name="number">hack</span> it off the end.

<aside name="number">

Yet again, we take care of this edge case with numbers to ensure that pylox and
clox work the same. Handling weird corners of the language like this will drive
you crazy but is an important part of the job.

Users rely on these details -- either deliberately or inadvertently -- and if
the implementations aren't consistent, their program will break when they run it
on different interpreters.

</aside>

### Reporting runtime errors

If a runtime error is thrown while evaluating the expression, `interpret()`
catches it. This lets us report the error to the user and then gracefully
continue.

We need to hook it up to the `run()` method, which until now has just been
printing the syntax tree for the parsed expression. We replace that temporary
code with:

```python
# lox/__main__.py replace Lox.run()
def run(self, source: str):
    try:
        tokens = tokenize(source)
        ast = parse(tokens)
        value = eval(ast, self.environment)
        print(stringify(value))
    except LoxRuntimeError as error:
        self.report_error(error, code=70)
    except LoxSyntaxError as error:
        self.report_error(error, code=65)
```

Since the `eval()` function requires an environment parameter, we need to add an
`environment` field to the Lox class. For now, it can just be an empty
dictionary since we don't have any variables yet. We initialize it in the
constructor:

```python
# lox/__main__.py Lox method
def __init__(self, interactive: bool = False):
    self.environment = Env()
    self.interactive = interactive
```

Finally, we need to implement `report_error()`, which is responsible for showing
the runtime error to the user. If the user is running a Lox <span
name="repl">script from a file</span> and a runtime error occurs, we set an exit
code when the process quits to let the calling process know. Not everyone cares
about shell etiquette, but we do.

```python
# lox/__main__.py Lox method
def report_error(self, error: Exception, code: int):
    print(error)
    if not self.interactive:
        sys.exit(code)
```

<aside name="repl">

If the user is running the REPL, we don't care about propagating runtime or
syntax errors. After they are reported, we simply loop around and let them input
new code and keep going.

</aside>

We have an entire language pipeline now: scanning, parsing, and execution.
Congratulations, you now have your very own arithmetic calculator.

As you can see, the interpreter is pretty bare bones. But the Interpreter class
and the Visitor pattern we've set up today form the skeleton that later chapters
will stuff full of interesting guts -- variables, functions, etc. Right now, the
interpreter doesn't do very much, but it's alive!

<img src="image/evaluating-expressions/skeleton.png" alt="A skeleton waving hello." />

<div class="challenges">

## Challenges

1.  Allowing comparisons on types other than numbers could be useful. The
    operators might have a reasonable interpretation for strings. Even
    comparisons among mixed types, like `3 < "pancake"` could be handy to enable
    things like ordered collections of heterogeneous types. Or it could simply
    lead to bugs and confusion.

    Would you extend Lox to support comparing other types? If so, which pairs of
    types do you allow and how do you define their ordering? Justify your
    choices and compare them to other languages.

2.  Many languages define `+` such that if _either_ operand is a string, the
    other is converted to a string and the results are then concatenated. For
    example, `"scone" + 4` would yield `scone4`. Extend the code in
    `eval(Binary)` to support that.

3.  What happens right now if you divide a number by zero? What do you think
    should happen? Justify your choice. How do other languages you know handle
    division by zero, and why do they make the choices they do?

    Change the implementation in `eval(Binary)` to detect and report a runtime
    error for this case.

</div>

<div class="design-note">

## Design Note: Static and Dynamic Typing

Some languages, like Java, are statically typed which means type errors are
detected and reported at compile time before any code is run. Others, like Lox,
are dynamically typed and defer checking for type errors until runtime right
before an operation is attempted. We tend to consider this a black-and-white
choice, but there is actually a continuum between them.

It turns out even most statically typed languages do _some_ type checks at
runtime. The type system checks most type rules statically, but inserts runtime
checks in the generated code for other operations.

For example, in Java, the _static_ type system assumes a cast expression will
always safely succeed. After you cast some value, you can statically treat it as
the destination type and not get any compile errors. But downcasts can fail,
obviously. The only reason the static checker can presume that casts always
succeed without violating the language's soundness guarantees, is because the
cast is checked _at runtime_ and throws an exception on failure.

A more subtle example is [covariant arrays][] in Java and C#. The static
subtyping rules for arrays allow operations that are not sound. Consider:

[covariant arrays]:
  https://en.wikipedia.org/wiki/Covariance_and_contravariance_(computer_science)#Covariant_arrays_in_Java_and_C.23

```java
Object[] stuff = new Integer[1];
stuff[0] = "not an int!";
```

This code compiles without any errors. The first line upcasts the Integer array
and stores it in a variable of type Object array. The second line stores a
string in one of its cells. The Object array type statically allows that --
strings _are_ Objects -- but the actual Integer array that `stuff` refers to at
runtime should never have a string in it! To avoid that catastrophe, when you
store a value in an array, the JVM does a _runtime_ check to make sure it's an
allowed type. If not, it throws an ArrayStoreException.

Java could have avoided the need to check this at runtime by disallowing the
cast on the first line. It could make arrays _invariant_ such that an array of
Integers is _not_ an array of Objects. That's statically sound, but it prohibits
common and safe patterns of code that only read from arrays. Covariance is safe
if you never _write_ to the array. Those patterns were particularly important
for usability in Java 1.0 before it supported generics. James Gosling and the
other Java designers traded off a little static safety and performance -- those
array store checks take time -- in return for some flexibility.

There are few modern statically typed languages that don't make that trade-off
_somewhere_. Even Haskell will let you run code with non-exhaustive matches. If
you find yourself designing a statically typed language, keep in mind that you
can sometimes give users more flexibility without sacrificing _too_ many of the
benefits of static safety by deferring some type checks until runtime.

On the other hand, a key reason users choose statically typed languages is
because of the confidence the language gives them that certain kinds of errors
can _never_ occur when their program is run. Defer too many type checks until
runtime, and you erode that confidence.

</div>
````

"""Contains ~ATH's AST and data structure primitives for easier access."""
import operator
from functools import partialmethod


def isAthValue(obj):
    """True if an object is a number or string."""
    return isinstance(obj, (int, float, complex, str))


class SymbolError(Exception):
    """Raised when a symbol-specific exception occurs."""


class SymbolDeath(Exception):
    """Raised when a symbol dies."""


class AthExpr(object):
    """Base class of all ~ATH AST nodes."""
    __slots__ = ()

    def __eq__(self, othr):
        if isinstance(othr, self.__class__):
            self_attrs = {slot: getattr(self, slot) for slot in self.__slots__}
            othr_attrs = {slot: getattr(othr, slot) for slot in othr.__slots__}
            return self_attrs == othr_attrs
        return False

    def __hash__(self):
        return object.__hash__(self)

    def __repr__(self):
        attr_list = [repr(getattr(self, slot)) for slot in self.__slots__]
        attr_str = ', '.join(attr_list)
        return '{}({})'.format(self.__class__.__name__, attr_str)


class AthBuiltinFunction(AthExpr):
    """~ATH Builtin Function Wrappers."""
    __slots__ = ('name', 'func', 'argsmin', 'argsmax')

    def __init__(self, name, func, argsmin, argsmax=None):
        self.name = name
        self.func = func
        self.argsmin = argsmin
        self.argsmax = argsmin if argsmax is None else argsmax

    def __repr__(self):
        return '<~ATH Builtin Function {}>'.format(self.name)

    def pprint(self, level=0):
        return '{}({!r}, {}, {}, {})'.format(
            self.__class__.__name__,
            self.name,
            self.func.__name__,
            self.argsmin,
            self.argsmax,
            )

    def __call__(self, env, *args):
        alen = len(args)
        if self.argsmin <= alen and (self.argsmax < 0 or alen <= self.argsmax):
            return self.func(env, *args)
        else:
            raise TypeError


class AthSymbol(AthExpr):
    """~ATH Variable data structure."""
    __slots__ = ('alive', 'left', 'right')

    def __init__(self, alive=True, left=None, right=None):
        self.alive = alive
        if left is None:
            self.left = None
        else:
            self.assign_left(left)
        if right is None:
            self.right = None
        else:
            self.assign_right(right)

    def __repr__(self):
        if isinstance(self.right, AthFunction):
            rstr = '<AthFunction {}>'.format(self.right.name)
        else:
            rstr = repr(self.right)
        return '{}({}, {!r}, {})'.format(
            self.__class__.__name__,
            self.alive, self.left, rstr,
            )

    def cmpop(self, other, op):
        """Base function for comparison operators."""
        if not isAthValue(self.left):
            raise SymbolError('symbol left is not a value')
        if isinstance(other, AthSymbol):
            return AthSymbol(op(self.left, other.left))
        else:
            return AthSymbol(op(self.left, other), self.left, self.right)

    def unoop(self, op):
        """Base function for unary operators."""
        if not isAthValue(self.left):
            raise SymbolError('symbol left is not a value')
        return AthSymbol(left=op(self.left))

    def binop(self, other, op):
        """Base function for binary operators."""
        if not isAthValue(self.left):
            raise SymbolError('symbol left is not a value')
        if isinstance(other, AthSymbol):
            return AthSymbol(left=op(self.left, other.left))
        else:
            return AthSymbol(left=op(self.left, other), right=self.right)

    def reop(self, other, op):
        """Base function for reverse binary operators."""
        if not isAthValue(self.left):
            raise SymbolError('symbol left is not a value')
        return AthSymbol(left=op(other, self.left), right=self.right)

    def inop(self, other, op):
        """Base function for in-place binary operators."""
        if not isAthValue(self.left):
            raise SymbolError('symbol left is not a value')
        self.left = op(self.left, other)
        return self

    def __bool__(self):
        return self.alive

    __add__ = partialmethod(binop, op=operator.add)
    __radd__ = partialmethod(reop, op=operator.add)
    __iadd__ = partialmethod(inop, op=operator.add)

    __sub__ = partialmethod(binop, op=operator.sub)
    __rsub__ = partialmethod(reop, op=operator.sub)
    __isub__ = partialmethod(inop, op=operator.sub)

    __mul__ = partialmethod(binop, op=operator.mul)
    __rmul__ = partialmethod(reop, op=operator.mul)
    __imul__ = partialmethod(inop, op=operator.mul)

    __truediv__ = partialmethod(binop, op=operator.truediv)
    __rtruediv__ = partialmethod(reop, op=operator.truediv)
    __itruediv__ = partialmethod(inop, op=operator.truediv)

    __floordiv__ = partialmethod(binop, op=operator.floordiv)
    __rfloordiv__ = partialmethod(reop, op=operator.floordiv)
    __ifloordiv__ = partialmethod(inop, op=operator.floordiv)

    __mod__ = partialmethod(binop, op=operator.mod)
    __rmod__ = partialmethod(reop, op=operator.mod)
    __imod__ = partialmethod(inop, op=operator.mod)

    __pow__ = partialmethod(binop, op=operator.pow)
    __rpow__ = partialmethod(reop, op=operator.pow)
    __ipow__ = partialmethod(inop, op=operator.pow)

    __lshift__ = partialmethod(binop, op=operator.lshift)
    __rlshift__ = partialmethod(reop, op=operator.lshift)
    __ilshift__ = partialmethod(inop, op=operator.lshift)

    __rshift__ = partialmethod(binop, op=operator.rshift)
    __rrshift__ = partialmethod(reop, op=operator.rshift)
    __irshift__ = partialmethod(inop, op=operator.rshift)

    __and__ = partialmethod(binop, op=operator.and_)
    __rand__ = partialmethod(reop, op=operator.and_)
    __iand__ = partialmethod(inop, op=operator.and_)

    __or__ = partialmethod(binop, op=operator.or_)
    __ror__ = partialmethod(reop, op=operator.or_)
    __ior__ = partialmethod(inop, op=operator.or_)

    __xor__ = partialmethod(binop, op=operator.xor)
    __rxor__ = partialmethod(reop, op=operator.xor)
    __ixor__ = partialmethod(inop, op=operator.xor)

    __invert__ = partialmethod(unoop, op=operator.invert)
    __pos__ = partialmethod(unoop, op=operator.pos)
    __neg__ = partialmethod(unoop, op=operator.neg)

    __eq__ = partialmethod(cmpop, op=operator.eq)
    __ne__ = partialmethod(cmpop, op=operator.ne)
    __gt__ = partialmethod(cmpop, op=operator.gt)
    __ge__ = partialmethod(cmpop, op=operator.ge)
    __lt__ = partialmethod(cmpop, op=operator.lt)
    __le__ = partialmethod(cmpop, op=operator.le)

    def __contains__(self, symbol):
        """Returns True if this symbol contains the given symbol as
        one of its left or right values, or the left or right values
        of those values if they're also symbols.

        Note that this performs the test recursively, and might be slow
        for large-scale binary symbol heaps.

        Average time: O(log(n))
        Worst-case  : O(n)
        """
        if self.left is symbol or self.right is symbol:
            # If either side is the symbol, return True.
            return True
        elif isinstance(self.left, AthSymbol):
            if isinstance(self.right, AthSymbol):
                # If both values are symbols, return True
                # if at least one value contains the symbol
                return (
                    self.left.__contains__(symbol) or 
                    self.right.__contains__(symbol)
                    )
            else:
                # If only left is a symbol, check that one
                return self.left.__contains__(symbol)
        elif isinstance(self.right, AthSymbol):
            # If only right is a symbol, check that one
            return self.right.__contains__(symbol)
        else:
            # If neither are symbols, return False.
            return False


    def copy(self):
        """Deep copies this symbol and returns the result."""
        newsymbol = AthSymbol(self.alive)
        if isinstance(self.left, AthSymbol):
            newsymbol.left = self.left.copy()
        else:
            newsymbol.left = self.left
        if isinstance(self.right, AthSymbol):
            newsymbol.right = self.right.copy()
        else:
            newsymbol.right = self.right
        return newsymbol

    def refcopy(self, ref):
        """Replaces all instances of a reference symbol in
        this symbol with deep copies of that reference symbol.
        """
        if ref is self:
            return self.copy()
        if isinstance(self.left, AthSymbol):
            self.left = self.left.refcopy(ref)
        if isinstance(self.right, AthSymbol):
            self.right = self.right.refcopy(ref)
        return self

    def copyfrom(self, other):
        self.alive = other.alive
        self.left = other.left
        self.right = other.right

    def assign_left(self, value):
        if not (isAthValue(value)
            or isinstance(value, AthSymbol)
            or value is None
            ):
            raise TypeError(
                'May only assign constants or symbols to left'
                )
        self.left = value


    def assign_right(self, value):
        if not (isinstance(value, (AthFunction, AthSymbol)) or value is None):
            raise TypeError(
                'May only assign functions or symbols to right'
                )
        self.right = value

    def kill(self):
        """THIS.DIE()"""
        self.alive = False


class BuiltinSymbol(AthSymbol):
    __slots__ = ()

    def __init__(self, alive=True, left=None, right=None):
        self.alive = alive
        self.left = left
        self.right = right

    @classmethod
    def from_builtin(cls, name, func, argsmin, argsmax=None):
        return cls(True, name, AthBuiltinFunction(name, func, argsmin, argsmax))

    def __repr__(self):
        return '{}({}, {!r}, {!r})'.format(
            self.__class__.__name__,
            self.alive, self.left, self.right,
            )

    def copyfrom(self, other):
        raise SymbolError('Builtins are not mutable!')

    def assign_left(self, value):
        raise SymbolError('Builtins are not mutable!')

    def assign_right(self, value):
        raise SymbolError('Builtins are not mutable!')


class NullSymbol(BuiltinSymbol):
    """NULL is a singleton immutable symbol used as the default no value object.
    Some ~ATH statements can use NULL to initialize empty and dead symbols.
    """
    __slots__ = ()
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__(False)

    def __repr__(self):
        return '{}()'.format(
            self.__class__.__name__
            )

    def copy(self):
        return AthSymbol(False)

    def refcopy(self):
        return AthSymbol(False)        
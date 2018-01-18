#!/usr/bin/env python
import sys
from time import time
from argparse import ArgumentParser
from symbol import AthSymbol, AthFunction, BuiltinSymbol, SymbolDeath
from athast import CondJumpStmt, ExecuteStmt, TildeAthLoop
from athparser import ath_lexer, ath_parser

__version__ = '1.3.5 Dev Build'
__author__ = 'virtuNat'


def echo_error(msg):
    sys.stderr.write(msg)
    sys.exit(1)


class AthStackFrame(object):
    """Keeps a record of all symbols declared in a given scope.
    ~ATH implements dynamic scope, so be wary when coding in it!
    """
    __slots__ = ('scope_vars', 'return_pt', 'state', 'eval_stack')

    def __init__(self, scope_vars=None, return_pt=None):
        if not scope_vars:
            self.scope_vars = {}
        else:
            self.scope_vars = scope_vars
        self.return_pt = return_pt
        self.state = 0

    def __getitem__(self, name):
        return self.scope_vars[name]

    def __setitem__(self, name, value=None):
        if value is None:
            value = AthSymbol(False)
        try:
            symbol = self.scope_vars[name]
        except KeyError:
            pass
        finally:
            self.scope_vars[name] = value


class TildeAthInterp(object):
    """This is supposed to be a Finite State Machine"""
    __slots__ = ('modules', 'bltin_vars', 'stack', 'state')

    def __init__(self):
        self.modules = {}
        self.bltin_vars = {
            'THIS': BuiltinSymbol(),
            'NULL': BuiltinSymbol(False),
            'DIE': BuiltinSymbol(),
            'ATH': BuiltinSymbol(),
            'print': BuiltinSymbol(),
            'input': BuiltinSymbol(),
            'import': BuiltinSymbol(),
            'DEBATE': BuiltinSymbol(),
            'UNLESS': BuiltinSymbol(),
            'EXECUTE': BuiltinSymbol(),
            'DIVULGATE': BuiltinSymbol(),
            'FABRICATE': BuiltinSymbol(),
            'REPLICATE': BuiltinSymbol(),
            'PROCREATE': BuiltinSymbol(),
            'BIFURCATE': BuiltinSymbol(),
            'AGGREGATE': BuiltinSymbol(),
            'ENUMERATE': BuiltinSymbol(),
            }
        self.stack = [AthStackFrame()]
        # Current execution state.
        self.state = 0

    def push_stack(self, ast, state, init_dict={}):
        self.stack[-1].return_pt = ast
        self.stack.append(AthStackFrame(init_dict))
        self.state = state
        stacklen = len(self.stack)
        if stacklen < 1000:
            return
        elif stacklen == 1000:
            print('i told you DOG i TOLD you about STACKS!!')
        elif stacklen == 1500:
            print('quick dude come get the ruler its ESCAPING from ABOVE!!')
        elif stacklen == 2000:
            print('dude how HIGH do you have to even BE to do such a thing??')
        elif stacklen == 4000:
            raise RecursionError

    def pop_stack(self):
        self.stack.pop()
        self.state = self.stack[-1].state
        return self.stack[-1].return_pt

    def lookup_name(self, name):
        for frame in reversed(self.stack):
            try:
                return frame[name]
            except KeyError:
                continue
        try:
            return self.bltin_vars[name]
        except KeyError:
            raise NameError('Symbol {} not found'.format(name))

    def assign_name(self, name, value):
        try:
            self.stack[-1][name] = value
        except IndexError:
            raise RuntimeError('All the stack frames died, what the fuck happened?')

    def trampoline(self, eval_stack, ast, return_val=None):
        ctrl_name = ast.ctrl_name
        # If return_val is not None, a value was returned from a function.
        if return_val is not None:
            # Pass the return value to the caller.
            eval_stack[-1].return_val = return_val
        while True:
            print('Stack: ', eval_stack[-1])
            # Execution must continue from the expression on top of the stack.
            try:
                # Evaluate the expression at the top of the stack.
                callback, value = next(eval_stack[-1].eval_gen)
            except SymbolDeath:
                if not self.lookup_name('THIS'):
                    # If THIS dies, end execution.
                    sys.exit(0)
                elif not self.lookup_name(ctrl_name):
                    # If the AST control name dies, reraise.
                    return self.pop_stack()
            if callback:
                # If there's a callback, see if it's a function call.
                if not isinstance(callback, AthFunction):
                    # Push evaluation stack if it's not a function.
                    eval_stack.append(callback.iterate(self))
                    continue
                value = AthSymbol(None)
                # # If the callback is a function, move to function state.
                # self.stack[-1].eval_stack = eval_stack
                # self.push_stack(ast, 2, value)
                # return iter(callback.body)
            # If there's no callback, this expression is done.
            eval_stack.pop()
            try:
                # Use the return value in the next expression.
                eval_stack[-1].return_val = value
            except IndexError:
                # If there are no more statements, move on.
                return None

    def execute(self, ast):
        count = 0
        try:
            while True:
                print(ast.index)
                if not self.state: # Toplevel execution.
                    try:
                        node = next(ast)
                    except StopIteration:
                        # Reset AST iteration state.
                        iter(ast)
                        # Prevent infinite iteration from toplevel.
                        if count == 1025:
                            echo_error(
                                'UnboundATHLoopError: THIS.DIE() not called'
                                )
                        count += 1
                        continue
                elif self.state == 1: # Looping
                    try:
                        node = next(ast)
                    except StopIteration:
                        if not self.lookup_name(ctrl_name):
                            # If the control name died, kill the loop.
                            ast = self.pop_stack()
                        else:
                            # Reset AST iteration state when continuing loop.
                            iter(ast)
                        continue
                elif self.state == 2: # Function execution
                    try:
                        node = next(ast)
                    except StopIteration:
                        # Reset AST iteration state.
                        iter(ast)
                        # Prevent infinite iteration from toplevel.
                        if count == 1025:
                            echo_error(
                                'UnboundATHLoopError: THIS.DIE() not called'
                                )
                        count += 1  
                    self.state = 0
                    continue
                # Evalutate execution state.
                if isinstance(node, CondJumpStmt):
                    # Jump if no condition or on failure.
                    if node.clause and node.clause.eval(self):
                        continue
                    ast.index += node.height
                    continue
                elif isinstance(node, TildeAthLoop):
                    # Add stack frame and replace ast reference.
                    self.push_stack(ast, 1)
                    ast = iter(node.body)
                    ctrl_name = ast.ctrl_name
                    continue
                elif isinstance(node, ExecuteStmt):
                    self.state = 2
                    continue
                self.trampoline([node.iterate(self)], ast)
        except RecursionError:
            print('my GUY.')
            print('stop making the stack not STOP from getting any taller!!!')
            sys.exit(1)
        except KeyboardInterrupt:
            print(self.stack[-1].scope_vars)
            raise
        except Exception:
            print('dude its ESCAPING TO THE SIDE, stop it!!!!')
            raise

    def interpret(self, fname):
        if not fname.endswith('.~ATH'):
            echo_error('IOError: script must be a ~ATH file')
        with open(fname, 'r') as script_file:
            script = script_file.read()
        tokens = ath_lexer(script)
        try:
            result = ath_parser(tokens, 0).value
        except SyntaxError:
            echo_error('RuntimeError: the parser could not understand the script')
        result.flatten()

        for stmt in result:
            if isinstance(stmt, TildeAthLoop):
                result.index = 0
                break
        else:
            echo_error('RuntimeError: no ~ATH loop found in top-level script')

        with open(fname[:-4]+'py', 'w') as py_file:
            py_file.write('#!/usr/bin/env python\nfrom athast import *\n')
            py_file.write('from tildeath import TildeAthInterp\n\n')
            py_file.write('ath_script = ' + repr(result))
            py_file.write('\nTildeAthInterp().execute(ath_script)\n')
        self.execute(result)


if __name__ == '__main__':
    cmdparser = ArgumentParser(
        description='A fanmade ~ATH interpreter.',
        )
    cmdparser.add_argument(
        'script',
        help='The ~ATH file to run.',
        metavar='scr_name',
        )
    cmdargs = cmdparser.parse_args()
    ath_interp = TildeAthInterp()
    ath_interp.interpret(cmdargs.script)

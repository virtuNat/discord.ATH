#!/usr/bin/env python
from athstmt import *
from athinterpreter import TildeAthInterp

stmts = AthStatementList([
    TildeAthLoop(False, AthStatementList([
        AthTokenStatement('print', [LiteralToken('Hello World!\\n', str)]),
        AthTokenStatement('print', [LiteralToken('This is the script ~s!\\n', str), IdentifierToken('THIS')]),
        AthTokenStatement('DIE', [IdentifierToken('THIS')]),
        ], pendant='THIS'),
        AthTokenStatement('EXECUTE', [IdentifierToken('NULL')]))
    ], pendant='THIS')
TildeAthInterp().exec_stmts('hello.~ATH', stmts)

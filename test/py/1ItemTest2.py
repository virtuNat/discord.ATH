#!/usr/bin/env python
from athast import *
from athparser import TildeAthInterp

ath_script = Serialize([ProcreateStmt(VarExpr('LOOP'), IntExpr(0)), TildeAthLoop(VarExpr('LOOP'), Serialize([PrintFunc([StringExpr('Which of the following is not a French word?\\n')]), PrintFunc([StringExpr('[A] sale\\n')]), PrintFunc([StringExpr('[B] mode\\n')]), PrintFunc([StringExpr('[C] grand\\n')]), PrintFunc([StringExpr('[D] chat\\n')]), PrintFunc([StringExpr('[E] A, B, C, and D are all French words\\n')]), PrintFunc([StringExpr('[F] A, B, C, and D are all not French words\\n')]), InputStmt(VarExpr('CHOICE'), StringExpr('')), ProcreateStmt(VarExpr('F'), StringExpr('F')), ProcreateStmt(VarExpr('CHEAT'), StringExpr('THE CHEAT CODE')), ProcreateStmt(VarExpr('DEATH'), StringExpr('DIE')), DebateStmt(BinaryExpr('<=', VarExpr('CHOICE'), VarExpr('F')), Serialize([PrintFunc([StringExpr('Wrong! Try again, idiot.\\n')])], LOOP), [UnlessStmt(BinaryExpr('==', VarExpr('CHOICE'), VarExpr('CHEAT')), Serialize([PrintFunc([StringExpr("Damn, you caught me. It's a trick question.\\n")])], LOOP)), UnlessStmt(BinaryExpr('==', VarExpr('CHOICE'), VarExpr('DEATH')), Serialize([PrintFunc([StringExpr('Hmph. Ninny.\\n')]), KillFunc(VarExpr('LOOP'), [])], LOOP)), UnlessStmt(None, Serialize([PrintFunc([StringExpr("HA! Loser can't even guess the cheat code.\\n")])], LOOP))]), PrintFunc([StringExpr('\\n')])], LOOP)), KillFunc(VarExpr('THIS'), [])], THIS)
TildeAthInterp().execute(ath_script)

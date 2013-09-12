tokens = ("NAME", "INT", "FLOAT", "TIMES", "POW", "PLUS", "MINUS", "DIV")

literals = ['(', ')']

t_TIMES = r'\*'
t_POW = r'\*\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_DIV = r'/'

precedence = (
	('left', 'PLUS', 'MINUS'),
	('left', 'TIMES', 'DIV'),
	('right', 'POW'),
	('right', 'UMINUS')
)
def t_FLOAT(t):
	r'([0-9]+\.[0-9]*)|([0-9]*\.[0-9]+)'
	try:
		t.value = float(t.value)
	except ValueError:
		raise Exception("Float value too large %s" % t.value)
		t.value = 0
	return t

def t_INT(t):
	r'[0-9]+'
	try:
		t.value = int(t.value)
	except ValueError:
		raise Exception("Integer value too large %s" % t.value)
		t.value = 0
	return t

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_ignore = " \t"

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

def t_error(t):
	raise Exception("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

import ply.lex as lex
lex.lex(debug=False)

from .expr import *

def p_expression_float(p):
	'expression : FLOAT'
	p[0] = Number(p[1])

def p_expression_int(p):
	'expression : INT'
	p[0] = Number(p[1])

import operator

def p_expression_add(p):
	"expression : expression PLUS expression"
	p[0] = InfixOp(operator.add, p[1], p[3])

def p_expression_sub(p):
	"expression : expression MINUS expression"
	p[0] = InfixOp(operator.sub, p[1], p[3])

def p_expression_mult(p):
	"expression : expression TIMES expression"
	p[0] = InfixOp(operator.mul, p[1], p[3])

def p_expression_pow(p):
	"expression : expression POW expression"
	p[0] = InfixOp(smartpow, p[1], p[3])

def p_expression_uminus(p):
	"expression : MINUS expression %prec UMINUS"
	p[0] = NumericalOp(operator.neg, p[2])

def p_expression_div(p):
	"expression : expression DIV expression"
	p[0] = InfixOp(smartdiv, p[1], p[3])

def p_expression_function(p):
	"expression : NAME '(' expression ')'"
	try:
		op = {"sin": math.sin,
		 "asin": math.asin,
		 "cos": math.cos,
		 "acos": math.acos,
		 "tan": math.tan,
		 "atan": math.atan,
		 "abs": abs,
		 "log": math.log,
		 "int": int,
		 "float": float,
		 "floor": math.floor,
		 "ceil": math.ceil,
		 "exp": math.exp,
		 "log2": log2,
		 "log10": math.log10,
		 "sqrt": math.sqrt,
		 }[p[1]]
		p[0] = NumericalOp(op, p[3])
	except KeyError as ex:
		raise Exception("Unsupported function: %s" % ex)

def p_expression_group(p):
	"expression : '(' expression ')'"
	p[0] = p[2]

def p_error(p):
	raise Exception("Syntax error")


import ply.yacc as yacc
yacc.yacc(debug=False, write_tables=False)

def evaluate(s):
	e = yacc.parse(s)
	return eval(e)

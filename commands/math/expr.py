import math
import operator

class Number(object):
	"""technically, this simply evaluates to whatever you put in it. But you probably want to put a number in it."""
	def __init__(self, num):
		self.num = num
	def eval(self):
		return self.num

class InfixOp(object):
	"""this covers +, -, *, /. Probably other stuff too."""
	def __init__(self, op, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
		self.op = op

	def eval(self):
		return self.op(self.expr1.eval(), self.expr2.eval())

class NumericalOp(object):
	"covers things like sin, log, tan, arccos, abs, etc"
	def __init__(self, op, expr):
		self.expr = expr
		self.op = op

	def eval(self):
		return self.op(self.expr.eval())

def smartdiv(a, b):
	return float(a) / b

def smartpow(a, b):
	if b > 100:
		raise Exception("Exponent too large.")
	else:
		return a ** b

def log2(n):
	return math.log(n) / math.log(2)

def eval(expr):
	n = expr.eval()
	try:
		if round(n) == n:
			return int(n)
	except OverflowError:
		pass
	return n


from .parser import evaluate

def handle(bot, user, destination, arg):
	to = destination if destination.startswith(bot.config.CHANNEL_PREFIX) else user.split('!', 1)[0]
	try:
		bot.chat(str(evaluate(arg)), to)
	except ZeroDivisionError:
		bot.chat("division by zero", to)
	except Exception as ex:
		bot.chat(str(ex), to)

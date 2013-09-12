import random

def handle(bot, user, destination, arg):
	try:
		num, sides = arg.split()
		if int(num) > 40 or int(sides) > 40:
			return
		rolls = [random.randint(1, int(sides)) for k in range(int(num))]
		to = destination if destination.startswith(bot.config.CHANNEL_PREFIX) else user.split('!', 1)[0]
		bot.chat(' '.join([str(r) for r in rolls]) + ' (%s)' % sum(rolls), to)
	except:
		pass

def handle(bot, user, destination, arg):
	if not destination.startswith(bot.config.CHANNEL_PREFIX):
		return
	nickname = arg or user.split('!')[0]
	info = bot.get_user(user)
	if info and info['can_op']:
		bot.write('MODE', destination, '+o', nickname)

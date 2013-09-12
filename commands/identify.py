import hashlib

def handle(bot, user, destination, arg):
	to = destination if destination.startswith(bot.config.CHANNEL_PREFIX) else user.split('!')[0]
	cur = bot.db.cursor()
	try:
		parts = arg.split(None, 1)
		if len(parts) > 1:
			nickname = parts[0].strip()
			password = hashlib.sha1(parts[1].strip().encode('utf-8')).hexdigest()
		else:
			nickname = user.split('!')[0]
			password = hashlib.sha1(parts[0].strip().encode('utf-8')).hexdigest()
		cur.execute('select id from users where nickname = ? and password = ?', (nickname, password))
		user_id = cur.fetchone()[0]
		cur.execute('select user_id from hosts where host = ?', (user,))
		row = cur.fetchone()
		if row and row[0] == user_id:
			bot.chat('You are already identified!', to)
		else:
			cur.execute('insert into hosts (user_id, host, date_registered) values (?, ?, current_timestamp)', (user_id, user))
			bot.db.commit()
			bot.chat("OK, I've identified %s as %s" % (user, nickname), to)
	except Exception as ex:
		bot.chat('I was not able to identify you.', to)
	finally:
		cur.close()

import functools
import smtplib

TEMPLATE = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s'

def send_sms(fromaddr, toaddr, subject, message):
	s = smtplib.SMTP('localhost')
	s.sendmail(fromaddr, [toaddr], TEMPLATE % (fromaddr, toaddr, subject, message))
	s.quit()

def get_sms_email(db, nickname):
	cur = db.cursor()
	try:
		cur.execute('select sms_email from users where nickname = ?', (nickname,))
		return cur.fetchone()[0]
	except:
		pass
	finally:
		cur.close()

def got_host(bot, nick, host, is_op, is_away, subject=None, message=None):
	mask = '%s!%s' % (nick, host)
	cur = bot.db.cursor()
	try:
		cur.execute('select u.sms_email from users u inner join hosts h on h.user_id = u.id where h.host = ?', (mask,))
		email = cur.fetchone()[0]
		send_sms(bot.config.BOT_EMAIL, email, subject, message)
	except:
		bot.chat('I do not have an SMS address for %s.' % nick)
	finally:
		cur.close()

def handle(bot, user, destination, arg):
	to = destination if destination.startswith(bot.config.CHANNEL_PREFIX) else user.split('!', 1)[0]
	try:
		nick, message = arg.split(None, 1)
		subject = 'SMS from %s' % nick
		# Make sure the person trying to SMS has a valid user entry.
		info = bot.get_user(user)
		if info:
			email = get_sms_email(bot.db, nick)
			if email:
				send_sms(bot.config.BOT_EMAIL, email, subject, message)
			else:
				bot.lookup(nick, functools.partial(got_host, subject=subject, message=message))
		else:
			bot.chat('I could not identify you.', to)
	except Exception, ex:
		bot.chat('Error sending SMS: %s' % ex, to)

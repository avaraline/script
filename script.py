#!/usr/bin/env python

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.tcpserver import TCPServer
import datetime
import sqlite3
import socket
import email
import sys
import re
import os

import config

line_regex = re.compile('^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?')

class Script (object):

	def __init__(self, nick=None, user=None, logdir=None):
		self.config = config
		self.nickname = nick or config.BOT_NICKNAME
		self.username = user or config.BOT_USERNAME
		self.logdir = logdir or config.LOG_DIRECTORY
		self.stream = None
		self.ready = not config.WAIT_FOR_PING
		self.onready = []
		self.channels = []
		self.lookup_callbacks = {}
		self.host = '%s!%s@localhost' % (self.nickname, self.username)
		self.db = sqlite3.connect(config.DATABASE_FILE)
		self.db.row_factory = sqlite3.Row

	def start(self, host=None, port=None):
		host = host or config.SERVER_HOST
		port = port or config.SERVER_PORT
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
		s.connect((host, port))
		self.stream = IOStream(s)
		self.write('NICK', self.nickname)
		self.write('USER', self.username, config.BOT_MODES, self.username, config.BOT_REALNAME)
		self.read_line(self.parse_line)

	def read_line(self, callback):
		self.stream.read_until(b'\r\n', callback)

	def parse_line(self, data):
		# IRC doesn't really define an encoding. Try UTF-8 first, fall back to latin-1.
		try:
			data = data.decode('utf-8')
		except:
			data = data.decode('latin-1')
		parts = line_regex.match(data.strip()).groupdict()
		cmd = parts['command'].lower()
		args = []
		if parts['argument']:
			if ':' in parts['argument']:
				arg, text = parts['argument'].split(':', 1)
				args.extend(arg.strip().split())
				args.append(text.strip())
			else:
				args.extend(parts['argument'].split())
		func = getattr(self, 'handle_%s' % cmd, None)
		if func and callable(func):
			try:
				func(parts['prefix'], *args)
			except Exception as ex:
				print('Error handling "%s": %s' % (cmd, str(ex)))
		self.read_line(self.parse_line)

	def write(self, cmd, *args):
		if not isinstance(cmd, bytes):
			cmd = cmd.encode('ascii')
		line = cmd.upper()
		if args:
			byte_args = []
			for a in args:
				if isinstance(a, str):
					byte_args.append(a.encode('utf-8'))
				elif isinstance(a, bytes):
					byte_args.append(a)
				else:
					raise Exception('Arguments to write must be str or bytes.')
			if b' ' in byte_args[-1]:
				byte_args[-1] = b':' + byte_args[-1]
			line += b' ' + b' '.join(byte_args)
		self.stream.write(line + b'\r\n')

	def chat(self, line, destination=None):
		destination = destination or self.channels
		if not destination:
			return
		if not isinstance(destination, (list, tuple)):
			destination = (destination,)
		# Since we don't receive our own chat, log it manually.
		for dest in destination:
			self.log_chat(self.user, dest, line)
			self.write('PRIVMSG', dest, line)

	def join(self, channel):
		if not channel.startswith(config.CHANNEL_PREFIX):
			return
		if self.ready:
			self.write('JOIN', channel)
		else:
			self.onready.append(lambda bot: bot.write('JOIN', channel))

	def lookup(self, nickname, callback):
		self.lookup_callbacks[nickname] = callback
		self.write('USERHOST', nickname)

	def get_user(self, host):
		host = host.lower().strip()
		cur = self.db.cursor()
		try:
			cur.execute("""
				select nickname, password, name, email, sms_email, can_op, auto_op
				from users u inner join hosts h on h.user_id = u.id where h.host = ?
			""", (host,))
			return cur.fetchone()
		finally:
			cur.close()

	def log_chat(self, user, destination, line):
		if not destination.startswith(config.CHANNEL_PREFIX) or not self.logdir or not config.ENABLE_LOGGING:
			return
		if not os.path.exists(self.logdir):
			os.mkdir(self.logdir)
		chandir = os.path.join(self.logdir, destination[1:])
		if not os.path.exists(chandir):
			os.mkdir(chandir)
		now = datetime.datetime.now()
		filename = now.strftime('%Y-%m-%d') + '.txt'
		time = now.strftime('%H:%M:%S')
		logfile = os.path.join(chandir, filename)
		with open(logfile, 'ab') as f:
			log_line = '%s\t%s\t%s\n' % (time, user, line)
			f.write(log_line.encode('utf-8'))

	def handle_ping(self, prefix, *args):
		self.write('PONG', *args)
		# I don't know if this is universally accepted, but our server doesn't
		# let you do anything until you respond to the initial PING.
		if not self.ready:
			self.ready = True
			for func in self.onready:
				func(self)

	def handle_join(self, user, channel):
		nick = user.split('!')[0]
		if nick == self.nickname:
			self.user = user
			if channel.startswith(config.CHANNEL_PREFIX) and channel not in self.channels:
				self.channels.append(channel)
		else:
			u = self.get_user(user)
			if u and u['auto_op']:
				self.write('MODE', channel, '+o', nick)

	def handle_part(self, user, channel, msg=None):
		pass

	def handle_302(self, server, mynick, userhost):
		nick, host = userhost.split('=', 1)
		is_op = False
		if nick.endswith('*'):
			is_op = True
			nick = nick[:-1]
		is_away = host.startswith('-')
		host = host[1:]
		if nick in self.lookup_callbacks:
			self.lookup_callbacks[nick](self, nick, host, is_op, is_away)
			del self.lookup_callbacks[nick]

	def handle_privmsg(self, user, destination, line):
		if destination.startswith(config.CHANNEL_PREFIX):
			self.log_chat(user, destination, line)
		if line.startswith('!'):
			parts = line.split(None, 1)
			cmd = parts[0].strip()[1:]
			arg = None if len(parts) < 2 else parts[1].strip()
			self.run_command(user, destination, cmd, arg)

	def run_command(self, user, destination, cmd, arg):
		try:
			mod_name = 'commands.%s' % cmd
			if mod_name in sys.modules:
				del sys.modules[mod_name]
			mod = __import__(mod_name, [], [], 'commands')
			mod.handle(self, user, destination, arg)
		except Exception as ex:
			print('Error running command "%s": %s' % (cmd, str(ex)))

class EmailGateway (TCPServer):

	def __init__(self, bot):
		super(EmailGateway, self).__init__()
		self.bot = bot

	def handle_stream(self, stream, address):
		stream.read_until_close(self.handle_email)

	def handle_email(self, data):
		msg = email.message_from_string(data)
		who = msg['From'].strip()
		cur = self.bot.db.cursor()
		try:
			cur.execute('select nickname from users where sms_email = ?', (who.lower(),))
			who = cur.fetchone()[0] + ' (SMS)'
		except:
			pass
		finally:
			cur.close()
		what = msg.get_payload().splitlines()[0].strip()
		self.bot.chat('From %s: %s' % (who, what))

if __name__ == '__main__':
	bot = Script(config.BOT_NICKNAME)
	bot.start(config.SERVER_HOST, config.SERVER_PORT)
	for c in config.JOIN_CHANNELS:
		bot.join(c)
	if config.ENABLE_EMAIL_GATEWAY:
		gateway = EmailGateway(bot)
		gateway.listen(config.EMAIL_GATEWAY_PORT, config.EMAIL_GATEWAY_HOST)
	IOLoop.instance().start()

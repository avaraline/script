import requests

API_URL = 'http://api.wunderground.com/api/%(key)s/conditions/q/%(query)s.json%(extra)s'
API_KEY = 'eb44fa43667ddea5'

def handle(bot, user, destination, arg):
	to = destination if destination.startswith(bot.config.CHANNEL_PREFIX) else user.split('!', 1)[0]
	query = arg
	extra = ''
	if not arg:
		query = 'autoip'
		extra = '?geo_ip=%s' % user.rsplit('@', 1)[-1]
	else:
		query = query.replace(' ', '_')
	url = API_URL % {
		'key': API_KEY,
		'query': query,
		'extra': extra,
	}
	data = requests.get(url).json()['current_observation']
	city = data['display_location']['full']
	temp = data['temp_f']
	cond = data['weather']
	flik = data['feelslike_f']
	bot.chat('Currently in %s: %s and %s (feels like %s)' % (city, temp, cond, flik), to)

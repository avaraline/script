import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SERVER_HOST = 'avaraline.net'
SERVER_PORT = 6667

BOT_NICKNAME = 'script'
BOT_USERNAME = 'script'
BOT_REALNAME = 'Script 2.0'
BOT_MODES = '+iwB'
BOT_EMAIL = 'script@avaraline.net'

CHANNEL_PREFIX = '#'
JOIN_CHANNELS = ['#avaraline']

WAIT_FOR_PING = False

ENABLE_LOGGING = True
LOG_DIRECTORY = os.path.join(SCRIPT_DIR, 'logs')

ENABLE_EMAIL_GATEWAY = False
EMAIL_GATEWAY_HOST = '127.0.0.1'
EMAIL_GATEWAY_PORT = 7100

DATABASE_FILE = os.path.join(SCRIPT_DIR, 'users.db')

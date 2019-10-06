import random
import string
import traceback
from configparser import ConfigParser




import os
configfile_name = "config.ini"

# Check if there is already a configurtion file
if not os.path.isfile(configfile_name):
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(configfile_name, 'w')
    # Add content to the file
    Config = ConfigParser(allow_no_value=True)
    Config.add_section('FILENAMES')
    Config.set('FILENAMES', 'urls_filename', 'urls.txt')
    Config.set('FILENAMES', 'filters_filename', 'filters.txt')
    Config.set('FILENAMES', 'id_file', 'id_file.txt')
    Config.add_section('PARSER OPTIONS')
    Config.set('PARSER OPTIONS','API_ID','')
    Config.set('PARSER OPTIONS','API_HASH','')
    Config.add_section('TELEGRAM OPTIONS')
    Config.set('TELEGRAM OPTIONS', 'API_TOKEN ', '')
    Config.set('TELEGRAM OPTIONS', 'WEBHOOK_HOST', '18.216.72.123')
    Config.set('TELEGRAM OPTIONS', 'WEBHOOK_PORT', '8443')
    Config.set('TELEGRAM OPTIONS', 'WEBHOOK_LISTEN', '0.0.0.0')
    Config.set('TELEGRAM OPTIONS', 'WEBHOOK_SSL_CERT', './webhook_cert.pem')
    Config.set('TELEGRAM OPTIONS', 'WEBHOOK_SSL_PRIV', './webhook_pkey.pem')
    Config.set('TELEGRAM OPTIONS', 'CUSTOM_START', '')
    Config.write(cfgfile)
    cfgfile.close()
config = ConfigParser()
config.read(configfile_name)
try:
    urls_filename = config.get('FILENAMES','urls_filename')
    filters_filename = config.get('FILENAMES','filters_filename')
    id_file = config.get('FILENAMES','id_file')
    api_id = int(config.get('PARSER OPTIONS','api_id'))
    api_hash = config.get('PARSER OPTIONS','api_hash')
    REGISTER_CODE = ''
    REGISTER_PHRASE = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
    API_TOKEN = config.get('TELEGRAM OPTIONS','api_token')
    WEBHOOK_HOST = config.get('TELEGRAM OPTIONS','WEBHOOK_HOST')
    WEBHOOK_PORT = int(config.get('TELEGRAM OPTIONS','WEBHOOK_PORT'))
    WEBHOOK_LISTEN = config.get('TELEGRAM OPTIONS','WEBHOOK_LISTEN')  # In some VPS you may need to put here the IP addr
    WEBHOOK_SSL_CERT = config.get('TELEGRAM OPTIONS','WEBHOOK_SSL_CERT') # Path to the ssl certificate
    WEBHOOK_SSL_PRIV = config.get('TELEGRAM OPTIONS','WEBHOOK_SSL_PRIV')  # Path to the ssl private key
    CUSTOM_START = config.get('TELEGRAM OPTIONS','CUSTOM_START')
    WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
    WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)
except Exception as e:
    print('Настройте ваш файл конфигурации')
    print(str(e))
    print(traceback.format_exc())
    input()
    raise Exception()
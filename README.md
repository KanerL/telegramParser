# TelegramLiveChannelParser
This app allows you to get live posts from Telegram channels with filters that you are interested in
# How to run
Download repository and then run this commands :

    pip install -r requirments.txt
    python main.py

The ``config.ini`` file will be created at the first launch

    [PARSER OPTIONS]
    api_id = VALUE # App API key.Can get here https://my.telegram.org/ 
    api_hash = VALUE # App API Hash.Can get here https://my.telegram.org/ 

    [TELEGRAM OPTIONS]
    api_token  = VALUE # Bot api key(https://t.me/BotFather)
    /# Server settigs
    webhook_host = 0.0.0.0 # Server ip
    webhook_port = 8443 # Server port
    webhook_listen = 0.0.0.0 # Server ip(not necessary to change)
    webhook_ssl_cert = ./webhook_cert.pem # file with ssl certificate
    webhook_ssl_priv = ./webhook_pkey.pem # file with ssl private key
    custom_start = VALUE # Custom start message
# Creating of certificates:

    openssl genrsa -out webhook_pkey.pem 2048
    openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
  When "Common Name (e.g. server FQDN or YOUR name)" is requested enter the same as value of ``webhook_host``

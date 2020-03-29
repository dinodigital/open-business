from mintersdk.minterapi import MinterAPI

# ----------------------------------------------------------------------------------------------------------------------
# Настройки API
# ----------------------------------------------------------------------------------------------------------------------

# API_NODE_URL = 'http://api.minter.one'
API_NODE_URL = 'https://mnt.funfasy.dev/v0'

TIMEOUTS = {
    'read_timeout': 6,
    'connect_timeout': 7
}

HEADERS = {
    'X-Project-Id': 'b6ed57c1-cb5a-4d14-87d1-da2c71d34552',
    'X-Project-Secret': '2278fc456df510d12f3e0d0a94bce6f8'
}

API = MinterAPI(API_NODE_URL, headers=HEADERS, **TIMEOUTS)

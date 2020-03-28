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

HEADERS = {}

API = MinterAPI(API_NODE_URL, headers=HEADERS, **TIMEOUTS)

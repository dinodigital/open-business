from mintersdk.minterapi import MinterAPI
from mintersdk.sdk.wallet import MinterWallet

# ----------------------------------------------------------------------------------------------------------------------
# ОСНОВНЫЕ НАСТРОЙКИ
# ----------------------------------------------------------------------------------------------------------------------

PAYLOAD = 'Автоматическая выплата'

SEED = ''
PRIVATE_KEY = MinterWallet.create(mnemonic=SEED)['private_key']
ADDRESS = MinterWallet.create(mnemonic=SEED)['address']

STOP_LIST = ['Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5']
DELEGATED_TOKEN = 'GORBUNOV'
MIN_COINS_DELEGATED = 1


# ----------------------------------------------------------------------------------------------------------------------
# Насторйки выплат
# ----------------------------------------------------------------------------------------------------------------------

# Налоги
PAYING_TAXES = False
TAXES = {
    'wallet': 'Mx5cef09065d68561ad9f61a905c7d0aa230117733',
    'percent': 0.1
}

# Делегаторы
PAYING_DELEGATORS = True
DELEGATORS_PERCENT = 0.1

# Основатели
FOUNDERS = {
        'gorbunov': {
            'wallet': 'Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5',
            'percent': 0.85},
        'isheldon': {
            'wallet': 'Mxd315211a50c65e036c14117f6949f2ac91bb6170',
            'percent': 0.15}
}


# ----------------------------------------------------------------------------------------------------------------------
# API
# ----------------------------------------------------------------------------------------------------------------------
NODE_API_URL = 'http://api.minter.one'
TIMEOUTS = {'read_timeout': 6, 'connect_timeout': 7}
API = MinterAPI(NODE_API_URL, **TIMEOUTS)
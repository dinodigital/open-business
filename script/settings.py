from mintersdk.minterapi import MinterAPI
from mintersdk.sdk.wallet import MinterWallet

# ----------------------------------------------------------------------------------------------------------------------
# Основные настройки скрипта
# ----------------------------------------------------------------------------------------------------------------------

PAYLOAD = 'Автоматическая выплата'
PAYING_TAXES = False
PAYING_FOUNDERS = True
PAYING_DELEGATORS = True


# ----------------------------------------------------------------------------------------------------------------------
# Настройки выплат
# ----------------------------------------------------------------------------------------------------------------------

# НАЛОГИ
TAXES = {
    'Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5': 0.1
}

# ОСНОВАТЕЛИ
FOUNDERS = {
    'Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5': 0.85,
    'Mx5cef09065d68561ad9f61a905c7d0aa230117733': 0.15
}

# ДЕЛЕГАТОРЫ
DELEGATORS_PERCENT = 0.1
DELEGATED_TOKEN = 'GORBUNOV'
MIN_COINS_DELEGATED = 1
STOP_LIST = ['Mx0f4e09ae5e998cf0322f1f13b36284274b5a3db5']


# ----------------------------------------------------------------------------------------------------------------------
# Настройки API
# ----------------------------------------------------------------------------------------------------------------------
class MinterAPIService(MinterAPI):
    request_headers = {
    'X-Project-Id': '014fd596-dc73-44f2-a8d8-03de263db60a',
    'X-Project-Secret': '5da1e427f1a9a1431dadcd3a772de3f6'
    }

    def _request(self, command, request_type='get', **kwargs):
        kwargs['headers'] = self.request_headers
        return super()._request(command, request_type=request_type, **kwargs)


# NODE_API_URL = 'http://api.minter.one'
NODE_API_URL = 'https://mnt.funfasy.dev/v0'
TIMEOUTS = {'read_timeout': 6, 'connect_timeout': 7}
# API = MinterAPI(NODE_API_URL, **TIMEOUTS)
API = MinterAPIService(NODE_API_URL, **TIMEOUTS)

# ----------------------------------------------------------------------------------------------------------------------
# Автонастройки кошелька
# ----------------------------------------------------------------------------------------------------------------------
with open('script/seed.txt', 'r') as f:
    SEED = f.read()
PRIVATE_KEY = MinterWallet.create(mnemonic=SEED)['private_key']
ADDRESS = MinterWallet.create(mnemonic=SEED)['address']

